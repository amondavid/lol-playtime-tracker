from pathlib import Path
import sqlite3

DATABASE_PATH = Path("data/lol-playtime.db")


def init_db():
    DATABASE_PATH.parent.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()

def save_setting(key, value):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute(
        """
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
        """,
        (key, value)
    )   
    
    connection.commit()
    connection.close()