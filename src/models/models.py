import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class WeekDays(enum.Enum):
    MONDAY = "Segunda-feira"
    TUESDAY = "Terça-feira"
    WEDNESDAY = "Quarta-feira"
    THURSDAY = "Quinta-feira"
    FRIDAY = "Sexta-feira"
    SATURDAY = "Sábado"
    SUNDAY = "Domingo"

    @staticmethod
    def from_string(day_string):
        day_string = day_string.strip().lower()
        mapping = {
            "segunda-feira": WeekDays.MONDAY,
            "terca-feira": WeekDays.TUESDAY,
            "quarta-feira": WeekDays.WEDNESDAY,
            "quinta-feira": WeekDays.THURSDAY,
            "sexta-feira": WeekDays.FRIDAY,
            "sabado": WeekDays.SATURDAY,
            "domingo": WeekDays.SUNDAY,
        }
        return mapping.get(day_string, None)


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
