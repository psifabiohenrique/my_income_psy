import tkinter as tk

from views.patient_form import PatientFormView
from views.patient_list import PatientListView
from views.session_form import SessionFormView
from views.statistics_form import StatisticsView
from views.spreadsheet_integration_form import SpreadsheetIntegrationForm


class AppController(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.views = {}
        # self.create_views()
        self.show_view("patient_list")

    def show_view(self, name, **kwargs):
        # Destroy all existing views
        for view_name, view in self.views.items():
            if view:
                view.destroy()
        self.views = {}

        # Recreate the desired view
        if name == "patient_form":
            self.views["patient_form"] = PatientFormView(
                self, self.show_view, patient_id=kwargs.get("patient_id")
            )
        elif name == "patient_list":
            self.views["patient_list"] = PatientListView(self, self.show_view)
        elif name == "session_form":
            self.views["session_form"] = SessionFormView(self, self.show_view)
        elif name == "statistics":
            self.views["statistics"] = StatisticsView(self, self.show_view)
        elif name == "spreedsheet_integration":
            self.views["spreedsheet_integration"] = SpreadsheetIntegrationForm(
                self, self.show_view
            )

        # Grid the desired view
        current_view = self.views[name]
        current_view.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
