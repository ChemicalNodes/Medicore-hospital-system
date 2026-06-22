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

   

    else:
        raise Exception("No database connected. Please login first.")


def is_connected():
    return _config["type"] is not None


 