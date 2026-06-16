import logging
import shutil
from pathlib import Path

import config
from mnemo.db import sqlite as db

logger = logging.getLogger(__name__)


def add_screenshot(session_id: int, filepath: str, copy_to_dir: bool = True) -> int:
    """
    Register a screenshot with the active session.

    If copy_to_dir is True, copies the file into SCREENSHOTS_DIR so the pipeline
    owns a stable copy regardless of where the source file lives.
    """
    src = Path(filepath).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"Screenshot not found: {src}")

    dest_path = str(src)
    if copy_to_dir:
        screenshots_dir = Path(config.SCREENSHOTS_DIR)
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        dest = screenshots_dir / f"session_{session_id}_{src.name}"
        if not dest.exists():
            shutil.copy2(src, dest)
            logger.info("Screenshot copied: %s -> %s", src, dest)
        dest_path = str(dest)

    screenshot_id = db.add_screenshot(session_id, dest_path)
    return screenshot_id
