import tkinter as tk
from tkinter import messagebox, ttk

from src.models.models import Patient
from src.utils import session_scope


class PatientListView(tk.Frame):
    def __init__(self, master, show_view_callback):
        super().__init__(master)
        self.show_view = show_view_callback
        self.patient_buttons = []

        tk.Label(self, text="Patient List", font=("Arial", 16)).pack(pady=10)

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Create patient button
        create_patient_button = tk.Button(
            button_frame,
            text="Create patient",
            command=lambda: self.show_view("patient_form"),
        )
        create_patient_button.pack(side=tk.LEFT, padx=5)

        # Create Session button
        create_session_button = tk.Button(
            button_frame,
            text="Create Session",
            command=lambda: self.show_view("session_form"),
        )
        create_session_button.pack(side=tk.LEFT, padx=5)

        # Go to Statistics button
        statistics_button = tk.Button(
            button_frame,
            text="Go to Statistics",
            command=lambda: self.show_view("statistics"),
        )
        statistics_button.pack(side=tk.LEFT, padx=5)

        # Spreadsheet Integradion button
        spreadsheet_integration = ttk.Button(
            button_frame,
            text="Spreadsheet Integration",
            command=lambda: self.show_view("spreedsheet_integration"),
        )
        spreadsheet_integration.pack(side=tk.LEFT, padx=5)

        # Separator
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", padx=5, pady=5)

        self.update_patient_list()

    def update_patient_list(self):
        # Destroy existing buttons to prevent accumulation
        for button in self.patient_buttons:
            button.destroy()
        self.patient_buttons = []

        with session_scope() as session:
            patients = session.query(Patient).all()
            for patient in patients:
                patient_frame = tk.Frame(self)
                patient_frame.pack(pady=5)

                # Acesse o valor da enumeração para exibir o dia de atendimento
                attendance_day_value = (
                    patient.attendance_day.value
                    if patient.attendance_day
                    else "Não definido"
                )
                patient_info = f"{patient.name} - Dia: {attendance_day_value} - Plano: {patient.health_plan or 'Nenhum'}"
                tk.Label(patient_frame, text=patient_info).pack(
                    side=tk.LEFT, padx=5
                )

                edit_button = tk.Button(
                    patient_frame,
                    text="Edit",
                    command=lambda id=patient.id: self.edit_patient_form(id),
                )
                edit_button.pack(side=tk.LEFT, padx=5)
                self.patient_buttons.append(edit_button)

                delete_button = tk.Button(
                    patient_frame,
                    text="Delete",
                    command=lambda id=patient.id: self.delete_patient_wrapper(
                        id
                    ),
                )
                delete_button.pack(side=tk.LEFT, padx=5)
                self.patient_buttons.append(delete_button)

    def edit_patient_form(self, patient_id):
        self.show_view("patient_form", patient_id=patient_id)

    def delete_patient_wrapper(self, patient_id):
        if messagebox.askyesno(
            "Delete Patient", "Are you sure you want to delete this patient?"
        ):
            self.delete_patient(patient_id)
            self.update_patient_list()

    def delete_patient(self, patient_id):
        with session_scope() as session:
            patient = (
                session.query(Patient).filter(Patient.id == patient_id).first()
            )
            if patient:
                session.delete(patient)
