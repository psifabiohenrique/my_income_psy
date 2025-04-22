from tkinter import messagebox  # Importa a messagebox

import pandas as pd

from src.models.database import get_session
from src.models.models import (  # Ajuste o caminho conforme necessário
    Appointment,
    Patient,
    WeekDays,
)
from src.utils import session_scope


class SpreadsheetIntegration:
    def __init__(self):
        self.db_session = get_session()

    def export_to_spreadsheet(self, file_path):
        # Consulta os dados dos pacientes e atendimentos
        with session_scope() as session:
            pacientes = session.query(Patient).all()
            atendimentos = session.query(Appointment).all()

            # Cria DataFrames
            pacientes_df = pd.DataFrame(
                [
                    {
                        "ID": paciente.id,
                        "Nome": paciente.name,
                        "Dia de Atendimento": paciente.attendance_day.value,
                        "Hora": paciente.time,
                        "Plano de Saúde": paciente.health_plan,
                        "Valor da Clínica": paciente.clinic_value,
                        "Percentual do Terapeuta": paciente.therapist_percentage,
                    }
                    for paciente in pacientes
                ]
            )

            atendimentos_df = pd.DataFrame(
                [
                    {
                        "ID": atendimento.id,
                        "Data": atendimento.date,
                        "ID do Paciente": atendimento.patient_id,
                        "Registro Feito": atendimento.record_done,
                        "Registro Lançado": atendimento.record_launched,
                    }
                    for atendimento in atendimentos
                ]
            )

            # Exporta para Excel
            with pd.ExcelWriter(
                file_path, engine="xlsxwriter"
            ) as writer:  # Usando o engine xlsxwriter
                pacientes_df.to_excel(
                    writer, sheet_name="Pacientes", index=False
                )
                atendimentos_df.to_excel(
                    writer, sheet_name="Atendimentos", index=False
                )

    def import_from_spreadsheet(self, file_path):
        # Lê os dados do Excel
        xls = pd.ExcelFile(file_path)
        with session_scope() as session:
            pacientes_df = pd.read_excel(xls, "Pacientes")
            atendimentos_df = pd.read_excel(xls, "Atendimentos")

            # Importa os dados para a base de dados
            for _, row in pacientes_df.iterrows():
                # Verifica se o paciente já existe
                existing_paciente = (
                    session.query(Patient)
                    .filter(Patient.id == row["ID"])
                    .first()
                )
                if existing_paciente:
                    # Exibe uma message box informando que a atualização não é permitida
                    messagebox.showwarning(
                        "ID Duplicado",
                        f"Paciente com ID {row['ID']} já existe. Atualização não permitida.",
                    )
                    continue  # Pula para o próximo paciente

                # Formata o dia da semana para corresponder à enumeração
                attendance_day_value = row["Dia de Atendimento"].strip()
                attendance_day = WeekDays.from_string(attendance_day_value)
                if attendance_day is None:
                    print(
                        f"Erro: '{attendance_day_value}' não é um dia da semana válido."
                    )
                    continue  # Pula para o próximo paciente se houver um erro

                paciente = Patient(
                    id=row["ID"],
                    name=row["Nome"],
                    attendance_day=attendance_day,
                    time=row["Hora"],
                    health_plan=row["Plano de Saúde"],
                    clinic_value=row["Valor da Clínica"],
                    therapist_percentage=row["Percentual do Terapeuta"],
                )
                session.add(paciente)

            for _, row in atendimentos_df.iterrows():
                # Verifica se o atendimento já existe
                existing_atendimento = (
                    session.query(Appointment)
                    .filter(Appointment.id == row["ID"])
                    .first()
                )
                if existing_atendimento:
                    # Exibe uma message box informando que a atualização não é permitida
                    messagebox.showwarning(
                        "ID Duplicado",
                        f"Atendimento com ID {row['ID']} já existe. Atualização não permitida.",
                    )
                    continue  # Pula para o próximo atendimento

                atendimento = Appointment(
                    id=row["ID"],
                    date=row["Data"],
                    patient_id=row["ID do Paciente"],
                    record_done=row["Registro Feito"],
                    record_launched=row["Registro Lançado"],
                )
                session.add(atendimento)

            session.commit()
