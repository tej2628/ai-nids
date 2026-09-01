import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from config import DATABASE_PATH
from src.utils import logger


@contextmanager
def connection(db_path=DATABASE_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        logger.exception("Database operation failed")
        raise
    finally:
        conn.close()


def init_database(db_path=DATABASE_PATH):
    with connection(db_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL, destination_ip TEXT NOT NULL, protocol TEXT NOT NULL,
            source_port INTEGER, destination_port INTEGER, prediction TEXT NOT NULL,
            attack_type TEXT, confidence REAL NOT NULL, risk_level TEXT NOT NULL, mode TEXT NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_detections_prediction ON detections(prediction)")


def insert_detection(event, db_path=DATABASE_PATH):
    fields = ("timestamp", "source_ip", "destination_ip", "protocol", "source_port", "destination_port", "prediction", "attack_type", "confidence", "risk_level", "mode")
    values = [event.get(field) for field in fields]
    values[0] = values[0] or datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connection(db_path) as conn:
        cursor = conn.execute(f"INSERT INTO detections ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})", values)
        return cursor.lastrowid


def get_recent_detections(limit=50, search="", prediction="", db_path=DATABASE_PATH):
    limit = max(1, min(int(limit), 250))
    query, params = "SELECT * FROM detections WHERE 1=1", []
    if search:
        query += " AND (source_ip LIKE ? OR destination_ip LIKE ? OR attack_type LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    if prediction in ("NORMAL", "ATTACK"):
        query += " AND prediction = ?"; params.append(prediction)
    query += " ORDER BY timestamp DESC LIMIT ?"; params.append(limit)
    with connection(db_path) as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_stats(db_path=DATABASE_PATH):
    with connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) total, SUM(prediction='NORMAL') normal, SUM(prediction='ATTACK') attacks, SUM(risk_level IN ('HIGH','CRITICAL')) high_risk FROM detections").fetchone()
        attacks = conn.execute("SELECT COALESCE(attack_type,'Unknown') name, COUNT(*) value FROM detections WHERE prediction='ATTACK' GROUP BY attack_type ORDER BY value DESC").fetchall()
        trend = conn.execute("SELECT substr(timestamp,1,13) hour, COUNT(*) value FROM detections GROUP BY hour ORDER BY hour DESC LIMIT 12").fetchall()
    return {"total": row["total"] or 0, "normal": row["normal"] or 0, "attacks": row["attacks"] or 0, "high_risk": row["high_risk"] or 0, "attack_types": [dict(x) for x in attacks], "trend": list(reversed([dict(x) for x in trend]))}


def clear_detections(db_path=DATABASE_PATH):
    with connection(db_path) as conn:
        conn.execute("DELETE FROM detections")
