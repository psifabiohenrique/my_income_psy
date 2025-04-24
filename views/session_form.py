import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from tkcalendar import DateEntry

from src.models.models import Appointment, Patient
from src.utils import session_scope


class SessionFormView(ttk.Frame):
    def __init__(self, master, show_view_callback):
        super().__init__(master)
        self.show_view = show_view_callback
        self.selected_appointment_id = None

        # Title label
        title_label = ttk.Label(self, text="Session Form", font=("Arial", 16))
        # Center align all widgets
        title_label.pack(pady=10, anchor="center")

        # Back button
        back_button = ttk.Button(
            self, text="Back to List", command=lambda: self.show_view("patient_list")
        )
        back_button.pack(pady=20, anchor="center")

        # Form fields frame
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(pady=10, padx=20, anchor="center")

        # Patient selection
        ttk.Label(self.form_frame, text="Patient:").grid(row=0, column=0, sticky="w")
        self.setup_patient_combobox()
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=5)

        # Session date
        ttk.Label(self.form_frame, text="Session Date:").grid(
            row=1, column=0, sticky="w"
        )
        self.date_entry = DateEntry(
            self.form_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd-mm-yyyy",
        )
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Record done checkbox
        self.record_done_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.form_frame, text="Record Done", variable=self.record_done_var
        ).grid(row=2, column=0, columnspan=2, pady=5)

        # Record launched checkbox
        self.record_launched_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.form_frame, text="Record Launched", variable=self.record_launched_var
        ).grid(row=3, column=0, columnspan=2, pady=5)

        # Buttons frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10, anchor="center")

        # Save button
        self.save_button = ttk.Button(
            self.button_frame, text="Save", command=self.save_session
        )
        self.save_button.pack(side="left", padx=5)

        # Delete button
        self.delete_button = ttk.Button(
            self.button_frame, text="Delete", command=self.delete_session
        )
        self.delete_button.pack(side="left", padx=5)
        self.delete_button.state(["disabled"])  # Initially disabled

        # Latest sessions label
        ttk.Label(self, text="Latest Sessions", font=("Arial", 14)).pack(
            pady=10, anchor="center"
        )

        # Filters frame
        self.filters_frame = ttk.Frame(self)
        self.filters_frame.pack(pady=10, padx=20, fill="x", anchor="center")

        # Record done filter
        self.filter_record_done_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.filters_frame, text="Record Done", variable=self.filter_record_done_var
        ).grid(row=0, column=0, padx=5, sticky="w")

        # Record launched filter
        self.filter_record_launched_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.filters_frame,
            text="Record Launched",
            variable=self.filter_record_launched_var,
        ).grid(row=0, column=1, padx=5, sticky="w")

        # Apply filters button
        apply_filters_button = ttk.Button(
            self.filters_frame, text="Apply Filters", command=self.apply_filters
        )
        apply_filters_button.grid(row=0, column=4, padx=5, sticky="w")

        # Clear filters button
        clear_filters_button = ttk.Button(
            self.filters_frame, text="Clear Filters", command=self.clear_filters
        )
        clear_filters_button.grid(row=0, column=5, padx=5, sticky="w")

        # Date range filters
        ttk.Label(self.filters_frame, text="Start Date:").grid(
            row=1, column=0, sticky="w"
        )
        self.filter_start_date_entry = DateEntry(
            self.filters_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd-mm-yyyy",
        )
        self.filter_start_date_entry.set_date(
            datetime(datetime.now().year, datetime.now().month, 1)
        )
        self.filter_start_date_entry.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Label(self.filters_frame, text="End Date:").grid(
            row=1, column=2, sticky="w"
        )
        self.filter_end_date_entry = DateEntry(
            self.filters_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd-mm-yyyy",
        )
        self.filter_end_date_entry.set_date(datetime.now())
        self.filter_end_date_entry.grid(row=1, column=3, padx=5, sticky="w")

        self.filter_applied = False

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, anchor="center")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, anchor="center")

        self.clear_filters()

        self.update_sessions_list()

    def get_patient_names(self):
        """Fetch patient names from the database ordered alphabetically"""
        with session_scope() as session:
            patients = session.query(Patient).order_by(Patient.name).all()
            return [patient.name for patient in patients]

    def setup_patient_combobox(self):
        """Configure patient combobox with autocomplete feature"""
        self.patient_combo = ttk.Combobox(
            self.form_frame, values=self.get_patient_names()
        )
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=5)

        def on_type(event):
            """Filter combobox values based on user input"""
            value = event.widget.get().lower()
            all_patients = self.get_patient_names()

            if value:
                filtered_patients = [
                    patient for patient in all_patients if value in patient.lower()
                ]
                self.patient_combo["values"] = filtered_patients
            else:
                self.patient_combo["values"] = all_patients

            # Show dropdown list
            self.patient_combo.event_generate("<Down>")

        # Bind to both KeyRelease and KeyPress to ensure dropdown stays open
        self.patient_combo.bind("<KeyRelease>", on_type)

    def save_session(self):
        """Save the session data to the database"""
        patient_name = self.patient_combo.get()
        session_date_str = self.date_entry.get()
        record_done = self.record_done_var.get()
        record_launched = self.record_launched_var.get()

        # Replace "/" with "-" to handle both date formats
        session_date_str = session_date_str.replace("/", "-")

        try:
            session_date = datetime.strptime(session_date_str, "%d-%m-%Y").date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use dd-mm-yyyy.")
            return

        if not patient_name:
            messagebox.showerror("Error", "Select a patient.")
            return

        with session_scope() as session:
            patient = (
                session.query(Patient).filter(Patient.name == patient_name).first()
            )
            if patient:
                if self.selected_appointment_id:
                    # Editing existing session
                    appointment_to_update = (
                        session.query(Appointment)
                        .filter(Appointment.id == self.selected_appointment_id)
                        .first()
                    )
                    if appointment_to_update:
                        appointment_to_update.date = session_date
                        appointment_to_update.patient_id = patient.id
                        appointment_to_update.record_done = record_done
                        appointment_to_update.record_launched = record_launched
                        messagebox.showinfo("Success", "Session updated successfully!")
                    else:
                        messagebox.showerror("Error", "Session not found.")
                else:
                    # Creating new session
                    new_appointment = Appointment(
                        date=session_date,
                        patient_id=patient.id,
                        record_done=record_done,
                        record_launched=record_launched,
                    )
                    session.add(new_appointment)
                    messagebox.showinfo("Success", "Session saved successfully!")
            else:
                messagebox.showerror("Error", "Patient not found.")

        self.update_sessions_list()
        self.clear_form()

    def delete_session(self):
        """Delete the selected session from the database"""
        if not self.selected_appointment_id:
            messagebox.showerror("Error", "Select a session to delete.")
            return

        if messagebox.askyesno(
            "Confirm Deletion", "Are you sure you want to delete this session?"
        ):
            with session_scope() as session:
                appointment_to_delete = (
                    session.query(Appointment)
                    .filter(Appointment.id == self.selected_appointment_id)
                    .first()
                )
                if appointment_to_delete:
                    session.delete(appointment_to_delete)
                    messagebox.showinfo("Success", "Session deleted successfully!")
                    self.update_sessions_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "Session not found.")
        self.update_sessions_list()  # update session list after delete

    def load_session_for_editing(self, session_id):
        """Load the selected session's data into the form for editing"""
        with session_scope() as session:
            appointment_to_load = (
                session.query(Appointment).filter(Appointment.id == session_id).first()
            )

            if appointment_to_load:
                self.selected_appointment_id = appointment_to_load.id
                self.patient_combo.set(
                    appointment_to_load.patient.name
                    if appointment_to_load.patient
                    else ""
                )
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, appointment_to_load.date.strftime("%d-%m-%Y"))
                self.record_done_var.set(appointment_to_load.record_done)
                self.record_launched_var.set(appointment_to_load.record_launched)
                self.delete_button.config(state=tk.NORMAL)  # Enable delete button
                self.save_button.config(text="Update")  # Change button text to "Update"
            else:
                messagebox.showerror("Error", "Session not found.")

    def update_sessions_list(self):
        """Update the list of latest sessions"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        with session_scope() as session:
            query = session.query(Appointment)

            if self.filter_applied:
                if self.filter_record_done_var.get():
                    query = query.filter(Appointment.record_done)
                if self.filter_record_launched_var.get():
                    query = query.filter(Appointment.record_launched)

                start_date = self.filter_start_date_entry.get()
                end_date = self.filter_end_date_entry.get()
                if start_date and end_date:
                    try:
                        start_date = datetime.strptime(start_date, "%d-%m-%Y").date()
                        end_date = datetime.strptime(end_date, "%d-%m-%Y").date()
                        query = query.filter(
                            Appointment.date.between(start_date, end_date)
                        )
                    except ValueError:
                        messagebox.showerror(
                            "Error", "Invalid date format. Use dd-mm-yyyy."
                        )
                        return

            appointments = query.order_by(Appointment.date.desc()).limit(15).all()

            style = ttk.Style()
            style.configure("Red.TLabel", background="red")
            style.configure("Orange.TLabel", background="orange")
            style.configure("Green.TLabel", background="green")

            for appointment in appointments:
                patient_name = (
                    appointment.patient.name if appointment.patient else "N/A"
                )
                session_info = f"{appointment.date.strftime('%d-%m-%Y')} - {patient_name} - Done: {appointment.record_done} - Launched: {appointment.record_launched}"

                # Create the label with appropriate style
                style_name = "TLabel"
                if not appointment.record_done:
                    style_name = "Red.TLabel"
                elif not appointment.record_launched:
                    style_name = "Orange.TLabel"
                else:
                    style_name = "Green.TLabel"

                label = ttk.Label(
                    self.scrollable_frame, text=session_info, style=style_name, anchor="center"
                )

                label.bind(
                    "<Button-1>",
                    lambda e,
                    appointment_id=appointment.id: self.load_session_for_editing(
                        appointment_id
                    ),
                )

                label.pack(pady=5, padx=150, anchor="center")

    def clear_form(self):
        """Clear the form fields and reset to default state"""
        self.selected_appointment_id = None
        self.patient_combo.set("")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.record_done_var.set(False)
        self.record_launched_var.set(False)
        self.delete_button.config(state=tk.DISABLED)
        self.save_button.config(text="Save")

    def clear_filters(self):
        """Clear all filters and reset the session list to show the latest appointments."""
        self.filter_applied = False
        self.update_sessions_list()

    def apply_filters(self):
        self.filter_applied = True
        self.update_sessions_list()
