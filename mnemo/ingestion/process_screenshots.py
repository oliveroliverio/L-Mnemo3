import logging

from mnemo.db import sqlite as db
from mnemo.llm import ollama_client

logger = logging.getLogger(__name__)


def process_screenshot(screenshot: dict) -> bool:
    """
    Run VLM extraction on a single screenshot record.
    Returns True on success, False on failure (pipeline continues regardless).
    """
    sid = screenshot["id"]
    filepath = screenshot["filepath"]
    logger.info("Processing screenshot id=%d path=%s", sid, filepath)
    try:
        extracted_text = ollama_client.extract_screenshot(filepath)
        if not extracted_text or not extracted_text.strip():
            logger.warning("VLM returned empty response for screenshot id=%d", sid)
            db.update_screenshot(sid, extracted_text="", status="failed")
            return False
        db.update_screenshot(sid, extracted_text=extracted_text, status="processed")
        logger.info("Screenshot id=%d processed: %d chars", sid, len(extracted_text))
        return True
    except FileNotFoundError as exc:
        logger.error("Screenshot file missing id=%d: %s", sid, exc)
        db.update_screenshot(sid, extracted_text="", status="failed")
        return False
    except RuntimeError as exc:
        logger.error("LLM error for screenshot id=%d: %s", sid, exc)
        db.update_screenshot(sid, extracted_text="", status="failed")
        return False


def process_session_screenshots(session_id: int) -> dict:
    """
    Process all pending screenshots for a session.
    Returns counts: {total, processed, failed}.
    """
    screenshots = db.get_session_screenshots(session_id)
    pending = [s for s in screenshots if s["status"] == "pending"]
    logger.info("Processing %d pending screenshots for session %d", len(pending), session_id)

    processed = 0
    failed = 0
    for shot in pending:
        if process_screenshot(shot):
            processed += 1
        else:
            failed += 1

    logger.info(
        "Session %d screenshots done: total=%d processed=%d failed=%d",
        session_id, len(pending), processed, failed,
    )
    return {"total": len(pending), "processed": processed, "failed": failed}
