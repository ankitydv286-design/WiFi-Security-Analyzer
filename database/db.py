
import sqlite3
from config import DATABASE_PATH


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")

    return connection


def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            hostname TEXT,
            mac_address TEXT,
            first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ip_address, mac_address)
        );

        CREATE TABLE IF NOT EXISTS monitoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            latency_ms REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            severity TEXT,
            title TEXT,
            description TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_monitoring_timestamp
        ON monitoring(timestamp);

        CREATE INDEX IF NOT EXISTS idx_security_logs_timestamp
        ON security_logs(timestamp);

        CREATE INDEX IF NOT EXISTS idx_devices_ip
        ON devices(ip_address);
        """)


def save_devices(devices):
    with get_connection() as conn:
        for device in devices:
            conn.execute("""
                INSERT INTO devices (
                    ip_address, hostname, mac_address
                )
                VALUES (?, ?, ?)
                ON CONFLICT(ip_address, mac_address)
                DO UPDATE SET
                    hostname = excluded.hostname,
                    last_seen = CURRENT_TIMESTAMP
            """, (
                device["ip_address"],
                device["hostname"],
                device["mac_address"]
            ))


def save_monitoring(status):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO monitoring (status, latency_ms)
            VALUES (?, ?)
        """, (
            status["status"],
            status["latency_ms"]
        ))


def save_security_alerts(alerts):
    with get_connection() as conn:
        for alert in alerts:
            conn.execute("""
                INSERT INTO security_logs (
                    severity, title, description
                )
                SELECT ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM security_logs
                    WHERE title = ?
                    AND description = ?
                    AND timestamp >= datetime('now', '-1 hour')
                )
            """, (
                alert["severity"],
                alert["title"],
                alert["description"],
                alert["title"],
                alert["description"]
            ))


def get_recent_logs(limit=10):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT severity, title, description, timestamp
            FROM security_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]
