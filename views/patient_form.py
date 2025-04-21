import tkinter as tk
from tkinter import messagebox
from src.models.models import Patient, WeekDays
from tkinter import ttk
from src.utils import session_scope

class PatientFormView(tk.Frame):
    def __init__(self, master, show_view_callback, patient_id=None):
        super().__init__(master)
        self.show_view = show_view_callback
        self.patient_id = patient_id  # Store patient_id
        self.patient = None  # Store patient data
        tk.Label(self, text="Patient Form", font=("Arial", 16)).pack(pady=10)
        tk.Button(
            self, text="Back to List", command=lambda: self.show_view("patient_list")
        ).pack(pady=20)
        # Form fields
        self.form_frame = tk.Frame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")

        # Name field
        tk.Label(self.form_frame, text="Nome:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self.form_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Day of attendance field
        tk.Label(self.form_frame, text="Dia de Atendimento:").grid(
            row=1, column=0, sticky="w"
        )
        self.day_combo = ttk.Combobox(self.form_frame, values=[d.value for d in WeekDays])
        self.day_combo.grid(row=1, column=1, sticky="ew", pady=5)

        # Time field
        tk.Label(self.form_frame, text="Horário:").grid(row=2, column=0, sticky="w")
        self.time_entry = tk.Entry(self.form_frame)
        self.time_entry.grid(row=2, column=1, sticky="ew", pady=5)

        # Health plan field
        tk.Label(self.form_frame, text="Plano de Saúde:").grid(
            row=3, column=0, sticky="w"
        )
        self.health_plan_entry = tk.Entry(self.form_frame)
        self.health_plan_entry.grid(row=3, column=1, sticky="ew", pady=5)

        # Clinic value field
        tk.Label(self.form_frame, text="Valor Clínica:").grid(
            row=4, column=0, sticky="w"
        )
        self.clinic_value_entry = tk.Entry(self.form_frame)
        self.clinic_value_entry.grid(row=4, column=1, sticky="ew", pady=5)
        self.clinic_value_entry.bind("<FocusOut>", self.calculate_therapist_value)

        # Therapist percentage field
        tk.Label(self.form_frame, text="Porcentagem Terapeuta:").grid(
            row=5, column=0, sticky="w"
        )
        self.therapist_percentage_entry = tk.Entry(self.form_frame)
        self.therapist_percentage_entry.grid(row=5, column=1, sticky="ew", pady=5)
        self.therapist_percentage_entry.bind("<FocusOut>", self.calculate_therapist_value)

        # Therapist value field (READONLY)
        tk.Label(self.form_frame, text="Valor Terapeuta:").grid(
            row=6, column=0, sticky="w"
        )
        self.therapist_value_entry = tk.Entry(self.form_frame, state="readonly")
        self.therapist_value_entry.grid(row=6, column=1, sticky="ew", pady=5)

        # Buttons frame
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        # Save button
        tk.Button(self.button_frame, text="Salvar", command=self.save_patient).pack(
            side="left", padx=5
        )

        # Clear button
        tk.Button(self.button_frame, text="Limpar", command=self.clear_form).pack(
            side="left", padx=5
        )

        if self.patient_id:
            self.load_patient_data()

    def load_patient_data(self):
        """Load patient data from database and populate the form"""
        with session_scope() as session:
            self.patient = session.query(Patient).filter(Patient.id == self.patient_id).first()
            if self.patient:
                self.name_entry.insert(0, self.patient.name)
                self.day_combo.set(self.patient.attendance_day.value)
                self.time_entry.insert(0, self.patient.time)
                self.health_plan_entry.insert(0, self.patient.health_plan)
                self.clinic_value_entry.insert(0, str(self.patient.clinic_value))
                self.therapist_percentage_entry.insert(0, str(self.patient.therapist_percentage))
                self.calculate_therapist_value()

    def save_patient(self):
        """Save patient data from form fields"""
        name = self.name_entry.get()
        attendance_day = self.day_combo.get()
        time = self.time_entry.get()
        health_plan = self.health_plan_entry.get()
        clinic_value = self.clinic_value_entry.get()
        therapist_percentage = self.therapist_percentage_entry.get()

        # Standardize health plan to uppercase
        health_plan = health_plan.upper()

        try:
            clinic_value = float(clinic_value.replace(",", ".")) if clinic_value else 0.0
            therapist_percentage = float(therapist_percentage.replace(",", ".")) if therapist_percentage else 0.0
        except ValueError:
            messagebox.showerror("Error", "Invalid number format. Use numbers with '.' or ',' as decimal separators.")
            return

        with session_scope() as session:
            if self.patient_id:  # Editing existing patient
                patient = session.query(Patient).filter(Patient.id == self.patient_id).first()
                if patient:
                    patient.name = name
                    patient.attendance_day = WeekDays(attendance_day)
                    patient.time = time
                    patient.health_plan = health_plan
                    patient.clinic_value = clinic_value
                    patient.therapist_percentage = therapist_percentage
                    session.commit()
                    messagebox.showinfo("Success", "Patient updated successfully!")
                else:
                     messagebox.showerror("Error", "Patient not found!")
            else:  # Creating a new patient
                new_patient = Patient(
                    name=name,
                    attendance_day=WeekDays(attendance_day),
                    time=time,
                    health_plan=health_plan,
                    clinic_value=clinic_value,
                    therapist_percentage=therapist_percentage
                )
                session.add(new_patient)
                session.commit()
                messagebox.showinfo("Success", "Patient created successfully!")

        self.show_view("patient_list")

    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.day_combo.set('')
        self.time_entry.delete(0, tk.END)
        self.health_plan_entry.delete(0, tk.END)
        self.clinic_value_entry.delete(0, tk.END)
        self.therapist_percentage_entry.delete(0, tk.END)
        self.therapist_value_entry.config(state=tk.NORMAL)
        self.therapist_value_entry.delete(0, tk.END)
        self.therapist_value_entry.config(state="readonly")

    def calculate_therapist_value(self, event=None):
        """Calculate and display the therapist value"""
        try:
            clinic_value = float(self.clinic_value_entry.get().replace(",", ".")) if self.clinic_value_entry.get() else 0.0
            therapist_percentage = float(self.therapist_percentage_entry.get().replace(",", ".")) if self.therapist_percentage_entry.get() else 0.0
            therapist_value = clinic_value * (therapist_percentage / 100)
            self.therapist_value_entry.config(state=tk.NORMAL)
            self.therapist_value_entry.delete(0, tk.END)
            self.therapist_value_entry.insert(0, f"{therapist_value:.2f}")
            self.therapist_value_entry.config(state="readonly")
        except ValueError:
            self.therapist_value_entry.config(state=tk.NORMAL)
            self.therapist_value_entry.delete(0, tk.END)
            self.therapist_value_entry.config(state="readonly")
            messagebox.showerror("Error", "Invalid number format in Clinic Value or Therapist Percentage.")
