import tkinter as tk
from tkinter import ttk, messagebox
import database


class AppointmentsScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self.selected_id = None
        self._build_topbar()
        self._build_body()
        self.load_appointments()

    def _build_topbar(self):
        c = self.colors
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="📅  Appointments",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Button(topbar, text="＋  New Appointment",
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

        cols = ("id","patient","doctor","date","time","reason","status")
        self.tree = ttk.Treeview(body, columns=cols,
            show="headings", selectmode="browse")

        for col, label, width in [
            ("id","ID",40), ("patient","Patient",160),
            ("doctor","Doctor",160), ("date","Date",100),
            ("time","Time",80), ("reason","Reason",160),
            ("status","Status",100)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("patient", anchor="w")
        self.tree.column("doctor", anchor="w")
        self.tree.column("reason", anchor="w")

        sb = ttk.Scrollbar(body, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_row = tk.Frame(self, bg=c["bg"])
        btn_row.pack(fill="x", padx=16, pady=8)

        for text, color, cmd in [
            ("✏️  Edit",    c["accent2"], self._edit),
            ("✅  Mark Done", c["accent"], self._mark_done),
            ("❌  Cancel",  c["accent3"], self._cancel_appt),
            ("🗑  Delete",  c["accent4"], self._delete),
        ]:
            tk.Button(btn_row, text=text,
                bg=color, fg="white" if color != c["accent"] else "#000",
                font=("Courier", 10, "bold"),
                relief="flat", padx=12, pady=6,
                cursor="hand2", command=cmd
            ).pack(side="left", padx=(0, 8))

    def load_appointments(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, p.full_name, d.full_name,
                   a.appt_date, a.appt_time, a.reason, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors  d ON a.doctor_id  = d.id
            ORDER BY a.appt_date DESC, a.appt_time DESC
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
        form.title("Edit Appointment" if is_edit else "New Appointment")
        form.geometry("440x420")
        form.configure(bg=c["bg"])
        form.grab_set()

        tk.Label(form,
            text="✏️  Edit" if is_edit else "📅  New Appointment",
            bg=c["bg"], fg=c["accent"],
            font=("Courier", 15, "bold")).pack(pady=16)
        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")

        ff = tk.Frame(form, bg=c["bg"])
        ff.pack(fill="both", expand=True, padx=24, pady=16)

        # Load patients and doctors for dropdowns
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

        def field(label, key, row, options=None):
            tk.Label(ff, text=label,
                bg=c["bg"], fg=c["muted"],
                font=("Courier", 9)).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            if options is not None:
                w = ttk.Combobox(ff, textvariable=var,
                    values=options, font=("Courier", 11), width=26)
            else:
                w = tk.Entry(ff, textvariable=var,
                    bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    insertbackground=c["accent"], width=28)
            w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            entries[key] = var
            if is_edit and key in data:
                var.set(data[key])
            return var

        patient_var = field("Patient *",   "patient", 0, patient_options)
        doctor_var  = field("Doctor *",    "doctor",  1, doctor_options)
        date_var    = field("Date * (YYYY-MM-DD)", "appt_date", 2)
        time_var    = field("Time * (HH:MM)",      "appt_time", 3)
        reason_var  = field("Reason",      "reason",  4)
        status_var  = field("Status",      "status",  5,
            ["Scheduled","In Progress","Done","Cancelled"])

        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")
        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(pady=14)

        def save():
            pat_str = patient_var.get()
            doc_str = doctor_var.get()
            date    = date_var.get().strip()
            time    = time_var.get().strip()
            reason  = reason_var.get().strip()
            status  = status_var.get().strip() or "Scheduled"

            if not pat_str or not doc_str or not date or not time:
                messagebox.showwarning("Missing", "Patient, Doctor, Date and Time required.", parent=form)
                return

            try:
                patient_id = int(pat_str.split("—")[0].strip())
                doctor_id  = int(doc_str.split("—")[0].strip())
            except:
                messagebox.showwarning("Error", "Invalid patient or doctor selection.", parent=form)
                return

            conn = database.get_connection()
            cursor = conn.cursor()
            if is_edit:
                cursor.execute("""
                    UPDATE appointments
                    SET patient_id=?, doctor_id=?, appt_date=?,
                        appt_time=?, reason=?, status=?
                    WHERE id=?
                """, (patient_id, doctor_id, date, time, reason, status, self.selected_id))
            else:
                cursor.execute("""
                    INSERT INTO appointments
                    (patient_id, doctor_id, appt_date, appt_time, reason, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, doctor_id, date, time, reason, status))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_appointments()

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

    def _update_status(self, status):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click an appointment first.")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status=? WHERE id=?",
            (status, self.selected_id))
        conn.commit()
        conn.close()
        self.load_appointments()

    def _mark_done(self):   self._update_status("Done")
    def _cancel_appt(self): self._update_status("Cancelled")

    def _edit(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click an appointment first.")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_id, doctor_id, appt_date, appt_time, reason, status
            FROM appointments WHERE id=?
        """, (self.selected_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            keys = ["patient","doctor","appt_date","appt_time","reason","status"]
            self._open_form(dict(zip(keys, row)))

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click an appointment first.")
            return
        if messagebox.askyesno("Confirm", "Delete this appointment?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.selected_id = None
            self.load_appointments()