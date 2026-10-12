import sqlite3
import os

DB_PATH = "telemetry_drop.db"

def init_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
    """)

    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'Ecl!pse_Uncrackable_Adm1n_Key_2026', 'administrator');
    """)

    conn.commit()
    conn.close()
    print("[*] Database initialized with administrator account.")

if __name__ == "__main__":
    init_database()