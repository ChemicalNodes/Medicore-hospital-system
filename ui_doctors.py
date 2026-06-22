import tkinter as tk
from tkinter import ttk, messagebox
import database


class DoctorsScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self.selected_id = None
        self._build_topbar()
        self._build_body()
        self.load_doctors()

    def _build_topbar(self):
        c = self.colors
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="👨‍⚕️  Doctors & Staff",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Button(topbar, text="＋  Add Doctor",
            bg=c["accent"], fg="#000",
            font=("Courier", 11, "bold"),
            relief="flat", padx=14, pady=6,
            cursor="hand2", command=self._open_form
        ).pack(side="right", padx=20)
        tk.Frame(self, bg=c["border"], height=1).pack(fill="x")

    def _build_body(self):
        c = self.colors

        body = tk.Frame(self, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=12)

        left = tk.Frame(body, bg=c["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg=c["surface"], width=260)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        self._build_table(left)
        self._build_profile(right)

    def _build_table(self, parent):
        c = self.colors

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background=c["surface"], foreground=c["text"],
            fieldbackground=c["surface"], rowheight=32,
            font=("Courier", 11))
        style.configure("Treeview.Heading",
            background=c["surface2"], foreground=c["muted"],
            font=("Courier", 10, "bold"), relief="flat")
        style.map("Treeview",
            background=[("selected", c["surface2"])],
            foreground=[("selected", c["accent"])])

        frame = tk.Frame(parent, bg=c["surface"])
        frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(frame)
        sb.pack(side="right", fill="y")

        cols = ("id","name","specialty","phone","email","schedule")
        self.tree = ttk.Treeview(frame, columns=cols,
            show="headings", selectmode="browse",
            yscrollcommand=sb.set)

        for col, label, width in [
            ("id","ID",50), ("name","Full Name",200),
            ("specialty","Specialty",150), ("phone","Phone",130),
            ("email","Email",190), ("schedule","Schedule",100)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("name", anchor="w")
        self.tree.column("email", anchor="w")

        self.tree.pack(fill="both", expand=True)
        sb.configure(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_row = tk.Frame(parent, bg=c["bg"])
        btn_row.pack(fill="x", pady=8)
        tk.Button(btn_row, text="✏️  Edit",
            bg=c["accent2"], fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", padx=12, pady=6,
            cursor="hand2", command=self._edit
        ).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="🗑  Delete",
            bg=c["accent4"], fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", padx=12, pady=6,
            cursor="hand2", command=self._delete
        ).pack(side="left")

    def _build_profile(self, parent):
        c = self.colors

        tk.Label(parent, text="DOCTOR PROFILE",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(pady=(16, 4))

        tk.Label(parent, text="👨‍⚕️",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 36), width=3
        ).pack(pady=8)

        self.profile_name = tk.Label(parent,
            text="Select a doctor",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 12, "bold"), wraplength=220)
        self.profile_name.pack(pady=(4, 0))

        self.profile_spec = tk.Label(parent, text="",
            bg=c["surface"], fg=c["accent"],
            font=("Courier", 10))
        self.profile_spec.pack()

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=10)

        self.info_labels = {}
        for key, label in [
            ("phone",    "Phone"),
            ("email",    "Email"),
            ("schedule", "Schedule"),
            ("hired",    "Hired Date"),
            ("patients", "Total Patients"),
        ]:
            row = tk.Frame(parent, bg=c["surface"])
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label,
                bg=c["surface"], fg=c["muted"],
                font=("Courier", 9), anchor="w"
            ).pack(side="left")
            val = tk.Label(row, text="—",
                bg=c["surface"], fg=c["text"],
                font=("Courier", 9, "bold"), anchor="e")
            val.pack(side="right")
            self.info_labels[key] = val

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=8)

        btn_frame = tk.Frame(parent, bg=c["surface"])
        btn_frame.pack(fill="x", padx=12)
        tk.Button(btn_frame, text="✏️  Edit",
            bg=c["accent2"], fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", padx=10, pady=6,
            cursor="hand2", command=self._edit
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))
        tk.Button(btn_frame, text="🗑  Delete",
            bg=c["accent4"], fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", padx=10, pady=6,
            cursor="hand2", command=self._delete
        ).pack(side="right", expand=True, fill="x", padx=(4, 0))

    def load_doctors(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, specialty, phone, email, schedule_days
            FROM doctors ORDER BY id DESC
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row)
        conn.close()

    def _on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        self.selected_id = int(selected)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT full_name, specialty, phone, email, schedule_days, hire_date
            FROM doctors WHERE id=?
        """, (self.selected_id,))
        row = cursor.fetchone()

        # Count patients assigned
        cursor.execute(
            "SELECT COUNT(*) FROM patients WHERE doctor_id=?",
            (self.selected_id,))
        patient_count = cursor.fetchone()[0]
        conn.close()

        if not row:
            return

        name, spec, phone, email, schedule, hired = row
        self.profile_name.configure(text=name)
        self.profile_spec.configure(text=spec or "")
        self.info_labels["phone"].configure(text=phone or "—")
        self.info_labels["email"].configure(text=email or "—")
        self.info_labels["schedule"].configure(text=schedule or "—")
        self.info_labels["hired"].configure(text=hired or "—")
        self.info_labels["patients"].configure(
            text=str(patient_count),
            fg=self.colors["accent"])

    def _open_form(self, data=None):
        c = self.colors
        is_edit = data is not None

        form = tk.Toplevel(self)
        form.title("Edit Doctor" if is_edit else "Add Doctor")
        form.geometry("440x400")
        form.configure(bg=c["bg"])
        form.grab_set()

        tk.Label(form,
            text="✏️  Edit Doctor" if is_edit else "👨‍⚕️  New Doctor",
            bg=c["bg"], fg=c["accent"],
            font=("Courier", 15, "bold")).pack(pady=16)
        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")

        ff = tk.Frame(form, bg=c["bg"])
        ff.pack(fill="both", expand=True, padx=24, pady=16)

        entries = {}

        def field(label, key, row, options=None):
            tk.Label(ff, text=label,
                bg=c["bg"], fg=c["muted"],
                font=("Courier", 9)).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            if options:
                w = ttk.Combobox(ff, textvariable=var,
                    values=options, state="readonly",
                    font=("Courier", 11), width=26)
            else:
                w = tk.Entry(ff, textvariable=var,
                    bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    insertbackground=c["accent"], width=28)
            w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            entries[key] = var
            if is_edit and data and key in data:
                var.set(data[key])

        field("Full Name *",  "full_name",    0)
        field("Specialty *",  "specialty",    1, [
            "General Medicine","Cardiology","Pediatrics",
            "Surgery","Neurology","Orthopedics",
            "Dermatology","Gynecology","Other"])
        field("Phone",        "phone",        2)
        field("Email",        "email",        3)
        field("Schedule",     "schedule_days",4, [
            "Mon-Fri","Mon-Sat","Sun-Thu","All Week","On Call"])

        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")
        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(pady=14)

        def save():
            name     = entries["full_name"].get().strip()
            spec     = entries["specialty"].get().strip()
            phone    = entries["phone"].get().strip()
            email    = entries["email"].get().strip()
            schedule = entries["schedule_days"].get().strip()

            if not name or not spec:
                messagebox.showwarning("Missing",
                    "Name and Specialty are required.", parent=form)
                return

            conn = database.get_connection()
            cursor = conn.cursor()
            if is_edit:
                cursor.execute("""
                    UPDATE doctors SET full_name=?, specialty=?,
                    phone=?, email=?, schedule_days=? WHERE id=?
                """, (name, spec, phone, email, schedule, self.selected_id))
            else:
                cursor.execute("""
                    INSERT INTO doctors
                    (full_name, specialty, phone, email, schedule_days)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, spec, phone, email, schedule))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_doctors()
            messagebox.showinfo("Saved", "Doctor saved! ✅")

        tk.Button(btn_row, text="Cancel",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 11), relief="flat",
            padx=16, pady=7, cursor="hand2",
            command=form.destroy).pack(side="left", padx=8)
        tk.Button(btn_row, text="💾  Save",
            bg=c["accent"], fg="#000",
            font=("Courier", 11, "bold"),
            relief="flat", padx=16, pady=7,
            cursor="hand2", command=save).pack(side="left", padx=8)

    def _edit(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click a doctor first.")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT full_name, specialty, phone, email, schedule_days
            FROM doctors WHERE id=?
        """, (self.selected_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            keys = ["full_name","specialty","phone","email","schedule_days"]
            self._open_form(dict(zip(keys, row)))

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click a doctor first.")
            return
        if messagebox.askyesno("Confirm", "Delete this doctor?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doctors WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.selected_id = None
            self.profile_name.configure(text="Select a doctor")
            self.profile_spec.configure(text="")
            for lbl in self.info_labels.values():
                lbl.configure(text="—", fg=self.colors["text"])
            self.load_doctors()