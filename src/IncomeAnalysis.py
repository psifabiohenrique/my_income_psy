from datetime import date
from .models.models import Appointment, Patient
from sqlalchemy import func
from .utils import session_scope


class IncomeAnalysis:
    def __init__(
        self,
        start_date: date,
        end_date: date,
        selected_patient: str = "All",
        selected_health_plan: str = "All",
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_patient = selected_patient
        self.selected_health_plan = selected_health_plan

    def calculate_statistics(self):
        """
        Calculates the statistics for the given date range and filters.

        Returns:
            A tuple containing:
            - total_attendances: The total number of attendances.
            - attendances_by_health_plan: A dictionary with the number of attendances for each health plan.
            - total_therapist_income: The total income for the therapist.
        """
        with session_scope() as session:
            if self.selected_patient != "All":
                patient = session.query(Patient).filter(Patient.name == self.selected_patient).first()
                if not patient:
                    return 0, {}, 0.0

                query = session.query(Appointment).filter(
                    Appointment.date >= self.start_date,
                    Appointment.date <= self.end_date,
                    Appointment.patient_id == patient.id
                )

                total_attendances = query.count()

                attendances_by_health_plan_dict = {patient.health_plan: total_attendances}

                total_therapist_income = (
                    session.query(
                        func.sum(
                            Patient.clinic_value * (Patient.therapist_percentage / 100)
                        )
                    )
                    .join(Appointment, Appointment.patient_id == Patient.id)
                    .filter(Appointment.patient_id == patient.id,
                            Appointment.date >= self.start_date,
                            Appointment.date <= self.end_date)
                    .scalar()
                )

                if total_therapist_income is None:
                    total_therapist_income = 0.0

            elif self.selected_health_plan != "All":
                query = session.query(Appointment).join(Patient).filter(
                    Appointment.date >= self.start_date,
                    Appointment.date <= self.end_date,
                    Patient.health_plan == self.selected_health_plan
                )

                total_attendances = query.count()

                attendances_by_health_plan = (
                    session.query(Patient.health_plan, func.count(Appointment.id))
                    .join(Appointment, Patient.id == Appointment.patient_id)
                    .filter(
                        Appointment.date >= self.start_date,
                        Appointment.date <= self.end_date,
                        Patient.health_plan == self.selected_health_plan
                    )
                    .group_by(Patient.health_plan)
                    .all()
                )

                attendances_by_health_plan_dict = {}
                for plan, count in attendances_by_health_plan:
                    attendances_by_health_plan_dict[plan] = count

                total_therapist_income = (
                    session.query(
                        func.sum(
                            Patient.clinic_value * (Patient.therapist_percentage / 100)
                        )
                    )
                    .join(Appointment, Patient.id == Appointment.patient_id)
                    .filter(
                        Appointment.date >= self.start_date,
                        Appointment.date <= self.end_date,
                        Patient.health_plan == self.selected_health_plan
                    )
                    .scalar()
                )

                if total_therapist_income is None:
                    total_therapist_income = 0.0
            else:
                query = session.query(Appointment).filter(
                    Appointment.date >= self.start_date,
                    Appointment.date <= self.end_date,
                )

                total_attendances = query.count()

                attendances_by_health_plan = (
                    session.query(Patient.health_plan, func.count(Appointment.id))
                    .join(Appointment, Patient.id == Appointment.patient_id)
                    .filter(
                        Appointment.date >= self.start_date,
                        Appointment.date <= self.end_date,
                    )
                    .group_by(Patient.health_plan)
                    .all()
                )

                attendances_by_health_plan_dict = {}
                for plan, count in attendances_by_health_plan:
                    attendances_by_health_plan_dict[plan] = count

                total_therapist_income = (
                    session.query(
                        func.sum(
                            Patient.clinic_value * (Patient.therapist_percentage / 100)
                        )
                    )
                    .join(Appointment, Patient.id == Appointment.patient_id)
                    .filter(
                        Appointment.date >= self.start_date,
                        Appointment.date <= self.end_date,
                    )
                    .scalar()
                )

                if total_therapist_income is None:
                    total_therapist_income = 0.0

            return (
                total_attendances,
                attendances_by_health_plan_dict,
                total_therapist_income,
            )