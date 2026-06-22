import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import database


class CertificatesScreen(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg"])
        self.colors = colors
        self.selected_id = None
        self._build_topbar()
        self._build_body()
        self.load_certificates()

    def _build_topbar(self):
        c = self.colors
        topbar = tk.Frame(self, bg=c["surface"], pady=12)
        topbar.pack(fill="x")
        tk.Label(topbar, text="📄  Certificates",
            bg=c["surface"], fg=c["text"],
            font=("Courier", 18, "bold")).pack(side="left", padx=20)
        tk.Button(topbar, text="＋  Issue Certificate",
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

        cols = ("id","patient","doctor","type","date","signed")
        self.tree = ttk.Treeview(body, columns=cols,
            show="headings", selectmode="browse")

        for col, label, width in [
            ("id","ID",40), ("patient","Patient",180),
            ("doctor","Doctor",160), ("type","Type",150),
            ("date","Date",100), ("signed","Signed By",150)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("patient", anchor="w")

        sb = ttk.Scrollbar(body, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_row = tk.Frame(self, bg=c["bg"])
        btn_row.pack(fill="x", padx=16, pady=8)

        tk.Button(btn_row, text="🖨️  Print / Export",
            bg=c["accent2"], fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", padx=12, pady=6,
            cursor="hand2", command=self._print_cert
        ).pack(side="left", padx=(0, 8))

        tk.Button(btn_row, text="🗑  Delete",
            bg=c["accent4"], fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", padx=12, pady=6,
            cursor="hand2", command=self._delete
        ).pack(side="left")

    def load_certificates(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, p.full_name, d.full_name,
                   c.cert_type, c.issued_date, c.signed_by
            FROM certificates c
            JOIN patients p ON c.patient_id = p.id
            JOIN doctors  d ON c.doctor_id  = d.id
            ORDER BY c.issued_date DESC
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row)
        conn.close()

    def _on_select(self, event):
        s = self.tree.focus()
        if s:
            self.selected_id = int(s)

    def _open_form(self):
        c = self.colors
        form = tk.Toplevel(self)
        form.title("Issue Certificate")
        form.geometry("480x500")
        form.configure(bg=c["bg"])
        form.grab_set()

        tk.Label(form, text="📄  Issue Certificate",
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
                    width=32, height=5,
                    insertbackground=c["accent"])
                w.grid(row=row, column=1, padx=12, pady=4)
                entries[key] = w
                return var
            else:
                w = tk.Entry(ff, textvariable=var,
                    bg=c["surface2"], fg=c["text"],
                    font=("Courier", 11), relief="flat",
                    insertbackground=c["accent"], width=32)
                w.grid(row=row, column=1, padx=12, pady=4, ipady=5)
            entries[key] = var
            return var

        patient_var = field("Patient *",     "patient",   0, patient_options)
        doctor_var  = field("Doctor *",      "doctor",    1, doctor_options)
        type_var    = field("Certificate *", "cert_type", 2, [
            "Exit Certificate", "Sick Leave",
            "Fit-to-Work", "Medical Report",
            "Hospitalization", "Death Certificate"
        ])
        signed_var  = field("Signed By",     "signed_by", 3)
        content_var = field("Content/Notes", "content",   4, big=True)

        tk.Frame(form, bg=c["border"], height=1).pack(fill="x")
        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(pady=14)

        def save():
            pat_str  = patient_var.get()
            doc_str  = doctor_var.get()
            cert_type = type_var.get().strip()
            signed   = signed_var.get().strip()
            content_w = entries.get("content")
            content  = content_w.get("1.0","end").strip() if isinstance(content_w, tk.Text) else ""

            if not pat_str or not doc_str or not cert_type:
                messagebox.showwarning("Missing", "Patient, Doctor and Type required.", parent=form)
                return

            try:
                patient_id = int(pat_str.split("—")[0].strip())
                doctor_id  = int(doc_str.split("—")[0].strip())
            except:
                messagebox.showwarning("Error", "Invalid selection.", parent=form)
                return

            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO certificates
                (patient_id, doctor_id, cert_type, issued_date, content, signed_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (patient_id, doctor_id, cert_type,
                  str(date.today()), content, signed))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_certificates()

        tk.Button(btn_row, text="Cancel",
            bg=c["surface2"], fg=c["text"],
            font=("Courier", 11), relief="flat",
            padx=16, pady=7, cursor="hand2",
            command=form.destroy).pack(side="left", padx=8)
        tk.Button(btn_row, text="💾  Issue",
            bg=c["accent"], fg="#000",
            font=("Courier", 11, "bold"),
            relief="flat", padx=16, pady=7,
            cursor="hand2", command=save).pack(side="left", padx=8)

    def _print_cert(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click a certificate first.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.cert_type, c.issued_date, c.content,
                   c.signed_by, p.full_name, p.birth_date,
                   p.gender, d.full_name, d.specialty
            FROM certificates c
            JOIN patients p ON c.patient_id = p.id
            JOIN doctors  d ON c.doctor_id  = d.id
            WHERE c.id = ?
        """, (self.selected_id,))
        cert = cursor.fetchone()
        conn.close()

        if not cert:
            return

        cert_type, issued, content, signed, patient, birth, gender, doctor, specialty = cert

        # Try PDF export with reportlab
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.pdfgen import canvas as rl_canvas
            from tkinter import filedialog

            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF","*.pdf")],
                initialfile=f"certificate_{self.selected_id}.pdf"
            )
            if not path:
                return

            c = rl_canvas.Canvas(path, pagesize=A4)
            w, h = A4

            # Header
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(w/2, h - 3*cm, "🏥 MediCore Hospital")
            c.setFont("Helvetica", 12)
            c.drawCentredString(w/2, h - 4*cm, cert_type.upper())
            c.line(2*cm, h - 4.5*cm, w - 2*cm, h - 4.5*cm)

            # Body
            c.setFont("Helvetica", 11)
            y = h - 6*cm
            for line in [
                f"Patient Name : {patient}",
                f"Date of Birth : {birth}",
                f"Gender        : {gender}",
                f"Issued Date   : {issued}",
                f"Doctor        : {doctor} ({specialty})",
                f"Signed By     : {signed or doctor}",
                "",
                "Notes / Content:",
            ]:
                c.drawString(2.5*cm, y, line)
                y -= 0.7*cm

            # Content text
            c.setFont("Helvetica", 10)
            for line in (content or "").split("\n"):
                c.drawString(2.5*cm, y, line)
                y -= 0.6*cm

            # Footer
            c.line(2*cm, 3*cm, w - 2*cm, 3*cm)
            c.setFont("Helvetica-Oblique", 9)
            c.drawCentredString(w/2, 2.5*cm, "This document is issued by MediCore Hospital Management System")
            c.drawCentredString(w/2, 2*cm, f"Generated on {date.today()}")

            c.save()
            messagebox.showinfo("Exported", f"Certificate saved to:\n{path}")

        except ImportError:
            # Fallback — show in a text window
            win = tk.Toplevel(self)
            win.title(f"Certificate #{self.selected_id}")
            win.geometry("500x500")
            win.configure(bg=self.colors["bg"])

            tk.Label(win, text=f"📄 {cert_type}",
                bg=self.colors["bg"], fg=self.colors["accent"],
                font=("Courier", 14, "bold")).pack(pady=12)

            txt = tk.Text(win,
                bg=self.colors["surface"], fg=self.colors["text"],
                font=("Courier", 11), relief="flat", padx=16, pady=12)
            txt.pack(fill="both", expand=True, padx=16, pady=8)

            txt.insert("end", f"CERTIFICATE TYPE : {cert_type}\n")
            txt.insert("end", f"ISSUED DATE      : {issued}\n")
            txt.insert("end", f"PATIENT          : {patient}\n")
            txt.insert("end", f"DATE OF BIRTH    : {birth}\n")
            txt.insert("end", f"GENDER           : {gender}\n")
            txt.insert("end", f"DOCTOR           : {doctor} ({specialty})\n")
            txt.insert("end", f"SIGNED BY        : {signed or doctor}\n")
            txt.insert("end", f"\nNOTES:\n{content or ''}\n")
            txt.configure(state="disabled")

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Click a certificate first.")
            return
        if messagebox.askyesno("Confirm", "Delete this certificate?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM certificates WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.selected_id = None
            self.load_certificates()