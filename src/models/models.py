import enum
from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WeekDays(enum.Enum):
    MONDAY = "Segunda-feira"
    TUESDAY = "Terça-feira"
    WEDNESDAY = "Quarta-feira"
    THURSDAY = "Quinta-feira"
    FRIDAY = "Sexta-feira"
    SATURDAY = "Sábado"
    SUNDAY = "Domingo"


class Patient(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    attendance_day = Column(Enum(WeekDays))
    time = Column(String)
    health_plan = Column(String, nullable=True)
    clinic_value = Column(Float)
    therapist_percentage = Column(Float)

    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "atendimentos"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    patient_id = Column(Integer, ForeignKey("pacientes.id"))
    record_done = Column(Boolean, default=False)
    record_launched = Column(Boolean, default=False)

    patient = relationship("Patient", back_populates="appointments")
