import tkinter as tk
from tkinter import ttk, messagebox
import database


class RecordsScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self.selected_id = None
        self._build_topbar()
        self._build_body()
        self.load_records()

    def _build_topbar(self):
        c = self.colors
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="📋  Medical Records",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Button(topbar, text="＋  Add Record",
            bg=c["accent"], fg="#000",
            font=("Courier", 11, "bold"),
            relief="flat", padx=14, pady=6,
            cursor="hand2", command=self._open_form
        ).pack(side="right", padx=20)
        tk.Frame(self, bg=c["border"], height=1).pack(fill="x")

    def _build_body(self):
        c = self.colors

        # Search
        sf = tk.Frame(self, bg=c["bg"], pady=10)
        sf.pack(fill="x", padx=16)
        tk.Label(sf, text="🔍  Search:",
            bg=c["bg"], fg=c["muted"],
            font=("Courier", 11)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_records())
        tk.Entry(sf, textvariable=self.search_var,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 11), relief="flat",
            insertbackground=c["accent"], width=30
        ).pack(side="left", padx=10, ipady=5)

        body = tk.Frame(self, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=8)

        left = tk.Frame(body, bg=c["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg=c["surface"], width=280)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        self._build_table(left)
        self._build_detail(right)

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

        cols = ("id","patient","doctor","date","diagnosis","type")
        self.tree = ttk.Treeview(frame, columns=cols,
            show="headings", selectmode="browse",
            yscrollcommand=sb.set)

        for col, label, width in [
            ("id","ID",50), ("patient","Patient",170),
            ("doctor","Doctor",160), ("date","Date",100),
            ("diagnosis","Diagnosis",200), ("type","Type",120)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("patient", anchor="w")
        self.tree.column("diagnosis", anchor="w")

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

    def _build_detail(self, parent):
        c = self.colors

        tk.Label(parent, text="RECORD DETAIL",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(pady=(16, 4))

        tk.Label(parent, text="📋",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 36), width=3
        ).pack(pady=8)

        self.detail_title = tk.Label(parent,
            text="Select a record",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 11, "bold"), wraplength=240)
        self.detail_title.pack(pady=(4, 0))

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=10)

        self.detail_labels = {}
        for key, label in [
            ("patient",  "Patient"),
            ("doctor",   "Doctor"),
            ("date",     "Visit Date"),
            ("type",     "Record Type"),
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
            self.detail_labels[key] = val

        tk.Label(parent, text="Notes:",
            bg=c["surface"], fg=c["muted"],
            font=("Courier", 9)).pack(anchor="w", padx=12, pady=(10, 2))

        self.notes_text = tk.Text(parent,
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 9), relief="flat",
            height=6, wrap="word",
            state="disabled")
        self.notes_text.pack(fill="x", padx=12, pady=(0, 8))

    def load_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_var.get().strip()
        conn = database.get_connection()
        cursor = conn.cursor()

        if search:
            cursor.execute("""
                SELECT r.id, p.full_name, d.full_name,
                       r.visit_date, r.diagnosis, r.record_type
                FROM medical_records r
                JOIN patients p ON r.patient_id = p.id
                JOIN doctors  d ON r.doctor_id  = d.id
                WHERE p.full_name LIKE ? OR r.diagnosis LIKE ?
                ORDER BY r.visit_date DESC
            """, (f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""
                SELECT r.id, p.full_name, d.full_name,
                       r.visit_date, r.diagnosis, r.record_type
                FROM medical_records r
                JOIN patients p ON r.patient_id = p.id
                JOIN doctors  d ON r.doctor_id  = d.id
                ORDER BY r.visit_date DESC
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
            SELECT r.diagnosis, r.notes, r.visit_date, r.record_type,
                   p.full_name, d.full_name
            FROM medical_records r
            JOIN patients p ON r.patient_id = p.id
            JOIN doctors  d ON r.doctor_id  = d.id
            WHERE r.id = ?
        """, (self.selected_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        diag, notes, visit_date, rtype, patient, doctor = row
        self.detail_title.configure(text=diag)
        self.detail_labels["patient"].configure(text=patient)
        self.detail_labels["doctor"].configure(text=doctor)
        self.detail_labels["date"].configure(text=visit_date or "—")
        self.detail_labels["type"].configure(text=rtype or "—")

        self.notes_text.configure(state="normal")
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", notes or "No notes.")
        self.notes_text.configure(state="disabled")

    def _open_form(self, data=None):
        c = self.colors
        is_edit = data is not None

        form = tk.Toplevel(self)
        form.title("Edit Record" if is_edit else "New Medical Record")
        form.geometry("480x500")
        form.configure(bg=c["bg"])
        form.grab_set()

        tk.Label(form,
            text="✏️  Edit" if is_edit else "📋  New Medical Record",
            bg=c["bg"], fg=c["accent"],
            font=("Courier", 15, "bold")).pack(pady=16)
        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")

        ff = tk.Frame(form, bg=c["bg"])
        ff.pack(fill="both", expand=True, padx=24, pady=16)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM patients ORDER BY full_name")
        patients = cursor.fetchall()
        cursor.execute("SELECT id, full_name FROM doctors ORDER BY full_name")
        doctors = cursor.fetchall()
        conn.close()

        patient_options = [f"{p[0]} — {p[1]}" for p in patients]
        doctor_options  = [f"{d[0]} — {d[1]}" for d in doctors]

        entries = {}

        def field(label, key, row, options=None, big=False):
            tk.Label(ff, text=label,
                bg=c["bg"], fg=c["muted"],
                font=("Courier", 9)).grid(row=row, column=0, sticky="nw", pady=4)
            var = tk.StringVar()
            if options is not None:
                w = ttk.Combobox(ff, textvariable=var,
                    values=options, font=("Courier", 11), width=30)
                w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            elif big:
                w = tk.Text(ff, bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    width=32, height=4,
                    insertbackground=c["accent"])
                w.grid(row=row, column=1, padx=12, pady=4)
                entries[key] = w
                if is_edit and data and key in data:
                    w.insert("1.0", data[key])
                return var
            else:
                w = tk.Entry(ff, textvariable=var,
                    bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    insertbackground=c["accent"], width=32)
                w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            entries[key] = var
            if is_edit and data and key in data:
                var.set(data[key])
            return var

        patient_var = field("Patient *",       "patient",     0, patient_options)
        doctor_var  = field("Doctor *",        "doctor",      1, doctor_options)
        date_var    = field("Visit Date *",    "visit_date",  2)
        diag_var    = field("Diagnosis *",     "diagnosis",   3)
        type_var    = field("Type",            "record_type", 4, [
            "Consultation","Follow-up","Emergency","Surgery","Lab Result"])
        notes_var   = field("Notes",           "notes",       5, big=True)

        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")
        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(pady=14)

        def save():
            pat_str = patient_var.get()
            doc_str = doctor_var.get()
            vdate   = date_var.get().strip()
            diag    = diag_var.get().strip()
            rtype   = type_var.get().strip() or "Consultation"
            notes_w = entries.get("notes")
            notes   = notes_w.get("1.0","end").strip() if isinstance(notes_w, tk.Text) else ""

            if not pat_str or not doc_str or not vdate or not diag:
                messagebox.showwarning("Missing",
                    "Patient, Doctor, Date and Diagnosis required.", parent=form)
                return

            try:
                patient_id = int(pat_str.split("—")[0].strip())
                doctor_id  = int(doc_str.split("—")[0].strip())
            except:
                messagebox.showwarning("Error", "Invalid selection.", parent=form)
                return

            conn = database.get_connection()
            cursor = conn.cursor()
            if is_edit:
                cursor.execute("""
                    UPDATE medical_records SET patient_id=?, doctor_id=?,
                    visit_date=?, diagnosis=?, record_type=?, notes=?
                    WHERE id=?
                """, (patient_id, doctor_id, vdate, diag, rtype, notes, self.selected_id))
            else:
                cursor.execute("""
                    INSERT INTO medical_records
                    (patient_id, doctor_id, visit_date, diagnosis, record_type, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, doctor_id, vdate, diag, rtype, notes))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_records()
            messagebox.showinfo("Saved", "Record saved! ✅")

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
            messagebox.showwarning("No Selection", "Click a record first.")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_id, doctor_id, visit_date,
                   diagnosis, record_type, notes
            FROM medical_records WHERE id=?
        """, (self.selected_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            keys = ["patient","doctor","visit_date","diagnosis","record_type","notes"]
            self._open_form(dict(zip(keys, row)))

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click a record first.")
            return
        if messagebox.askyesno("Confirm", "Delete this record?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medical_records WHERE id=?",
                (self.selected_id,))
            conn.commit()
            conn.close()
            self.selected_id = None
            self.detail_title.configure(text="Select a record")
            for lbl in self.detail_labels.values():
                lbl.configure(text="—")
            self.load_records()