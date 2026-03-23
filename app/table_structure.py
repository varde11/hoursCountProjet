from sqlalchemy import Column,Integer,DateTime,String,Float,ForeignKey,Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = "client"

    id_client = Column (String,primary_key=True,nullable=False)
    nom = Column(String,nullable=False)
    total_hours = Column(Float,default=0,nullable=False)
    password_hash = Column(String, nullable=False)


class Estimation(Base):
    __tablename__ = "estimation"

    id_estimation = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_client = Column(String, ForeignKey("client.id_client"), nullable=False)

    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)

    planned_hours = Column(Float)
    actual_hours = Column(Float)
    normal_hours = Column(Float)
    overtime_25_hours = Column(Float)
    overtime_50_hours = Column(Float)

    base_amount = Column(Float)
    overtime_25_amount = Column(Float)
    overtime_50_amount = Column(Float)
    special_amount = Column(Float)
    total_estimated_salary = Column(Float)

    details = Column(JSON)
    warnings = Column(JSON)

    time_stamp = Column(DateTime, nullable=False)