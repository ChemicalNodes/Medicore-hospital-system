import sqlite3
import os
import zipfile


_config = {
    "type": None,
    "connection": None,
    "odb_path": None,
}


def connect_sqlite(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()
        _config["type"] = "sqlite"
        _config["connection"] = db_path
        return True, "Connected to SQLite ✅"
    except Exception as e:
        return False, f"SQLite Error: {e}"


def connect_mysql(host, port, dbname, user, password):
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=host, port=int(port),
            database=dbname, user=user, password=password
        )
        conn.close()
        _config["type"] = "mysql"
        _config["connection"] = {
            "host": host, "port": port,
            "database": dbname,
            "user": user, "password": password
        }
        return True, "Connected to MySQL ✅"
    except Exception as e:
        return False, f"MySQL Error: {e}"


def connect_libreoffice(odb_path):
    try:
        if not os.path.exists(odb_path):
            return False, "File not found."
        if not odb_path.endswith(".odb"):
            return False, "Not a valid .odb file."
        with zipfile.ZipFile(odb_path, "r") as z:
            if "content.xml" not in z.namelist():
                return False, "Invalid .odb file."
        _config["type"] = "libreoffice"
        _config["odb_path"] = odb_path
        _config["connection"] = odb_path
        return True, "Connected to LibreOffice Base ✅"
    except Exception as e:
        return False, f"LibreOffice Error: {e}"


def get_connection():
    db_type = _config["type"]

    if db_type == "sqlite":
        conn = sqlite3.connect(_config["connection"])
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    elif db_type == "mysql":
        import mysql.connector
        cfg = _config["connection"]
        return mysql.connector.connect(
            host=cfg["host"], port=cfg["port"],
            database=cfg["database"],
            user=cfg["user"], password=cfg["password"]
        )

    elif db_type == "libreoffice":
        odb_path = _config["odb_path"]
        extract_dir = odb_path + "_extracted"
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(odb_path, "r") as z:
            z.extractall(extract_dir)
        db_file = os.path.join(extract_dir, "database", "db")
        if os.path.exists(db_file):
            return sqlite3.connect(db_file)
        return sqlite3.connect(os.path.join(extract_dir, "medicore.db"))

    else:
        raise Exception("No database connected. Please login first.")


def is_connected():
    return _config["type"] is not None


def save_libreoffice():
    if _config["type"] != "libreoffice":
        return
    odb_path = _config["odb_path"]
    extract_dir = odb_path + "_extracted"
    with zipfile.ZipFile(odb_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, extract_dir)
                z.write(full_path, arcname)