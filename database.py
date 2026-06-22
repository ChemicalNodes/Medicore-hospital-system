import db_connector


def get_connection():
    return db_connector.get_connection()


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name  TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            gender     TEXT NOT NULL,
            phone      TEXT,
            address    TEXT,
            blood_type TEXT,
            allergies  TEXT,
            doctor_id  INTEGER,
            created_at TEXT DEFAULT (date('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT NOT NULL,
            specialty     TEXT NOT NULL,
            phone         TEXT,
            email         TEXT,
            schedule_days TEXT,
            hire_date     TEXT DEFAULT (date('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id  INTEGER NOT NULL,
            appt_date  TEXT NOT NULL,
            appt_time  TEXT NOT NULL,
            reason     TEXT,
            status     TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            doctor_id   INTEGER NOT NULL,
            visit_date  TEXT DEFAULT (date('now')),
            diagnosis   TEXT NOT NULL,
            notes       TEXT,
            record_type TEXT DEFAULT 'Consultation',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id       INTEGER NOT NULL,
            patient_id      INTEGER NOT NULL,
            medication_name TEXT NOT NULL,
            dosage          TEXT NOT NULL,
            frequency       TEXT,
            duration        TEXT,
            instructions    TEXT,
            FOREIGN KEY (record_id)  REFERENCES medical_records(id),
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            doctor_id   INTEGER NOT NULL,
            cert_type   TEXT NOT NULL,
            issued_date TEXT DEFAULT (date('now')),
            content     TEXT,
            signed_by   TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
        )
    """)

    conn.commit()
    conn.close()


def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    cursor.executemany("""
        INSERT INTO doctors (full_name, specialty, phone, email, schedule_days)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ("Dr. Hamid Rezai",   "Cardiology",       "0555001001", "hamid@medicore.dz",  "Mon-Fri"),
        ("Dr. Samir Ait",     "General Medicine", "0555001002", "samir@medicore.dz",  "Mon-Sat"),
        ("Dr. Leila Bouazza", "Pediatrics",       "0555001003", "leila@medicore.dz",  "Sun-Thu"),
    ])

    cursor.executemany("""
        INSERT INTO patients
        (full_name, birth_date, gender, blood_type, phone, address, allergies, doctor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("Karim Benali",   "1984-03-14", "Male",   "A+",  "0555101001", "Algiers", "Penicillin", 1),
        ("Fatima Zohra",   "1997-07-22", "Female", "O-",  "0555101002", "Oran",    "",            2),
        ("Ahmed Mansouri", "1969-11-05", "Male",   "B+",  "0555101003", "Algiers", "Aspirin",     1),
        ("Sara Khelif",    "1992-01-30", "Female", "AB+", "0555101004", "Annaba",  "",            3),
        ("Omar Tlemcani",  "1963-06-18", "Male",   "A-",  "0555101005", "Algiers", "Ibuprofen",   2),
    ])

    conn.commit()
    conn.close()