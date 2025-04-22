import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date
from src.IncomeAnalysis import IncomeAnalysis
from src.models.models import Patient
from src.utils import session_scope


class StatisticsView(tk.Frame):
    def __init__(self, master, show_view_callback):
        super().__init__(master)
        self.show_view = show_view_callback

        tk.Label(self, text="Statistics", font=("Arial", 16)).pack(pady=10)
        tk.Button(
            self,
            text="Back to List",
            command=lambda: self.show_view("patient_list"),
        ).pack(pady=20)

        # Filter frame
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=10)

        # Patient filter
        tk.Label(filter_frame, text="Patient:").grid(row=0, column=0, padx=5)
        self.patient_combo = ttk.Combobox(
            filter_frame, values=["All"] + self.get_patient_names()
        )
        self.patient_combo.grid(row=0, column=1, padx=5)
        self.patient_combo.set("All")  # Default to all patients

        # Health plan filter
        tk.Label(filter_frame, text="Health Plan:").grid(row=0, column=2, padx=5)
        self.health_plan_combo = ttk.Combobox(
            filter_frame, values=["All"] + self.get_health_plans()
        )
        self.health_plan_combo.grid(row=0, column=3, padx=5)
        self.health_plan_combo.set("All")  # Default to all health plans

        # Date selection frame
        date_frame = tk.Frame(self)
        date_frame.pack(pady=10)

        # Calculate default dates
        today = date.today()
        first_day_of_month = today.replace(day=1)

        # Start date
        tk.Label(date_frame, text="Start Date:").grid(
            row=0, column=0, padx=5
        )
        self.start_date_entry = DateEntry(
            date_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd-mm-yyyy",
            year=first_day_of_month.year,
            month=first_day_of_month.month,
            day=first_day_of_month.day,
        )
        self.start_date_entry.grid(row=0, column=1, padx=5)

        # End date
        tk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=5)
        self.end_date_entry = DateEntry(
            date_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd-mm-yyyy",
            year=today.year,
            month=today.month,
            day=today.day,
        )
        self.end_date_entry.grid(row=0, column=3, padx=5)

        # Analyze button
        analyze_button = tk.Button(
            self, text="Analyze", command=self.analyze_data
        )
        analyze_button.pack(pady=10)

        # Results frame
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(pady=10)

        # Total attendances label
        tk.Label(self.results_frame, text="Total Attendances:").grid(
            row=0, column=0, sticky="w"
        )
        self.total_attendances_label = tk.Label(self.results_frame, text="0")
        self.total_attendances_label.grid(row=0, column=1, sticky="w")

        # Attendances by health plan label
        tk.Label(self.results_frame, text="Attendances by Health Plan:").grid(
            row=1, column=0, sticky="w"
        )
        self.attendances_by_health_plan_label = tk.Label(
            self.results_frame, text="None"
        )
        self.attendances_by_health_plan_label.grid(row=1, column=1, sticky="w")

        # Total money received label
        tk.Label(
            self.results_frame,
            text="Total Money Received:",
            font=("Arial", 12, "bold"),
        ).grid(row=2, column=0, sticky="w")
        self.total_money_received_label = tk.Label(
            self.results_frame, text="R$ 0.00", font=("Arial", 12, "bold")
        )
        self.total_money_received_label.grid(row=2, column=1, sticky="w")

        self.analyze_data()

    def get_patient_names(self):
        """Fetch patient names from the database"""
        with session_scope() as session:
            patients = session.query(Patient).all()
            return [patient.name for patient in patients]

    def get_health_plans(self):
        """Fetch unique health plans from the database"""
        with session_scope() as session:
            health_plans = (
                session.query(Patient.health_plan).distinct().all()
            )  # Fetch unique health plans
            return [
                plan[0] for plan in health_plans if plan[0]
            ]  # Extract health plan names

    def analyze_data(self):
        """Analyzes the data and updates the results labels"""
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        selected_patient = self.patient_combo.get()
        selected_health_plan = self.health_plan_combo.get()

        analysis = IncomeAnalysis(
            start_date, end_date, selected_patient, selected_health_plan
        )
        total_attendances, attendances_by_health_plan, total_therapist_income = (
            analysis.calculate_statistics()
        )

        # Format attendances by health plan
        attendances_by_health_plan_str = ", ".join(
            [
                f"{plan}: {count}"
                for plan, count in attendances_by_health_plan.items()
            ]
        )
        if not attendances_by_health_plan_str:
            attendances_by_health_plan_str = "None"

        self.update_results(
            total_attendances,
            attendances_by_health_plan_str,
            total_therapist_income,
        )

    def update_results(
        self, total_attendances, attendances_by_health_plan, total_money_received
    ):
        """Update the results labels with the analyzed data"""
        self.total_attendances_label.config(text=str(total_attendances))
        self.attendances_by_health_plan_label.config(
            text=attendances_by_health_plan
        )
        self.total_money_received_label.config(
            text=f"R$ {total_money_received:.2f}"
        )
