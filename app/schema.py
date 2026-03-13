from pydantic import BaseModel, Field
from typing import Optional, Literal, Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from datetime import datetime, date

class Periode(BaseModel):
    debut: Optional[str] = None
    fin: Optional[str] = None

class BaseHours(BaseModel):
    type: Literal["hebdomadaire", "mensuel", "mission", "inconnu"] = "inconnu"
    valeur: Optional[float] = None

class SpecialRateRule(BaseModel):
    label: Literal["night", "sunday", "holiday", "overtime_25", "overtime_50"]
    type: Literal["percent", "hourly_rate", "hourly_bonus"]
    value: float
    condition: Optional[str] = None

class ContractOutput(BaseModel):
    periode: Periode
    base_hours: Optional[BaseHours] = None
    base_hourly_rate: Optional[float] = None
    base_salary_reference: Optional[float] = None
    daily_hours: Optional[float] = None
    mission_days: Optional[int] = None
    special_rate_rules: List[SpecialRateRule] = Field(default_factory=list)
    commentaire: Optional[str] = None


class WorkInput(BaseModel):
    missing_hours: float = Field(0.0, ge=0, description="Heures prévues mais non travaillées")
    extra_hours: float = Field(0.0, ge=0, description="Heures travaillées en plus du volume prévu")

    night_hours: float = Field(0.0, ge=0, description="Nombre d'heures de nuit réellement effectuées")
    sunday_hours: float = Field(0.0, ge=0, description="Nombre d'heures effectuées le dimanche")
    holiday_hours: float = Field(0.0, ge=0, description="Nombre d'heures effectuées un jour férié")
    break_hours: float = Field(0.0, ge=0, description="Total des heures de pause non travaillées sur la période")
    comment: Optional[str] = None


class SalaryLine(BaseModel):
    label: str
    hours: Optional[float] = None
    rate: Optional[float] = None
    amount: float

class SalaryEstimation(BaseModel):
    planned_hours: float
    actual_hours: float

    normal_hours: float
    overtime_25_hours: float
    overtime_50_hours: float

    base_amount: float
    overtime_25_amount: float
    overtime_50_amount: float
    special_amount: float

    total_estimated_salary: float

    details: list[SalaryLine] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    retrieved_text: str
    trust : bool 
    comment : Optional[str]=None
    final_output: dict



# class ClientIn(BaseModel):
#     id_client: str = Field(..., min_length=3, max_length=20, description="Identifiant unique du client")
#     nom: str


class EstimationOut(BaseModel):
    id_estimation : int = Field(ge=1)
    id_client: str =  Field(...,min_length=3,max_length=20)
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    planned_hours: float
    actual_hours: float
    normal_hours: float
    overtime_25_hours: float
    overtime_50_hours: float
    base_amount: float
    overtime_25_amount: float
    overtime_50_amount: float
    special_amount: float
    total_estimated_salary: float
    details: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    time_stamp: datetime
    model_config = {"from_attributes":True}


class ClientIn(BaseModel):
    id_client: str = Field(..., min_length=3, max_length=20)
    nom: str = Field(...,min_length=2,max_length=50)
    password: str = Field(...,min_length=4,max_length=10)

class ClientLogin(BaseModel):
    id_client: str = Field(..., min_length=3, max_length=20)
    password: str = Field(...,min_length=4,max_length=10)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClientOut(BaseModel):
    id_client: str
    nom: str
    total_hours: float

    model_config = {"from_attributes": True}