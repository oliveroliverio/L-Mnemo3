import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

import config
from mnemo.db import sqlite as db
from mnemo.llm import ollama_client
from mnemo.memory_peg.memory_peg_client import get_memory_peg

logger = logging.getLogger(__name__)

MERGE_SYSTEM = """You are an expert educational content organiser.
You will receive multiple Markdown fragments extracted from screenshots of a study session.
Your job is to merge them into one coherent, well-structured study document.

Rules:
- Remove duplicate content; keep the most complete version.
- Preserve ALL factual content — do not omit concepts.
- Organise content with clear headings and logical flow.
- Keep code blocks, tables, formulas, and [FIGURE:] references intact.
- Do NOT add your own explanations or commentary.
- Output ONLY the merged Markdown body (no YAML front-matter, no title heading)."""


def _merge_fragments(fragments: list[str], session_title: str) -> str:
    """Use the text LLM to merge extracted screenshot fragments into one document."""
    if not fragments:
        return ""
    if len(fragments) == 1:
        return fragments[0]

    joined = "\n\n---\n\n".join(
        f"## Fragment {i + 1}\n\n{frag}" for i, frag in enumerate(fragments) if frag.strip()
    )
    prompt = (
        f"Study session topic: {session_title}\n\n"
        f"Below are {len(fragments)} Markdown fragments extracted from screenshots. "
        f"Merge them into one coherent study document.\n\n"
        f"{joined}"
    )
    return ollama_client.generate_text(prompt, system=MERGE_SYSTEM)


def _copy_screenshot_as_image(screenshot: dict, artifact_id: int, idx: int) -> str | None:
    """Copy a screenshot into exports/images/ so the artifact can reference it."""
    src = Path(screenshot["filepath"])
    if not src.exists():
        return None
    images_dir = Path(config.EXPORTS_DIR) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    dest = images_dir / f"artifact_{artifact_id}_img_{idx:03d}{src.suffix}"
    shutil.copy2(src, dest)
    return str(dest)


def _build_markdown(title: str, body: str, peg, screenshots: list[dict], artifact_id: int) -> str:
    """Assemble the final raw artifact Markdown with front-matter header."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# {title}",
        "",
        f"**Created:** {now}  ",
        f"**Source screenshots:** {len(screenshots)}  ",
    ]
    if peg.week_character or peg.day_theme or peg.time_character:
        lines += [
            "",
            "## Memory Peg",
            "",
            f"| Field | Value |",
            f"| --- | --- |",
        ]
        if peg.week_character:
            lines.append(f"| Week Character | {peg.week_character} |")
        if peg.day_theme:
            lines.append(f"| Day Theme | {peg.day_theme} |")
        if peg.time_character:
            lines.append(f"| Time Character | {peg.time_character} |")
        if peg.week_number:
            lines.append(f"| Week | {peg.week_number} |")
        if peg.weekday:
            lines.append(f"| Weekday | {peg.weekday} |")

    lines += ["", "---", "", body.strip()]
    return "\n".join(lines)


def build_raw_artifact(session_id: int, title: str | None = None) -> int:
    """
    Build a Raw Artifact from all processed screenshots in the session.
    Returns the artifact_id.
    """
    session = db.get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    artifact_title = title or session["title"]
    screenshots = db.get_session_screenshots(session_id)
    if not screenshots:
        raise ValueError(f"No screenshots found for session {session_id}")

    logger.info(
        "Building raw artifact for session %d (%d screenshots)", session_id, len(screenshots)
    )

    # Collect extracted fragments from processed screenshots
    fragments = []
    for shot in screenshots:
        text = shot.get("extracted_text") or ""
        if shot["status"] == "processed" and text.strip():
            fragments.append(text)
        elif shot["status"] == "failed":
            logger.warning("Skipping failed screenshot id=%d", shot["id"])

    if not fragments:
        raise ValueError(f"No processed content available for session {session_id}")

    # Merge fragments via LLM (or use single fragment directly)
    logger.info("Merging %d fragments via LLM", len(fragments))
    try:
        body = _merge_fragments(fragments, artifact_title)
        if not body.strip():
            logger.warning("LLM merge returned empty body — concatenating fragments instead")
            body = "\n\n---\n\n".join(fragments)
    except RuntimeError as exc:
        logger.warning("LLM merge failed (%s) — concatenating fragments instead", exc)
        body = "\n\n---\n\n".join(fragments)

    # Fetch Memory Peg metadata
    peg = get_memory_peg()

    # Save to DB first to get the artifact_id (needed for image paths)
    artifact_id = db.save_raw_artifact(
        session_id=session_id,
        title=artifact_title,
        markdown="__placeholder__",
        source_screenshot_count=len(screenshots),
        week_character=peg.week_character,
        day_theme=peg.day_theme,
        time_character=peg.time_character,
        week_number=peg.week_number,
        weekday=peg.weekday,
    )

    # Build final markdown with peg header
    markdown = _build_markdown(artifact_title, body, peg, screenshots, artifact_id)

    # Update with real markdown
    with db._conn() as con:
        con.execute(
            "UPDATE raw_artifacts SET markdown = ? WHERE id = ?",
            (markdown, artifact_id),
        )

    logger.info("Raw artifact built: id=%d title=%r", artifact_id, artifact_title)
    return artifact_id


def export_raw_artifact(artifact_id: int) -> str:
    """Export the raw artifact to a Markdown file. Returns the file path."""
    artifact = db.get_raw_artifact(artifact_id)
    if not artifact:
        raise ValueError(f"Artifact {artifact_id} not found")

    out_dir = Path(config.EXPORTS_DIR) / "raw_artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in artifact["title"])
    safe_title = safe_title.strip().replace(" ", "_")[:60]
    filename = f"artifact_{artifact_id}_{safe_title}.md"
    out_path = out_dir / filename

    out_path.write_text(artifact["markdown"], encoding="utf-8")
    logger.info("Raw artifact exported: %s", out_path)
    return str(out_path)
