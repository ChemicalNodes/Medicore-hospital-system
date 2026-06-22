import tkinter as tk
from tkinter import ttk, messagebox
import database


class PrescriptionsScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self.selected_id = None
        self._build_topbar()
        self._build_body()
        self.load_prescriptions()

    def _build_topbar(self):
        c = self.colors
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="💊  Prescriptions",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Button(topbar, text="＋  New Prescription",
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

        cols = ("id","patient","medication","dosage","frequency","duration")
        self.tree = ttk.Treeview(body, columns=cols,
            show="headings", selectmode="browse")

        for col, label, width in [
            ("id","ID",40), ("patient","Patient",180),
            ("medication","Medication",180), ("dosage","Dosage",100),
            ("frequency","Frequency",120), ("duration","Duration",100)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("patient", anchor="w")
        self.tree.column("medication", anchor="w")

        sb = ttk.Scrollbar(body, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_row = tk.Frame(self, bg=c["bg"])
        btn_row.pack(fill="x", padx=16, pady=8)
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

    def load_prescriptions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.id, p.full_name,
                   pr.medication_name, pr.dosage,
                   pr.frequency, pr.duration
            FROM prescriptions pr
            JOIN patients p ON pr.patient_id = p.id
            ORDER BY pr.id DESC
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row)
        conn.close()

    def _on_select(self, event):
        s = self.tree.focus()
        if s:
            self.selected_id = int(s)

    def _open_form(self, data=None):
        c = self.colors
        is_edit = data is not None
        form = tk.Toplevel(self)
        form.title("Edit Prescription" if is_edit else "New Prescription")
        form.geometry("440x460")
        form.configure(bg=c["bg"])
        form.grab_set()

        tk.Label(form,
            text="✏️  Edit" if is_edit else "💊  New Prescription",
            bg=c["bg"], fg=c["accent"],
            font=("Courier", 15, "bold")).pack(pady=16)
        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")

        ff = tk.Frame(form, bg=c["bg"])
        ff.pack(fill="both", expand=True, padx=24, pady=16)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM patients ORDER BY full_name")
        patients = cursor.fetchall()
        cursor.execute("SELECT id, diagnosis FROM medical_records ORDER BY id DESC")
        records = cursor.fetchall()
        conn.close()

        patient_options = [f"{p[0]} — {p[1]}" for p in patients]
        record_options  = [f"{r[0]} — {r[1]}" for r in records]

        entries = {}

        def field(label, key, row, options=None):
            tk.Label(ff, text=label,
                bg=c["bg"], fg=c["muted"],
                font=("Courier", 9)).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            if options is not None:
                w = ttk.Combobox(ff, textvariable=var,
                    values=options, font=("Courier", 11), width=28)
            else:
                w = tk.Entry(ff, textvariable=var,
                    bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    insertbackground=c["accent"], width=30)
            w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            entries[key] = var
            if is_edit and key in data:
                var.set(data[key])
            return var

        patient_var = field("Patient *",      "patient",         0, patient_options)
        record_var  = field("Medical Record", "record",          1, record_options)
        med_var     = field("Medication *",   "medication_name", 2)
        dose_var    = field("Dosage *",       "dosage",          3)
        freq_var    = field("Frequency",      "frequency",       4,
            ["Once daily","Twice daily","3x daily","Every 8h","Every 12h","As needed"])
        dur_var     = field("Duration",       "duration",        5,
            ["3 days","5 days","7 days","10 days","14 days","30 days","90 days"])
        instr_var   = field("Instructions",   "instructions",    6)

        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")
        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(pady=14)

        def save():
            pat_str = patient_var.get()
            rec_str = record_var.get()
            med     = med_var.get().strip()
            dose    = dose_var.get().strip()
            freq    = freq_var.get().strip()
            dur     = dur_var.get().strip()
            instr   = instr_var.get().strip()

            if not pat_str or not med or not dose:
                messagebox.showwarning("Missing", "Patient, Medication and Dosage required.", parent=form)
                return

            try:
                patient_id = int(pat_str.split("—")[0].strip())
            except:
                messagebox.showwarning("Error", "Invalid patient.", parent=form)
                return

            record_id = 1
            if rec_str:
                try:
                    record_id = int(rec_str.split("—")[0].strip())
                except:
                    pass

            conn = database.get_connection()
            cursor = conn.cursor()
            if is_edit:
                cursor.execute("""
                    UPDATE prescriptions
                    SET patient_id=?, record_id=?, medication_name=?,
                        dosage=?, frequency=?, duration=?, instructions=?
                    WHERE id=?
                """, (patient_id, record_id, med, dose, freq, dur, instr, self.selected_id))
            else:
                cursor.execute("""
                    INSERT INTO prescriptions
                    (patient_id, record_id, medication_name, dosage, frequency, duration, instructions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (patient_id, record_id, med, dose, freq, dur, instr))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_prescriptions()

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
            messagebox.showwarning("No Selection", "Click a prescription first.")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_id, record_id, medication_name,
                   dosage, frequency, duration, instructions
            FROM prescriptions WHERE id=?
        """, (self.selected_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            keys = ["patient","record","medication_name","dosage","frequency","duration","instructions"]
            self._open_form(dict(zip(keys, row)))

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click a prescription first.")
            return
        if messagebox.askyesno("Confirm", "Delete this prescription?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prescriptions WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.selected_id = None
            self.load_prescriptions()