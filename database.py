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

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            match_id TEXT PRIMARY KEY,
            game_start_timestamp INTEGER NOT NULL,
            game_duration_seconds INTEGER NOT NULL,
            queue_id INTEGER NOT NULL
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


def get_setting(key):
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute(
        """
        SELECT value FROM settings
        WHERE key = ?
        """,
        (key,)
    )

    row = result.fetchone()
    connection.close()

    if row is None:
        return None
    
    return row[0]



def save_match(match_id, game_start_timestamp, game_duration_seconds, queue_id):
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute(
        """
        INSERT OR IGNORE INTO matches (
            match_id,
            game_start_timestamp,
            game_duration_seconds,
            queue_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            match_id,
            game_start_timestamp,
            game_duration_seconds,
            queue_id,
        ),
    )

    connection.commit()
    connection.close()
