import tkinter as tk
from controller import AppController

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestão de Consultório")
    root.geometry("800x800")

    try:
        root.iconbitmap("./icon.ico")
    except:
        ...

    app = AppController(root)
    app.pack(fill="both", expand=True)

    root.mainloop()
