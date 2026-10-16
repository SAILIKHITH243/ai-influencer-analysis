
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "influencer_history.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS channel_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                channel_name TEXT,
                recorded_at TEXT NOT NULL,
                subscriber_count INTEGER,
                total_channel_views INTEGER,
                total_channel_videos INTEGER,
                average_matched_video_views REAL,
                public_interactions_per_view_pct REAL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_channel_snapshots_channel_time
            ON channel_snapshots(channel_id, recorded_at)
        """)


def save_channel_snapshot(channel):
    """Save one timestamped snapshot of available public statistics."""

    def optional_number(key):
        value = channel.get(key)

        if value is None:
            return None

        try:
            if value != value:  # Handles NaN
                return None
        except TypeError:
            pass

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    channel_id = str(channel.get("channel_id", "")).strip()

    if not channel_id:
        raise ValueError("Channel ID is required to save a snapshot.")

    recorded_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO channel_snapshots (
                channel_id,
                channel_name,
                recorded_at,
                subscriber_count,
                total_channel_views,
                total_channel_videos,
                average_matched_video_views,
                public_interactions_per_view_pct
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            channel_id,
            channel.get("channel_name"),
            recorded_at,
            optional_number("subscriber_count"),
            optional_number("total_channel_views"),
            optional_number("total_channel_videos"),
            optional_number("average_matched_video_views"),
            optional_number("public_interactions_per_view_pct"),
        ))


def get_channel_history(channel_id):
    """Return saved snapshots for one channel, oldest first."""

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM channel_snapshots
            WHERE channel_id = ?
            ORDER BY recorded_at ASC
        """, (str(channel_id),)).fetchall()

    return [dict(row) for row in rows]
