import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
from src.models.models import Appointment, Patient
from src.utils import session_scope

class SessionFormView(tk.Frame):
    def __init__(self, master, show_view_callback):
        super().__init__(master)
        self.show_view = show_view_callback
        self.selected_session_id = None  # To store the ID of the selected session

        tk.Label(self, text="Session Form", font=("Arial", 16)).pack(pady=10, anchor="center")
        tk.Button(self, text="Back to List", command=lambda: self.show_view("patient_list")).pack(pady=20, anchor="center")

        # Form fields frame
        self.form_frame = tk.Frame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")

        # Patient selection
        tk.Label(self.form_frame, text="Paciente:").grid(row=0, column=0, sticky="w")
        self.patient_combo = ttk.Combobox(self.form_frame, values=self.get_patient_names())
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=5)

        # Session date
        tk.Label(self.form_frame, text="Data da Sessão:").grid(row=1, column=0, sticky="w")
        self.date_entry = DateEntry(self.form_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='dd-mm-yyyy')
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Prontuario feito checkbox
        self.record_done_var = tk.BooleanVar()
        tk.Checkbutton(self.form_frame, text="Prontuário Feito", variable=self.record_done_var).grid(row=2, column=0, columnspan=2, pady=5)

        # Prontuario lançado checkbox
        self.record_launched_var = tk.BooleanVar()
        tk.Checkbutton(self.form_frame, text="Prontuário Lançado", variable=self.record_launched_var).grid(row=3, column=0, columnspan=2, pady=5)

        # Buttons frame
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10, anchor="center")

        # Save button
        self.save_button = tk.Button(self.button_frame, text="Salvar", command=self.save_session)
        self.save_button.pack(side="left", padx=5)

        # Delete button
        self.delete_button = tk.Button(self.button_frame, text="Excluir", command=self.delete_session)
        self.delete_button.pack(side="left", padx=5)
        self.delete_button.config(state=tk.DISABLED)  # Initially disabled

        # Latest sessions label
        tk.Label(self, text="Últimos Atendimentos", font=("Arial", 14)).pack(pady=10, anchor="center")
        self.sessions_listbox = tk.Listbox(self, width=50, height=10)
        self.sessions_listbox.pack(pady=10, anchor="center")
        self.sessions_listbox.bind("<Double-Button-1>", self.load_session_for_editing)  # Bind double click event

        self.update_sessions_list()

    def get_patient_names(self):
        """Fetch patient names from the database"""
        with session_scope() as session:
            patients = session.query(Patient).all()
            return [patient.name for patient in patients]

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
            messagebox.showerror("Erro", "Formato de data inválido. Use dd-mm-yyyy.")
            return

        if not patient_name:
            messagebox.showerror("Erro", "Selecione um paciente.")
            return

        with session_scope() as session:
            patient = session.query(Patient).filter(Patient.name == patient_name).first()
            if patient:
                if self.selected_session_id:
                    # Editing existing session
                    session_to_update = session.query(Appointment).filter(Appointment.id == self.selected_session_id).first()
                    if session_to_update:
                        session_to_update.date = session_date
                        session_to_update.patient_id = patient.id
                        session_to_update.record_done = record_done
                        session_to_update.record_launched = record_launched
                        messagebox.showinfo("Sucesso", "Sessão atualizada com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Sessão não encontrada.")
                else:
                    # Creating new session
                    new_session = Appointment(
                        date=session_date,
                        patient_id=patient.id,
                        record_done=record_done,
                        record_launched=record_launched
                    )
                    session.add(new_session)
                    messagebox.showinfo("Sucesso", "Sessão salva com sucesso!")
            else:
                messagebox.showerror("Erro", "Paciente não encontrado.")

        self.update_sessions_list()
        self.clear_form()

    def delete_session(self):
        """Delete the selected session from the database"""
        if not self.selected_session_id:
            messagebox.showerror("Error", "Selecione um atendimento para excluir.")
            return

        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza de que deseja excluir este atendimento?"):
            with session_scope() as session:
                session_to_delete = session.query(Appointment).filter(Appointment.id == self.selected_session_id).first()
                if session_to_delete:
                    session.delete(session_to_delete)
                    messagebox.showinfo("Success", "Atendimento excluído com sucesso!")
                    self.update_sessions_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "Atendimento não encontrado.")
        self.update_sessions_list() # update session list after delete

    def load_session_for_editing(self, event):
        """Load the selected session's data into the form for editing"""
        selected_index = self.sessions_listbox.curselection()
        if not selected_index:
            return

        selected_session_info = self.sessions_listbox.get(selected_index[0])
        session_date_str = selected_session_info.split(" - ")[0]

        with session_scope() as session:
            try:
                session_date = datetime.strptime(session_date_str, "%d-%m-%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de data inválido na lista.")
                return

            session_to_load = session.query(Appointment).filter(Appointment.date == session_date).first()

            if session_to_load:
                self.selected_session_id = session_to_load.id
                if session_to_load.patient:
                    self.patient_combo.set(session_to_load.patient.name)
                else:
                    self.patient_combo.set("")  # Set to empty if no patient associated
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, session_to_load.date.strftime("%d-%m-%Y"))
                self.record_done_var.set(session_to_load.record_done)
                self.record_launched_var.set(session_to_load.record_launched)
                self.delete_button.config(state=tk.NORMAL)  # Enable delete button
                self.save_button.config(text="Atualizar")
            else:
                messagebox.showerror("Error", "Atendimento não encontrado.")

    def update_sessions_list(self):
        """Update the list of latest sessions"""
        self.sessions_listbox.delete(0, tk.END)  # Clear existing list

        with session_scope() as session:
            sessions = session.query(Appointment).order_by(Appointment.date.desc()).limit(10).all()  # Get latest 10 sessions
            for session in sessions:
                patient_name = session.patient.name if session.patient else "N/A"
                session_info = f"{session.date.strftime('%d-%m-%Y')} - {patient_name} - Feito: {session.record_done} - Lançado: {session.record_launched}"
                self.sessions_listbox.insert(tk.END, session_info)

    def clear_form(self):
        """Clear the form fields and reset to default state"""
        self.selected_session_id = None
        self.patient_combo.set("")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.record_done_var.set(False)
        self.record_launched_var.set(False)
        self.delete_button.config(state=tk.DISABLED)
        self.save_button.config(text="Salvar")
