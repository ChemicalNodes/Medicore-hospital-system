import tkinter as tk
from tkinter import ttk, messagebox
import database
from datetime import date


class PatientsScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self.selected_patient_id = None
        self._build_topbar()
        self._build_body()
        self.load_patients()

    def _build_topbar(self):
        c = self.colors
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="👥  Patients",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Button(topbar, text="＋  Register New Patient",
            bg=c["accent"], fg="#000",
            font=("Courier", 11, "bold"),
            relief="flat", padx=14, pady=6,
            cursor="hand2", command=self._open_form
        ).pack(side="right", padx=20)
        tk.Frame(self, bg=c["border"], height=1).pack(fill="x")

    def _build_body(self):
        c = self.colors

        # Search bar
        search_frame = tk.Frame(self, bg=c["bg"], pady=10)
        search_frame.pack(fill="x", padx=16)
        tk.Label(search_frame, text="🔍  Search:",
            bg=c["bg"], fg=c["muted"],
            font=("Courier", 11)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_patients())
        tk.Entry(search_frame,
            textvariable=self.search_var,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 11), relief="flat",
            insertbackground=c["accent"], width=30
        ).pack(side="left", padx=10, ipady=5)

        # Two column layout
        body = tk.Frame(self, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=8)

        left = tk.Frame(body, bg=c["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg=c["surface"], width=280)
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

        cols = ("id","name","age","gender","blood","phone")
        self.tree = ttk.Treeview(frame, columns=cols,
            show="headings", selectmode="browse",
            yscrollcommand=sb.set)

        for col, label, width in [
            ("id","ID",50), ("name","Full Name",200),
            ("age","Age",50), ("gender","Gender",80),
            ("blood","Blood",70), ("phone","Phone",140)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("name", anchor="w")

        self.tree.pack(fill="both", expand=True)
        sb.configure(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Action buttons
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

        tk.Label(parent, text="PATIENT PROFILE",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(pady=(16, 4))

        tk.Label(parent, text="👤",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 36), width=3
        ).pack(pady=8)

        self.profile_name = tk.Label(parent,
            text="Select a patient",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 12, "bold"), wraplength=240)
        self.profile_name.pack(pady=(4, 0))

        self.profile_id = tk.Label(parent, text="",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9))
        self.profile_id.pack()

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=10)

        self.info_labels = {}
        for key, label in [
            ("birth",   "Date of Birth"),
            ("age",     "Age"),
            ("gender",  "Gender"),
            ("blood",   "Blood Type"),
            ("phone",   "Phone"),
            ("address", "Address"),
            ("allergy", "Allergies"),
            ("doctor",  "Assigned Doctor"),
            ("since",   "Registered"),
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

    def load_patients(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_var.get().strip()
        conn = database.get_connection()
        cursor = conn.cursor()

        if search:
            cursor.execute("""
                SELECT id, full_name, birth_date, gender, blood_type, phone
                FROM patients
                WHERE full_name LIKE ? OR phone LIKE ?
                ORDER BY id DESC
            """, (f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""
                SELECT id, full_name, birth_date, gender, blood_type, phone
                FROM patients ORDER BY id DESC
            """)

        for row in cursor.fetchall():
            pid, name, birth, gender, blood, phone = row
            try:
                born = date.fromisoformat(birth)
                age = (date.today() - born).days // 365
            except:
                age = "?"
            self.tree.insert("", "end", iid=pid, values=(
                f"#{pid}", name, age,
                gender or "—", blood or "—", phone or "—"
            ))
        conn.close()

    def _on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        self.selected_patient_id = int(selected)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.full_name, p.birth_date, p.gender,
                   p.blood_type, p.phone, p.address,
                   p.allergies, p.created_at, d.full_name
            FROM patients p
            LEFT JOIN doctors d ON p.doctor_id = d.id
            WHERE p.id = ?
        """, (self.selected_patient_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        name, birth, gender, blood, phone, address, allergies, created, doctor = row

        try:
            born = date.fromisoformat(birth)
            age = f"{(date.today() - born).days // 365} years"
            birth_display = birth
        except:
            age = "?"
            birth_display = birth or "—"

        self.profile_name.configure(text=name)
        self.profile_id.configure(text=f"Patient #{self.selected_patient_id}")
        self.info_labels["birth"].configure(text=birth_display)
        self.info_labels["age"].configure(text=age)
        self.info_labels["gender"].configure(text=gender or "—")
        self.info_labels["blood"].configure(
            text=blood or "—",
            fg="#ef4444" if blood else self.colors["text"])
        self.info_labels["phone"].configure(text=phone or "—")
        self.info_labels["address"].configure(text=address or "—")
        self.info_labels["allergy"].configure(
            text=allergies or "None",
            fg="#f59e0b" if allergies else self.colors["text"])
        self.info_labels["doctor"].configure(text=doctor or "Not assigned")
        self.info_labels["since"].configure(text=created or "—")

    def _open_form(self, data=None):
        c = self.colors
        is_edit = data is not None

        form = tk.Toplevel(self)
        form.title("Edit Patient" if is_edit else "Register New Patient")
        form.geometry("500x560")
        form.configure(bg=c["bg"])
        form.grab_set()

        tk.Label(form,
            text="✏️  Edit Patient" if is_edit else "👤  New Patient",
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
                    font=("Courier", 11), width=28)
            else:
                w = tk.Entry(ff, textvariable=var,
                    bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    insertbackground=c["accent"], width=30)
            w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            entries[key] = var
            if is_edit and data and key in data:
                var.set(data[key])
            return var

        field("Full Name *",     "full_name",  0)
        field("Date of Birth *", "birth_date", 1)
        field("Gender *",        "gender",     2,
            ["Male","Female","Other"])
        field("Blood Type",      "blood_type", 3,
            ["A+","A-","B+","B-","AB+","AB-","O+","O-"])
        field("Phone",           "phone",      4)
        field("Address",         "address",    5)
        field("Allergies",       "allergies",  6)

        # Doctor dropdown
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM doctors ORDER BY full_name")
        doctors = cursor.fetchall()
        conn.close()

        doctor_options = [f"{d[0]} — {d[1]}" for d in doctors]

        tk.Label(ff, text="Assign Doctor",
            bg=c["bg"], fg=c["muted"],
            font=("Courier", 9)).grid(row=7, column=0, sticky="w", pady=4)
        doctor_var = tk.StringVar()
        ttk.Combobox(ff, textvariable=doctor_var,
            values=doctor_options,
            font=("Courier", 11), width=28
        ).grid(row=7, column=1, padx=12, pady=4, ipady=5)

        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")
        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(pady=14)

        def save():
            name      = entries["full_name"].get().strip()
            birth     = entries["birth_date"].get().strip()
            gender    = entries["gender"].get().strip()
            blood     = entries["blood_type"].get().strip()
            phone     = entries["phone"].get().strip()
            address   = entries["address"].get().strip()
            allergies = entries["allergies"].get().strip()

            if not name or not birth or not gender:
                messagebox.showwarning("Missing",
                    "Full Name, Date of Birth and Gender are required.",
                    parent=form)
                return

            doctor_id = None
            doc_str = doctor_var.get()
            if doc_str:
                try:
                    doctor_id = int(doc_str.split("—")[0].strip())
                except:
                    pass

            conn = database.get_connection()
            cursor = conn.cursor()
            if is_edit:
                cursor.execute("""
                    UPDATE patients SET full_name=?, birth_date=?,
                    gender=?, blood_type=?, phone=?, address=?,
                    allergies=?, doctor_id=? WHERE id=?
                """, (name, birth, gender, blood, phone,
                      address, allergies, doctor_id,
                      self.selected_patient_id))
            else:
                cursor.execute("""
                    INSERT INTO patients
                    (full_name, birth_date, gender, blood_type,
                     phone, address, allergies, doctor_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, birth, gender, blood,
                      phone, address, allergies, doctor_id))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_patients()
            messagebox.showinfo("Saved", "Patient saved! ✅")

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
        if not self.selected_patient_id:
            messagebox.showwarning("No Selection", "Click a patient first.")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT full_name, birth_date, gender, blood_type,
                   phone, address, allergies FROM patients WHERE id=?
        """, (self.selected_patient_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            keys = ["full_name","birth_date","gender","blood_type",
                    "phone","address","allergies"]
            self._open_form(dict(zip(keys, row)))

    def _delete(self):
        if not self.selected_patient_id:
            messagebox.showwarning("No Selection", "Click a patient first.")
            return
        if messagebox.askyesno("Confirm",
                f"Delete patient #{self.selected_patient_id}? This cannot be undone."):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE id=?",
                (self.selected_patient_id,))
            conn.commit()
            conn.close()
            self.selected_patient_id = None
            self.profile_name.configure(text="Select a patient")
            self.profile_id.configure(text="")
            for lbl in self.info_labels.values():
                lbl.configure(text="—", fg=self.colors["text"])
            self.load_patients()