from pathlib import Path
import sqlite3
import time 

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

    cursor = connection.execute(
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

    inserted = cursor.rowcount == 1

    connection.close()

    return inserted


def get_playtime_stats():
    connection = sqlite3.connect(DATABASE_PATH)

    total_result = connection.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(game_duration_seconds), 0),
            MAX(game_start_timestamp)
        FROM matches
        """
    )

    total_matches, total_seconds, last_played_timestamp = total_result.fetchone()

    fourteen_days_ago_ms = int((time.time() - 14 * 24 * 60 * 60) * 1000)

    recent_result = connection.execute(
        """
        SELECT COALESCE(SUM(game_duration_seconds), 0)
        FROM matches
        WHERE game_start_timestamp >= ?
        """,
        (fourteen_days_ago_ms,),
    )

    last_14_days_seconds = recent_result.fetchone()[0]

    connection.close()

    return {
        "total_matches": total_matches,
        "total_seconds": total_seconds,
        "last_14_days_seconds": last_14_days_seconds,
        "last_played_timestamp": last_played_timestamp,
    }


def match_exists(match_id):
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute(
        """
        SELECT 1 FROM matches
        WHERE match_id = ?
        """,
        (match_id,),
    )

    exists = result.fetchone() is not None

    connection.close()

    return exists