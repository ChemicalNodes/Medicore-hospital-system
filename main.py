import tkinter as tk
import database


class HospitalApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("MediCore — Hospital Management System")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self.configure(bg="#0b1220")

        self.colors = {
            "bg":       "#0b1220",
            "surface":  "#111827",
            "surface2": "#1a2438",
            "border":   "#1e2d45",
            "accent":   "#00c9a7",
            "accent2":  "#3b82f6",
            "accent3":  "#f59e0b",
            "accent4":  "#ef4444",
            "text":     "#e2e8f0",
            "muted":    "#64748b",
        }

        self.active_btn = None
        self._build_layout()

    def _build_layout(self):
        c = self.colors

        self.sidebar = tk.Frame(self, bg=c["surface"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(self, bg=c["bg"])
        self.content_area.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._navigate("dashboard", None)

    def _build_sidebar(self):
        c = self.colors

        logo_frame = tk.Frame(self.sidebar, bg=c["surface"], pady=16)
        logo_frame.pack(fill="x")

        tk.Label(logo_frame, text="🏥 MediCore",
            bg=c["surface"], fg=c["accent"],
            font=("Courier", 16, "bold")
        ).pack(padx=18, anchor="w")

        tk.Label(logo_frame, text="HOSPITAL SYSTEM",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 8)
        ).pack(padx=18, anchor="w")

        tk.Frame(self.sidebar, bg=c["border"], height=1).pack(fill="x")

        tk.Label(self.sidebar, text="MAIN MENU",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 8), pady=8
        ).pack(padx=18, anchor="w")

        nav_items = [
            ("🏠",  "Dashboard",       "dashboard"),
            ("👥",  "Patients",        "patients"),
            ("📅",  "Appointments",    "appointments"),
            ("📋",  "Medical Records", "records"),
            ("💊",  "Prescriptions",   "prescriptions"),
            ("📄",  "Certificates",    "certificates"),
            ("👨‍⚕️", "Doctors & Staff", "doctors"),
        ]

        for icon, label, page_id in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}  {label}",
                bg=c["surface"], fg=c["muted"],
                font=("Courier", 11),
                anchor="w", relief="flat", bd=0,
                padx=10, pady=10, cursor="hand2",
                activebackground=c["surface2"],
                activeforeground=c["text"],
            )
            btn.configure(
                command=lambda pid=page_id, b=btn: self._navigate(pid, b)
            )
            btn.pack(fill="x")

    def _navigate(self, page_id, btn):
        c = self.colors

        if self.active_btn:
            self.active_btn.configure(bg=c["surface"], fg=c["muted"])
        if btn:
            btn.configure(bg=c["surface2"], fg=c["accent"])
            self.active_btn = btn

        for widget in self.content_area.winfo_children():
            widget.destroy()

        pages = {
            "dashboard":     self._load_dashboard,
            "patients":      self._load_patients,
            "appointments":  self._load_appointments,
            "records":       self._load_records,
            "prescriptions": self._load_prescriptions,
            "certificates":  self._load_certificates,
            "doctors":       self._load_doctors,
        }

        if page_id in pages:
            pages[page_id]()

    def _load_dashboard(self):
        from ui_dashboard import DashboardScreen
        screen = DashboardScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)

    def _load_patients(self):
        from ui_patients import PatientsScreen
        screen = PatientsScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)

    def _load_appointments(self):
        from ui_appointments import AppointmentsScreen
        screen = AppointmentsScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)

    def _load_records(self):
        from ui_records import RecordsScreen
        screen = RecordsScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)

    def _load_prescriptions(self):
        from ui_prescriptions import PrescriptionsScreen
        screen = PrescriptionsScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)

    def _load_certificates(self):
        from ui_certificates import CertificatesScreen
        screen = CertificatesScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)

    def _load_doctors(self):
        from ui_doctors import DoctorsScreen
        screen = DoctorsScreen(self.content_area, self.colors)
        screen.pack(fill="both", expand=True)
        
if __name__ == "__main__":
    from login import LoginScreen
    app = LoginScreen()
    app.mainloop()