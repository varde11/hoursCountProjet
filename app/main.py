from schema import ContractOutput,WorkInput,SalaryEstimation,SalaryLine,ClientIn,EstimationOut,ClientOut,TokenOut,ClientLogin
from helpers import get_planned_hours,split_overtime_hours,get_special_rule,hash_password,verify_password
from logic import make_agent
from langchain_core.messages import HumanMessage

from fastapi import FastAPI,UploadFile,File,Form,Depends,HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional
from contextlib import asynccontextmanager


from db import get_db, sessionLocal,engine
from sqlalchemy.orm import Session
from sqlalchemy import exists
from table_structure import Base,Estimation,Client
from datetime import datetime,timedelta, timezone
from pydantic import ValidationError

import shutil
import os
from jose import jwt


agent = None

@asynccontextmanager
async def lifespan(app:FastAPI):

    global agent
    print("Préparation des ressources.....")
    if agent is None:
        agent = make_agent()

    Base.metadata.create_all(bind=engine)
    print("Préparation terminé")

    yield

    print("Fermeture de l'application, merci de l'avoir essayer ;)")



app = FastAPI(title="CountHoursAPI",lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("AUTHORIZED_URL1"),os.getenv("AUTHORIZED_URL2")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))



def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()

def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_client = payload.get("sub")
        if not id_client:
            raise HTTPException(status_code=401, detail="Token invalide")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")

    return client



@app.post("/login", response_model=TokenOut)
def login(client_data: ClientLogin, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id_client == client_data.id_client).first()

    if not client or not verify_password(client_data.password, client.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    token = create_access_token({"sub": client.id_client})

    return TokenOut(access_token=token)


@app.get("/healthy")
def get_healthy():
    return {"healthy":"Okayyy"}




def get_contract_info(
    contrat:UploadFile= File(...)
):
    final = None
    path_contrat = f"temp_{contrat.filename}"
    
    try:
        with open (path_contrat,"wb") as f :
            shutil.copyfileobj(contrat.file,f)
        
        events = agent.stream(
        {"messages": [HumanMessage(content=path_contrat)]},
            stream_mode="values"
        )

        for event in events:
            final = event["final_output"] if "final_output" in event and event["final_output"] else None
            txt = event["retrieved_text"] if "retrieved_text" in  event and event["retrieved_text"] else None
            comment = event["comment"] if "comment" in event and event["comment"] else None

        if final is None and comment:
            raise HTTPException(status_code=422,detail=comment)
    finally:
        os.remove(path_contrat)
        #print("Le fichier a bien été supprimé")
        #print("texte",txt)
    return final

    


def estimate_salary(contract: ContractOutput, work_input: WorkInput) -> SalaryEstimation:
    warnings = []

    if contract.base_hourly_rate is None:
        raise ValueError("Le taux horaire de base est manquant.")

    planned_hours = get_planned_hours(contract)
    

    if (contract.daily_hours is not None and contract.mission_days is not None and 
        (contract.base_hours is None or contract.base_hours.type != "hebdomadaire" or contract.base_hours.valeur is None)):
        warnings.append("Les heures planifiées ont été estimées à partir de la plage horaire journalière et du nombre de jours de mission.")
    
    actual_hours = max(planned_hours - work_input.break_hours -work_input.missing_hours + work_input.extra_hours, 0.0)

    base_rate = contract.base_hourly_rate

    normal_hours, overtime_25_hours, overtime_50_hours = split_overtime_hours(actual_hours)

    overtime_25_rate = base_rate * 1.25
    overtime_50_rate = base_rate * 1.50

    base_amount = normal_hours * base_rate
    overtime_25_amount = overtime_25_hours * overtime_25_rate
    overtime_50_amount = overtime_50_hours * overtime_50_rate

    special_amount = 0.0
    details = [
        SalaryLine(label="Heures normales", hours=normal_hours, rate=base_rate, amount=round(base_amount,2)),
    ]
    if work_input.night_hours > actual_hours:
        warnings.append("Les heures de nuit dépassent le total des heures réellement travaillées.")

    if work_input.sunday_hours > actual_hours:
        warnings.append("Les heures du dimanche dépassent le total des heures réellement travaillées.")

    if work_input.holiday_hours > actual_hours:
        warnings.append("Les heures fériées dépassent le total des heures réellement travaillées.")

    if work_input.break_hours > actual_hours:
        warnings.append("Les pauses renseignées sont trop élevées par rapport aux heures prévues.")

    if overtime_25_hours > 0:
        details.append(
            SalaryLine(
                label="Heures supplémentaires +25%",
                hours=overtime_25_hours,
                rate=overtime_25_rate,
                amount=round(overtime_25_amount,2)
            )
        )

    if overtime_50_hours > 0:
        details.append(
            SalaryLine(
                label="Heures supplémentaires +50%",
                hours=overtime_50_hours,
                rate=overtime_50_rate,
                amount=round(overtime_50_amount,2)
            )
        )



    night_rule = get_special_rule(contract, "night")
    if night_rule and work_input.night_hours > 0:
        if night_rule.type == "hourly_rate":
            amount = work_input.night_hours * night_rule.value
            details.append(
            SalaryLine(
                label="Heures de nuit (taux spécial complet)",
                hours=work_input.night_hours,
                rate=night_rule.value,
                amount=round(amount,2)
            )
        )

        elif night_rule.type == "hourly_bonus":
            amount = work_input.night_hours * night_rule.value
            details.append(
            SalaryLine(
                label="Majoration heures de nuit",
                hours=work_input.night_hours,
                rate=night_rule.value,
                amount=round(amount,2)
            )
        )

        elif night_rule.type == "percent":
            amount = work_input.night_hours * base_rate * (night_rule.value / 100)
            details.append(
            SalaryLine(
                label="Majoration heures de nuit (%)",
                hours=work_input.night_hours,
                rate=night_rule.value,
                amount=round(amount,2)
            )
        )

        else:
            amount = 0.0

        special_amount += amount
       


    sunday_rule = get_special_rule(contract, "sunday")
    if sunday_rule and work_input.sunday_hours > 0:
        if sunday_rule.type == "percent":
            amount = work_input.sunday_hours * base_rate * (sunday_rule.value / 100)
        elif sunday_rule.type == "hourly_rate":
            amount = work_input.sunday_hours * sunday_rule.value
        elif sunday_rule.type == "hourly_bonus":
            amount = work_input.sunday_hours * sunday_rule.value
        else:
            amount = 0.0

        special_amount += amount
        details.append(
            SalaryLine(
                label="Heures du dimanche",
                hours=work_input.sunday_hours,
                rate=sunday_rule.value,
                amount=round(amount,2)
            )
        )





    holiday_rule = get_special_rule(contract, "holiday")
    if holiday_rule and work_input.holiday_hours > 0:
        if holiday_rule.type == "percent":
            amount = work_input.holiday_hours * base_rate * (holiday_rule.value / 100)
        elif holiday_rule.type == "hourly_rate":
            amount = work_input.holiday_hours * holiday_rule.value
        elif holiday_rule.type == "hourly_bonus":
            amount = work_input.holiday_hours * holiday_rule.value
        else:
            amount = 0.0

        special_amount += amount
        details.append(
            SalaryLine(
                label="Heures fériées",
                hours=work_input.holiday_hours,
                rate=holiday_rule.value,
                amount=round(amount,2)
            )
        )

    total_estimated_salary = base_amount + overtime_25_amount + overtime_50_amount + special_amount

    if contract.base_hours and contract.base_hours.type == "mensuel":
        warnings.append("Le contrat semble mensuel : vérifie que les heures saisies correspondent bien à la bonne période.")

    if contract.commentaire:
        warnings.append(contract.commentaire)

    return SalaryEstimation(
        planned_hours=planned_hours,
        actual_hours=actual_hours,
        normal_hours=normal_hours,
        overtime_25_hours=overtime_25_hours,
        overtime_50_hours=overtime_50_hours,
        base_amount=round(base_amount,2),
        overtime_25_amount=round(overtime_25_amount,2),
        overtime_50_amount=round(overtime_50_amount,2),
        special_amount=round(special_amount,2),
        total_estimated_salary=round(total_estimated_salary,2),
        details=details,
        warnings=warnings,
    )




@app.get("/Me")
def get_client_by_id_client(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} n'existe pas.")
    return client

@app.get("/GetAllClient")
def get_all_client(db:Session=Depends(get_db)):
    clients = db.query(Client).all()
    if not clients:
        return []
    return clients



@app.post("/AddClient", response_model=ClientOut)
def add_client(client: ClientIn, db: Session = Depends(get_db)):
    if db.query(exists().where(Client.id_client == client.id_client)).scalar():
        raise HTTPException(
            status_code=422,
            detail=f"Il existe déjà un client avec l'id {client.id_client}"
        )

    new_client = Client(
        id_client=client.id_client,
        nom=client.nom,
        password_hash=hash_password(client.password),
        total_hours=0
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client


@app.get("/GetEstimationByIdEstimation/{id_estimation}",response_model=EstimationOut)
def get_estimation_by_id_estimation(id_estimation:int,db:Session=Depends(get_db)):
    estimation = db.query(Estimation).filter(Estimation.id_estimation==id_estimation).first()
    if not estimation:
        raise HTTPException (status_code=404,detail=f"Aucune estimation avec l'id {id_estimation} n'a été trouvée")
    
    return estimation


@app.get("/GetEstimationByIdClient",response_model=list[EstimationOut])
def get_estimation_by_id_client(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    
    if not db.query(exists().where(Client.id_client==current_client.id_client)).scalar():
        raise HTTPException(status_code=404, detail=f"Il n'existe aucun client avec l'identifiant {current_client.id_client}")

    estimation = db.query(Estimation).filter(Estimation.id_client==current_client.id_client).all()
    if not estimation:
        return []
    
    return estimation


@app.post("/EstimateSalary",response_model=EstimationOut)
def get_contrat_info(
    current_client:Client=Depends(get_current_client),
    db:Session=Depends(get_db),
    contrat_para: UploadFile = File(...),
    break_hours: float = Form(0.0),
    missing_hours: float = Form(0.0),
    extra_hours: float = Form(0.0),
    night_hours: float = Form(0.0),
    sunday_hours: float = Form(0.0),
    holiday_hours: float = Form(0.0),
    comment: Optional[str] = Form(None)
):
    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} n'existe pas.")


    contract = get_contract_info(contrat=contrat_para)
    work_para = WorkInput(
        missing_hours=missing_hours,
        break_hours = break_hours,
        extra_hours=extra_hours,
        night_hours=night_hours,
        sunday_hours=sunday_hours,
        holiday_hours=holiday_hours,
        comment=comment
    )
    #print(contract)
    estimation_raw = estimate_salary(contract=contract, work_input=work_para)

    try:
        SalaryEstimation.model_validate(estimation_raw)
    except ValidationError as ve:
        raise HTTPException(detail=f"Something went very wrong about the estimation: {ve}",status_code=500)
    
    estimation = Estimation(
        id_client = current_client.id_client,
        date_debut = datetime.strptime(contract.periode.debut,"%d/%m/%Y").date() if contract.periode.debut else None,
        date_fin = datetime.strptime(contract.periode.fin,"%d/%m/%Y").date() if contract.periode.fin else None,
        planned_hours = estimation_raw.planned_hours,
        actual_hours = estimation_raw.actual_hours,
        normal_hours = estimation_raw.normal_hours,
        overtime_25_hours = estimation_raw.overtime_25_hours,
        overtime_50_hours = estimation_raw.overtime_50_hours,
        base_amount = estimation_raw.base_amount,
        overtime_25_amount = estimation_raw.overtime_25_amount,
        overtime_50_amount = estimation_raw.overtime_50_amount,
        special_amount = estimation_raw.special_amount,
        total_estimated_salary = estimation_raw.total_estimated_salary,
        details = [detail.model_dump() for detail in estimation_raw.details],
        warnings = [warning for warning in estimation_raw.warnings],
        time_stamp = datetime.now().replace(microsecond=0)

    )
    db.add(estimation)
    client.total_hours = client.total_hours + estimation_raw.actual_hours
    db.commit()
    db.refresh(estimation)
    db.refresh(client)

    return estimation

    
del_description1 = "Supprimer une estimation retirera les heures apportées par cette estimation dans votre profil."
@app.delete("/DelEstimationByIdEstimation/{id_estimation}",response_model=EstimationOut,description=del_description1)
def del_estimation_by_idestimation(id_estimation:int,db:Session=Depends(get_db)):

    estimation = db.query(Estimation).filter(Estimation.id_estimation==id_estimation).first()
    if not estimation:
        raise HTTPException(status_code=404,detail=f"L'estimation d'identifiant {id_estimation} que vous essayez de supprimer n'existe pas.")
    
    try:
        deleted = EstimationOut.model_validate(estimation).model_dump()
    except ValidationError as ve:
        raise HTTPException (status_code=500,detail=f"Une erreur s'est produite: {ve}")
        

    client = db.query(Client).filter(Client.id_client==estimation.id_client).first()
    client.total_hours = client.total_hours - estimation.actual_hours
    db.query(Estimation).filter(Estimation.id_estimation==id_estimation).delete(synchronize_session=False)

    db.commit()
    db.refresh(client)

    return deleted


del_description2="Supprimer toutes les estimations remettra votre compteur d'heure à 0."
@app.delete("/DelEstimationByIdClient",response_model=list[EstimationOut],description=del_description2)
def del_estimation_by_idclient(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):

    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException (status_code=404,detail=f"Le client d'identifiant {current_client.id_client} est introuvable.")
    
    try:
        estimations = db.query(Estimation).filter(Estimation.id_client==current_client.id_client).all()
        if not estimations :
            return []
        
        deleted = [EstimationOut.model_validate(e).model_dump() for e in estimations]
    except ValidationError as ve:
        raise HTTPException(status_code=500,detail= f"Quelque chose s'est mal passé: {ve}")
    
    client.total_hours = 0
    db.query(Estimation).filter(Estimation.id_client==current_client.id_client).delete(synchronize_session=False)
    
    db.commit()
    db.refresh(client)

    return deleted