import tkinter as tk
from tkinter import ttk
import database
from datetime import date


class DashboardScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self._build()

    def _build(self):
        c = self.colors

        # Topbar
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="🏠  Dashboard",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Label(topbar,
            text=f"📅  {date.today().strftime('%A, %d %B %Y')}",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 11)).pack(side="right", padx=20)
        tk.Frame(self, bg=c["border"], height=1).pack(fill="x")

        # Scrollable area
        canvas = tk.Canvas(self, bg=c["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=c["bg"])
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Refresh button
        tk.Button(self.scroll_frame,
            text="🔄  Refresh",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 10), relief="flat",
            padx=12, pady=5, cursor="hand2",
            command=self._refresh
        ).pack(anchor="e", padx=20, pady=(10, 0))

        self._load_all()

    def _refresh(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        c = self.colors
        tk.Button(self.scroll_frame,
            text="🔄  Refresh",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 10), relief="flat",
            padx=12, pady=5, cursor="hand2",
            command=self._refresh
        ).pack(anchor="e", padx=20, pady=(10, 0))

        self._load_all()

    def _load_all(self):
        self._build_stats()
        self._build_recent_patients()
        self._build_today_appointments()

    def _build_stats(self):
        c = self.colors

        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM doctors")
        total_doctors = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE appt_date=?",
            (str(date.today()),))
        today_appts = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='Scheduled'")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM prescriptions")
        total_rx = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM certificates")
        total_certs = cursor.fetchone()[0]

        conn.close()

        stats = [
            ("👥", "Total Patients",    total_patients, c["accent"]),
            ("👨‍⚕️","Doctors & Staff",  total_doctors,  c["accent2"]),
            ("📅", "Today's Appts",     today_appts,    c["accent3"]),
            ("⏳", "Pending",           pending,        c["accent4"]),
            ("💊", "Prescriptions",     total_rx,       c["accent"]),
            ("📄", "Certificates",      total_certs,    c["accent2"]),
        ]

        tk.Label(self.scroll_frame,
            text="📊  Overview",
            bg=c["bg"], fg=c["text"],
            font=("Courier", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(12, 8))

        grid = tk.Frame(self.scroll_frame, bg=c["bg"])
        grid.pack(fill="x", padx=16)

        for i, (icon, label, value, color) in enumerate(stats):
            card = tk.Frame(grid, bg=c["surface"], padx=20, pady=16)
            card.grid(row=i//3, column=i%3,
                padx=6, pady=6, sticky="ew")
            grid.columnconfigure(i%3, weight=1)

            tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(0, 10))

            tk.Label(card, text=icon,
                bg=c["surface"], fg=color,
                font=("Courier", 26)).pack(anchor="w")
            tk.Label(card, text=str(value),
                bg=c["surface"], fg=color,
                font=("Courier", 30, "bold")).pack(anchor="w")
            tk.Label(card, text=label,
                bg=c["surface"], fg=c["muted"],
                font=("Courier", 9)).pack(anchor="w")

    def _build_recent_patients(self):
        c = self.colors

        tk.Frame(self.scroll_frame, bg=c["border"], height=1).pack(
            fill="x", padx=16, pady=(16, 0))
        tk.Label(self.scroll_frame,
            text="👥  Recent Patients",
            bg=c["bg"], fg=c["text"],
            font=("Courier", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(12, 6))

        frame = tk.Frame(self.scroll_frame, bg=c["surface"])
        frame.pack(fill="x", padx=16, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background=c["surface"], foreground=c["text"],
            fieldbackground=c["surface"], rowheight=28,
            font=("Courier", 11))
        style.configure("Treeview.Heading",
            background=c["surface2"], foreground=c["muted"],
            font=("Courier", 10, "bold"), relief="flat")
        style.map("Treeview",
            background=[("selected", c["surface2"])],
            foreground=[("selected", c["accent"])])

        cols = ("id","name","age","gender","blood","phone","registered")
        tree = ttk.Treeview(frame, columns=cols,
            show="headings", height=6)

        for col, label, width in [
            ("id","ID",50), ("name","Full Name",180),
            ("age","Age",50), ("gender","Gender",80),
            ("blood","Blood",70), ("phone","Phone",140),
            ("registered","Registered",110)
        ]:
            tree.heading(col, text=label)
            tree.column(col, width=width, anchor="center")
        tree.column("name", anchor="w")
        tree.pack(fill="x")

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, birth_date, gender,
                   blood_type, phone, created_at
            FROM patients ORDER BY id DESC LIMIT 8
        """)
        for row in cursor.fetchall():
            pid, name, birth, gender, blood, phone, created = row
            try:
                born = date.fromisoformat(birth)
                age = (date.today() - born).days // 365
            except:
                age = "?"
            tree.insert("", "end", values=(
                f"#{pid}", name, age,
                gender or "—", blood or "—",
                phone or "—", created or "—"
            ))
        conn.close()

    def _build_today_appointments(self):
        c = self.colors

        tk.Frame(self.scroll_frame, bg=c["border"], height=1).pack(
            fill="x", padx=16, pady=(8, 0))
        tk.Label(self.scroll_frame,
            text="📅  Today's Appointments",
            bg=c["bg"], fg=c["text"],
            font=("Courier", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(12, 6))

        frame = tk.Frame(self.scroll_frame, bg=c["surface"])
        frame.pack(fill="x", padx=16, pady=(0, 16))

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.appt_time, p.full_name, d.full_name,
                   a.reason, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors  d ON a.doctor_id  = d.id
            WHERE a.appt_date = ?
            ORDER BY a.appt_time
        """, (str(date.today()),))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            tk.Label(frame,
                text="  No appointments scheduled for today.",
                bg=c["surface"], fg=c["muted"],
                font=("Courier", 11), pady=16
            ).pack(anchor="w", padx=16)
            return

        status_colors = {
            "Done":        c["accent"],
            "In Progress": c["accent2"],
            "Scheduled":   c["accent3"],
            "Cancelled":   c["accent4"],
        }

        for appt_time, patient, doctor, reason, status in rows:
            row_frame = tk.Frame(frame, bg=c["surface"])
            row_frame.pack(fill="x", padx=12, pady=4)

            tk.Label(row_frame,
                text=appt_time or "—",
                bg=c["surface"], fg=c["accent"],
                font=("Courier", 11, "bold"), width=7
            ).pack(side="left")

            tk.Label(row_frame,
                text=patient,
                bg=c["surface"], fg=c["text"],
                font=("Courier", 11), width=20, anchor="w"
            ).pack(side="left", padx=8)

            tk.Label(row_frame,
                text=doctor,
                bg=c["surface"], fg=c["muted"],
                font=("Courier", 10), width=18, anchor="w"
            ).pack(side="left")

            tk.Label(row_frame,
                text=reason or "—",
                bg=c["surface"], fg=c["muted"],
                font=("Courier", 10), anchor="w"
            ).pack(side="left", padx=8)

            color = status_colors.get(status, c["muted"])
            tk.Label(row_frame,
                text=status,
                bg=color,
                fg="#000" if status == "Done" else "white",
                font=("Courier", 9, "bold"),
                padx=8, pady=2
            ).pack(side="right", padx=8)

            tk.Frame(frame, bg=c["border"], height=1).pack(
                fill="x", padx=12)