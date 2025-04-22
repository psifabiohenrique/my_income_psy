import tkinter as tk
from tkinter import filedialog, ttk

from src.spreadsheet_integration import SpreadsheetIntegration


class SpreadsheetIntegrationForm(tk.Frame):
    def __init__(self, master, show_view_callback):
        super().__init__(master)
        self.show_view = show_view_callback
        self.spreadsheet_to_open = ""
        self.spreadsheet_to_save = ""
        self.integration = SpreadsheetIntegration()

        # Cria uma instância de Tk
        self.root = tk.Toplevel(
            master
        )  # Use Toplevel para não criar uma nova janela principal
        self.root.withdraw()  # Oculta a janela principal

        ttk.Label(self, text="Spreadsheet Integration", font=("Arial", 16)).pack(
            pady=10, anchor="center"
        )

        ttk.Button(
            self,
            text="Open spreadsheet",
            command=self.open_archive_selector,
        ).pack(pady=20, anchor="center")

        ttk.Button(
            self,
            text="Save spreadsheet",
            command=self.save_archive_selector,
        ).pack(pady=20, anchor="center")

        ttk.Button(
            self,
            text="Return to patient list",
            command=lambda: self.show_view("patient_list"),
        ).pack(pady=50, anchor="center")

    def open_archive_selector(self):
        self.spreadsheet_to_open = filedialog.askopenfilename(
            title="Select spreadsheet",
            parent=self.root,  # Use parent=self.root
        )
        if self.spreadsheet_to_open:
            self.integration.import_from_spreadsheet(self.spreadsheet_to_open)

    def save_archive_selector(self):
        self.spreadsheet_to_save = filedialog.asksaveasfilename(
            title="Save Spreadsheet",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            parent=self.root,  # Use parent=self.root
        )
        if self.spreadsheet_to_save:
            self.integration.export_to_spreadsheet(self.spreadsheet_to_save)
