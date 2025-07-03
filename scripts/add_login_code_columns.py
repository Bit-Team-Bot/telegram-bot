import sqlite3
from pathlib import Path

# Pfad zur zentralen Datenbankdatei
DB_PATH = str(Path(__file__).resolve().parent.parent / "telegram_bot.db")

# Zu prüfende und ggf. hinzuzufügende Spalten
COLUMNS = [
    ("login_code", "TEXT"),
    ("login_code_expires_at", "DATETIME")
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for col, coltype in COLUMNS:
        if not column_exists(cursor, "users", col):
            print(f"Füge Spalte '{col}' hinzu...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {coltype}")
        else:
            print(f"Spalte '{col}' existiert bereits.")
    conn.commit()
    cursor.close()
    conn.close()
    print("Fertig.")

if __name__ == "__main__":
    main() 