import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import db_connector
import database


class LoginScreen(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("MediCore — Login")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(bg="#0b1220")

        self.colors = {
            "bg":      "#0b1220",
            "surface": "#111827",
            "surface2":"#1a2438",
            "border":  "#1e2d45",
            "accent":  "#00c9a7",
            "accent4": "#ef4444",
            "text":    "#e2e8f0",
            "muted":   "#64748b",
        }

        self.db_type = tk.StringVar(value="sqlite")
        self._build()

    def _build(self):
        c = self.colors

        tk.Label(self, text="🏥",
            bg=c["bg"], fg=c["accent"],
            font=("Courier", 48)).pack(pady=(32, 0))

        tk.Label(self, text="MediCore",
            bg=c["bg"], fg=c["accent"],
            font=("Courier", 24, "bold")).pack()

        tk.Label(self, text="HOSPITAL MANAGEMENT SYSTEM",
            bg=c["bg"], fg=c["muted"],
            font=("Courier", 8)).pack(pady=(0, 24))

        tk.Frame(self, bg=c["border"], height=1).pack(fill="x")

        card = tk.Frame(self, bg=c["surface"], padx=32, pady=24)
        card.pack(fill="x", padx=32, pady=24)

        tk.Label(card, text="USERNAME",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(anchor="w")

        self.username = tk.Entry(card,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 12), relief="flat",
            insertbackground=c["accent"])
        self.username.pack(fill="x", ipady=7, pady=(4, 12))
        self.username.insert(0, "admin")

        tk.Label(card, text="PASSWORD",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(anchor="w")

        self.password = tk.Entry(card,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 12), relief="flat",
            insertbackground=c["accent"], show="●")
        self.password.pack(fill="x", ipady=7, pady=(4, 16))

        tk.Frame(card, bg=c["border"], height=1).pack(fill="x", pady=(0, 16))

        tk.Label(card, text="DATABASE TYPE",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(anchor="w")

        db_frame = tk.Frame(card, bg=c["surface"])
        db_frame.pack(fill="x", pady=(4, 12))

        for label, value in [("SQLite","sqlite"),("MySQL","mysql")]:
            tk.Radiobutton(
                db_frame, text=label,
                variable=self.db_type, value=value,
                bg=c["surface"], fg=c["text"],
                selectcolor=c["surface2"],
                activebackground=c["surface"],
                font=("Courier", 10),
                command=self._toggle_panel
            ).pack(side="left", padx=(0, 16))

        self.panel = tk.Frame(card, bg=c["surface"])
        self.panel.pack(fill="x")
        self._build_sqlite_panel()

        tk.Button(card,
            text="🔌  Connect & Login",
            bg=c["accent"], fg="#000",
            font=("Courier", 12, "bold"),
            relief="flat", pady=10, cursor="hand2",
            command=self._login
        ).pack(fill="x", pady=(16, 0))

        self.status = tk.Label(self, text="",
            bg=c["bg"], fg=c["accent4"],
            font=("Courier", 10))
        self.status.pack(pady=8)

    def _toggle_panel(self):
        for w in self.panel.winfo_children():
            w.destroy()
        t = self.db_type.get()
        if t == "sqlite":
            self._build_sqlite_panel()
        elif t == "mysql":
            self._build_mysql_panel()
        else:
            self._build_libreoffice_panel()

    def _field(self, parent, label, default="", show=None):
        c = self.colors
        tk.Label(parent, text=label,
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(anchor="w")
        var = tk.StringVar(value=default)
        tk.Entry(parent, textvariable=var,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 11), relief="flat",
            insertbackground=c["accent"],
            show=show or ""
        ).pack(fill="x", ipady=5, pady=(2, 8))
        return var

    def _build_sqlite_panel(self):
        c = self.colors
        tk.Label(self.panel, text="DATABASE FILE",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(anchor="w")
        row = tk.Frame(self.panel, bg=c["surface"])
        row.pack(fill="x", pady=(2, 0))
        self.sqlite_path = tk.StringVar(value="hospital.db")
        tk.Entry(row, textvariable=self.sqlite_path,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 11), relief="flat"
        ).pack(side="left", fill="x", expand=True, ipady=5)
        tk.Button(row, text="Browse",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 9), relief="flat", cursor="hand2",
            command=lambda: self.sqlite_path.set(
                filedialog.asksaveasfilename(
                    defaultextension=".db",
                    filetypes=[("SQLite","*.db")]
                ) or self.sqlite_path.get())
        ).pack(side="right", padx=(4, 0))

    def _build_mysql_panel(self):
        self.mysql_host = self._field(self.panel, "HOST", "localhost")
        self.mysql_port = self._field(self.panel, "PORT", "3306")
        self.mysql_db   = self._field(self.panel, "DATABASE NAME", "hospital_db")
        self.mysql_user = self._field(self.panel, "MYSQL USER", "root")
        self.mysql_pass = self._field(self.panel, "MYSQL PASSWORD", "", show="●")

    

    def _login(self):
        user = self.username.get().strip()
        pwd  = self.password.get().strip()

        if user != "admin" or pwd != "admin":
            self.status.configure(text="❌ Invalid username or password")
            return

        t = self.db_type.get()
        if t == "sqlite":
            ok, msg = db_connector.connect_sqlite(self.sqlite_path.get().strip())
        elif t == "mysql":
            ok, msg = db_connector.connect_mysql(
                self.mysql_host.get(), self.mysql_port.get(),
                self.mysql_db.get(), self.mysql_user.get(),
                self.mysql_pass.get()
            )
        else:
            ok, msg = db_connector.connect_libreoffice(self.odb_path.get().strip())

        self.status.configure(text=msg,
            fg=self.colors["accent"] if ok else self.colors["accent4"])

        if ok:
            database.setup_database()
            database.insert_sample_data()
            self.after(800, self._launch)

    def _launch(self):
        self.destroy()
        from main import HospitalApp
        app = HospitalApp()
        app.mainloop()


if __name__ == "__main__":
    app = LoginScreen()
    app.mainloop()