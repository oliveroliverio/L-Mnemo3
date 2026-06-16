import os
import tempfile
import pytest

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["MNEMO_DB_PATH"] = _tmp.name

from mnemo.db import sqlite as db


def setup_function():
    db.init_db()


def test_session_lifecycle():
    sid = db.create_session("Test Session", topic="Python", category="CS")
    assert isinstance(sid, int)
    session = db.get_session(sid)
    assert session["title"] == "Test Session"
    assert session["end_time"] is None

    db.end_session(sid)
    session = db.get_session(sid)
    assert session["end_time"] is not None


def test_screenshot_crud():
    sid = db.create_session("Screenshot Test")
    shot_id = db.add_screenshot(sid, "/tmp/test.png")
    shots = db.get_session_screenshots(sid)
    assert len(shots) == 1
    assert shots[0]["status"] == "pending"

    db.update_screenshot(shot_id, "## Extracted text", status="processed")
    shots = db.get_session_screenshots(sid)
    assert shots[0]["status"] == "processed"
    assert "Extracted" in shots[0]["extracted_text"]


def test_raw_artifact_crud():
    sid = db.create_session("Artifact Test")
    art_id = db.save_raw_artifact(
        session_id=sid,
        title="Test Artifact",
        markdown="# Test\n\nContent here.",
        source_screenshot_count=3,
        week_character="Buzz Lightyear",
        day_theme="Independence Day",
        time_character="Bill Nye",
    )
    artifact = db.get_raw_artifact(art_id)
    assert artifact["title"] == "Test Artifact"
    assert artifact["week_character"] == "Buzz Lightyear"
    assert artifact["source_screenshot_count"] == 3


def test_derivatives_crud():
    sid = db.create_session("Derivative Test")
    art_id = db.save_raw_artifact(sid, "Art", "# Content", 1)

    did = db.save_derivative(art_id, "summary", "# Summary\n\nShort.", status="completed")
    derivatives = db.get_artifact_derivatives(art_id)
    assert len(derivatives) == 1
    assert derivatives[0]["derivative_type"] == "summary"
    assert derivatives[0]["status"] == "completed"
