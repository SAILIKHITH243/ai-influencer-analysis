"""SQLite persistence for creator snapshots and saved shortlist entries."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "influencer_history.db"

NUMERIC_FIELDS = (
    "subscriber_count",
    "total_channel_views",
    "total_channel_videos",
    "average_matched_video_views",
    "median_matched_video_views",
    "matched_video_count",
    "recent_matched_videos_30d",
    "recent_matched_videos_90d",
    "public_interactions_per_view_pct",
    "content_match_pct",
    "performance_score",
    "performance_view_score",
    "performance_engagement_score",
    "performance_subscriber_score",
    "suitability_score",
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _number(value):
    """Convert numeric values safely, including pandas missing values."""
    if value is None:
        return None

    try:
        if value != value:
            return None
    except (TypeError, ValueError):
        pass

    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return None


def initialize_database():
    """Create tables and migrate additional columns when needed."""
    with get_connection() as connection:
        connection.execute(
            """
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
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_channel_snapshots_channel_time
            ON channel_snapshots(channel_id, recorded_at)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS creator_shortlist (
                channel_id TEXT PRIMARY KEY,
                channel_name TEXT,
                channel_url TEXT,
                thumbnail_url TEXT,
                description TEXT,
                published_at TEXT,
                subscriber_count REAL,
                total_channel_views REAL,
                total_channel_videos REAL,
                average_matched_video_views REAL,
                median_matched_video_views REAL,
                matched_video_count REAL,
                recent_matched_videos_30d REAL,
                recent_matched_videos_90d REAL,
                public_interactions_per_view_pct REAL,
                content_match_pct REAL,
                performance_score REAL,
                performance_view_score REAL,
                performance_engagement_score REAL,
                performance_subscriber_score REAL,
                suitability_score REAL,
                score_formula TEXT,
                performance_inputs_used TEXT,
                recommendation_reason TEXT,
                campaign_tag TEXT DEFAULT 'General',
                saved_at TEXT NOT NULL,
                last_updated_at TEXT NOT NULL
            )
            """
        )

        existing_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(creator_shortlist)"
            ).fetchall()
        }

        migrations = {
            "median_matched_video_views": "REAL",
            "matched_video_count": "REAL",
            "recent_matched_videos_30d": "REAL",
            "recent_matched_videos_90d": "REAL",
            "score_formula": "TEXT",
            "performance_inputs_used": "TEXT",
        }

        for column, data_type in migrations.items():
            if column not in existing_columns:
                connection.execute(
                    f"ALTER TABLE creator_shortlist "
                    f"ADD COLUMN {column} {data_type}"
                )


def save_channel_snapshot(channel):
    """Save a timestamped snapshot of public channel statistics."""
    channel_id = str(channel.get("channel_id", "")).strip()

    if not channel_id:
        raise ValueError("Channel ID is required to save a snapshot.")

    with get_connection() as connection:
        connection.execute(
            """
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
            """,
            (
                channel_id,
                channel.get("channel_name"),
                utc_now(),
                _number(channel.get("subscriber_count")),
                _number(channel.get("total_channel_views")),
                _number(channel.get("total_channel_videos")),
                _number(channel.get("average_matched_video_views")),
                _number(channel.get("public_interactions_per_view_pct")),
            ),
        )


def get_channel_history(channel_id):
    """Return saved historical snapshots, oldest first."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM channel_snapshots
            WHERE channel_id = ?
            ORDER BY recorded_at ASC, id ASC
            """,
            (str(channel_id),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_latest_channel_snapshots():
    """Return the latest saved snapshot for each channel."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT s.*
            FROM channel_snapshots s
            INNER JOIN (
                SELECT channel_id, MAX(id) AS latest_id
                FROM channel_snapshots
                GROUP BY channel_id
            ) latest ON latest.latest_id = s.id
            ORDER BY s.recorded_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_tracking_summary():
    """Return overall history-tracking totals."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS snapshot_count,
                COUNT(DISTINCT channel_id) AS tracked_channels,
                MIN(recorded_at) AS first_recorded_at,
                MAX(recorded_at) AS last_recorded_at
            FROM channel_snapshots
            """
        ).fetchone()

    return dict(row) if row else {
        "snapshot_count": 0,
        "tracked_channels": 0,
        "first_recorded_at": None,
        "last_recorded_at": None,
    }


def save_creator_to_shortlist(creator, campaign_tag="General"):
    """Save or update a creator in the persistent shortlist."""
    channel_id = str(creator.get("channel_id", "")).strip()

    if not channel_id:
        raise ValueError("Channel ID is required to save a creator.")

    now = utc_now()
    campaign_tag = str(campaign_tag or "General").strip() or "General"

    columns = [
        "channel_id",
        "channel_name",
        "channel_url",
        "thumbnail_url",
        "description",
        "published_at",
        "subscriber_count",
        "total_channel_views",
        "total_channel_videos",
        "average_matched_video_views",
        "median_matched_video_views",
        "matched_video_count",
        "recent_matched_videos_30d",
        "recent_matched_videos_90d",
        "public_interactions_per_view_pct",
        "content_match_pct",
        "performance_score",
        "performance_view_score",
        "performance_engagement_score",
        "performance_subscriber_score",
        "suitability_score",
        "score_formula",
        "performance_inputs_used",
        "recommendation_reason",
        "campaign_tag",
        "saved_at",
        "last_updated_at",
    ]

    values = [
        channel_id,
        creator.get("channel_name"),
        creator.get("channel_url"),
        creator.get("thumbnail_url"),
        creator.get("description"),
        creator.get("published_at"),
        *[_number(creator.get(field)) for field in NUMERIC_FIELDS],
        creator.get("score_formula"),
        creator.get("performance_inputs_used"),
        creator.get("recommendation_reason"),
        campaign_tag,
        now,
        now,
    ]

    update_columns = [
        column
        for column in columns
        if column not in ("channel_id", "saved_at")
    ]

    assignments = ", ".join(
        f"{column}=excluded.{column}"
        for column in update_columns
    )

    with get_connection() as connection:
        connection.execute(
            f"INSERT INTO creator_shortlist ({', '.join(columns)}) "
            f"VALUES ({', '.join('?' for _ in columns)}) "
            f"ON CONFLICT(channel_id) DO UPDATE SET {assignments}",
            values,
        )


def remove_creator_from_shortlist(channel_id):
    """Remove a saved creator by channel ID."""
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM creator_shortlist WHERE channel_id = ?",
            (str(channel_id),),
        )


def get_saved_creators(campaign_tag=None):
    """Return saved creators, optionally filtered by campaign tag."""
    with get_connection() as connection:
        if campaign_tag and campaign_tag != "All campaigns":
            rows = connection.execute(
                """
                SELECT *
                FROM creator_shortlist
                WHERE campaign_tag = ?
                ORDER BY saved_at DESC, channel_name COLLATE NOCASE
                """,
                (str(campaign_tag),),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM creator_shortlist
                ORDER BY saved_at DESC, channel_name COLLATE NOCASE
                """
            ).fetchall()

    return [dict(row) for row in rows]


def get_shortlist_campaigns():
    """Return distinct saved campaign tags."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT campaign_tag
            FROM creator_shortlist
            WHERE campaign_tag IS NOT NULL
              AND campaign_tag <> ''
            ORDER BY campaign_tag COLLATE NOCASE
            """
        ).fetchall()

    return [row[0] for row in rows]