import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timezone

import config

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _conn():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                topic       TEXT,
                category    TEXT,
                start_time  TEXT    NOT NULL,
                end_time    TEXT
            );

            CREATE TABLE IF NOT EXISTS screenshots (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER NOT NULL REFERENCES study_sessions(id),
                filepath        TEXT    NOT NULL,
                timestamp       TEXT    NOT NULL,
                extracted_text  TEXT,
                status          TEXT    NOT NULL DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS raw_artifacts (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id              INTEGER NOT NULL REFERENCES study_sessions(id),
                title                   TEXT    NOT NULL,
                markdown                TEXT    NOT NULL,
                created_at              TEXT    NOT NULL,
                week_character          TEXT,
                day_theme               TEXT,
                time_character          TEXT,
                week_number             INTEGER,
                weekday                 TEXT,
                source_screenshot_count INTEGER
            );

            CREATE TABLE IF NOT EXISTS artifact_images (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_id INTEGER NOT NULL REFERENCES raw_artifacts(id),
                filepath    TEXT    NOT NULL,
                caption     TEXT
            );

            CREATE TABLE IF NOT EXISTS derivatives (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_id     INTEGER NOT NULL REFERENCES raw_artifacts(id),
                derivative_type TEXT    NOT NULL,
                markdown        TEXT,
                created_at      TEXT    NOT NULL,
                status          TEXT    NOT NULL DEFAULT 'pending',
                error_message   TEXT
            );
        """)
    logger.info("Database initialised at %s", config.DB_PATH)


# ── Study Sessions ─────────────────────────────────────────────────────────────

def create_session(title: str, topic: str = "", category: str = "") -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO study_sessions (title, topic, category, start_time) VALUES (?, ?, ?, ?)",
            (title, topic, category, _now()),
        )
    session_id = cur.lastrowid
    logger.info("Session created: id=%d title=%r", session_id, title)
    return session_id


def end_session(session_id: int) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE study_sessions SET end_time = ? WHERE id = ?",
            (_now(), session_id),
        )
    logger.info("Session ended: id=%d", session_id)


def get_session(session_id: int) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,)).fetchone()
    return dict(row) if row else None


# ── Screenshots ────────────────────────────────────────────────────────────────

def add_screenshot(session_id: int, filepath: str) -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO screenshots (session_id, filepath, timestamp) VALUES (?, ?, ?)",
            (session_id, filepath, _now()),
        )
    screenshot_id = cur.lastrowid
    logger.info("Screenshot added: id=%d session=%d path=%s", screenshot_id, session_id, filepath)
    return screenshot_id


def update_screenshot(screenshot_id: int, extracted_text: str, status: str = "processed") -> None:
    with _conn() as con:
        con.execute(
            "UPDATE screenshots SET extracted_text = ?, status = ? WHERE id = ?",
            (extracted_text, status, screenshot_id),
        )


def get_session_screenshots(session_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM screenshots WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Raw Artifacts ──────────────────────────────────────────────────────────────

def save_raw_artifact(
    session_id: int,
    title: str,
    markdown: str,
    source_screenshot_count: int,
    week_character: str | None = None,
    day_theme: str | None = None,
    time_character: str | None = None,
    week_number: int | None = None,
    weekday: str | None = None,
) -> int:
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO raw_artifacts
               (session_id, title, markdown, created_at,
                week_character, day_theme, time_character,
                week_number, weekday, source_screenshot_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, title, markdown, _now(),
             week_character, day_theme, time_character,
             week_number, weekday, source_screenshot_count),
        )
    artifact_id = cur.lastrowid
    logger.info("Raw artifact saved: id=%d session=%d", artifact_id, session_id)
    return artifact_id


def get_raw_artifact(artifact_id: int) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM raw_artifacts WHERE id = ?", (artifact_id,)).fetchone()
    return dict(row) if row else None


def get_session_raw_artifact(session_id: int) -> dict | None:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM raw_artifacts WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    return dict(row) if row else None


def list_raw_artifacts() -> list[dict]:
    with _conn() as con:
        rows = con.execute("SELECT * FROM raw_artifacts ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


# ── Artifact Images ────────────────────────────────────────────────────────────

def save_artifact_image(artifact_id: int, filepath: str, caption: str = "") -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO artifact_images (artifact_id, filepath, caption) VALUES (?, ?, ?)",
            (artifact_id, filepath, caption),
        )
    return cur.lastrowid


# ── Derivatives ────────────────────────────────────────────────────────────────

def save_derivative(
    artifact_id: int,
    derivative_type: str,
    markdown: str | None,
    status: str = "completed",
    error_message: str | None = None,
) -> int:
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO derivatives
               (artifact_id, derivative_type, markdown, created_at, status, error_message)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (artifact_id, derivative_type, markdown, _now(), status, error_message),
        )
    derivative_id = cur.lastrowid
    logger.info("Derivative saved: id=%d type=%s artifact=%d status=%s",
                derivative_id, derivative_type, artifact_id, status)
    return derivative_id


def get_artifact_derivatives(artifact_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM derivatives WHERE artifact_id = ? ORDER BY created_at",
            (artifact_id,),
        ).fetchall()
    return [dict(r) for r in rows]
