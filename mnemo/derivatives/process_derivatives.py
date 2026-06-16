import logging
from pathlib import Path

import config
from mnemo.db import sqlite as db
from mnemo.llm import ollama_client

logger = logging.getLogger(__name__)

DERIVATIVE_PROMPTS = {
    "summary": (
        "You are an expert educational summariser.\n"
        "Condense the following study notes into a concise summary.\n"
        "Preserve all key concepts, definitions, and important details.\n"
        "Format as clean Markdown with clear headings.\n"
        "Output ONLY the summary Markdown.",
        "Summarise the following study notes:\n\n{content}",
    ),
    "review_questions": (
        "You are an expert educator creating active recall questions.\n"
        "Generate 10-15 review questions that test understanding of the material.\n"
        "Include a mix of factual recall, concept explanation, and application questions.\n"
        "Format as a numbered Markdown list.\n"
        "Output ONLY the questions, no answers.",
        "Generate review questions for the following study notes:\n\n{content}",
    ),
    "flashcards": (
        "You are an expert at creating spaced-repetition flashcards.\n"
        "Create 10-20 flashcards from the study notes.\n"
        "Format each card exactly as:\nQ: <question>\nA: <answer>\n\n"
        "Cover key terms, concepts, facts, and relationships.\n"
        "Output ONLY the flashcards.",
        "Create flashcards from the following study notes:\n\n{content}",
    ),
    "knowledge_gaps": (
        "You are an expert educational diagnostician.\n"
        "Analyse the study notes and identify concepts that:\n"
        "- Are mentioned but not fully explained\n"
        "- Rely on assumed background knowledge\n"
        "- Are likely to cause confusion\n"
        "- Would benefit from further study\n"
        "Format as a Markdown list with brief explanations of why each gap matters.\n"
        "Output ONLY the knowledge gaps analysis.",
        "Identify knowledge gaps in the following study notes:\n\n{content}",
    ),
}

DERIVATIVE_HEADERS = {
    "summary": "# Summary",
    "review_questions": "# Review Questions",
    "flashcards": "# Flashcards",
    "knowledge_gaps": "# Concepts Requiring Clarification",
}


def _generate_derivative(artifact: dict, derivative_type: str) -> str:
    system_prompt, user_template = DERIVATIVE_PROMPTS[derivative_type]
    content = artifact["markdown"]
    user_prompt = user_template.format(content=content)
    result = ollama_client.generate_text(user_prompt, system=system_prompt)
    if not result.strip():
        raise ValueError(f"LLM returned empty {derivative_type}")
    return result


def generate_derivative(artifact_id: int, derivative_type: str) -> int:
    """Generate one derivative type for an artifact. Returns derivative_id."""
    if derivative_type not in DERIVATIVE_PROMPTS:
        raise ValueError(f"Unknown derivative type: {derivative_type}")

    artifact = db.get_raw_artifact(artifact_id)
    if not artifact:
        raise ValueError(f"Artifact {artifact_id} not found")

    logger.info("Generating %s for artifact %d", derivative_type, artifact_id)
    try:
        content = _generate_derivative(artifact, derivative_type)
        derivative_id = db.save_derivative(artifact_id, derivative_type, content, status="completed")
        logger.info("Derivative %s saved: id=%d", derivative_type, derivative_id)
        return derivative_id
    except Exception as exc:
        logger.error("Failed to generate %s for artifact %d: %s", derivative_type, artifact_id, exc)
        derivative_id = db.save_derivative(
            artifact_id, derivative_type, None, status="failed", error_message=str(exc)
        )
        return derivative_id


def process_all_derivatives(artifact_id: int) -> dict:
    """Generate all derivative types. Returns {type: derivative_id}."""
    results = {}
    for dtype in DERIVATIVE_PROMPTS:
        results[dtype] = generate_derivative(artifact_id, dtype)
    return results


def export_derivative(derivative_id: int) -> str | None:
    """Export a derivative to a Markdown file. Returns file path or None if failed."""
    with db._conn() as con:
        row = con.execute("SELECT * FROM derivatives WHERE id = ?", (derivative_id,)).fetchone()
    if not row:
        raise ValueError(f"Derivative {derivative_id} not found")
    row = dict(row)

    if row["status"] != "completed" or not row["markdown"]:
        logger.warning("Derivative %d has status=%s — skipping export", derivative_id, row["status"])
        return None

    artifact = db.get_raw_artifact(row["artifact_id"])
    artifact_title = artifact["title"] if artifact else f"artifact_{row['artifact_id']}"

    out_dir = Path(config.EXPORTS_DIR) / "derivatives"
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in artifact_title)
    safe_title = safe_title.strip().replace(" ", "_")[:40]
    filename = f"derivative_{derivative_id}_{row['derivative_type']}_{safe_title}.md"
    out_path = out_dir / filename

    header = DERIVATIVE_HEADERS.get(row["derivative_type"], f"# {row['derivative_type'].replace('_', ' ').title()}")
    now = row["created_at"]
    preamble = (
        f"{header}\n\n"
        f"**Source:** {artifact_title} (artifact {row['artifact_id']})  \n"
        f"**Type:** {row['derivative_type']}  \n"
        f"**Generated:** {now}\n\n---\n\n"
    )
    out_path.write_text(preamble + row["markdown"].strip(), encoding="utf-8")
    logger.info("Derivative exported: %s", out_path)
    return str(out_path)


def export_all_derivatives(artifact_id: int) -> list[str]:
    """Export all derivatives for an artifact. Returns list of file paths."""
    derivatives = db.get_artifact_derivatives(artifact_id)
    paths = []
    for d in derivatives:
        path = export_derivative(d["id"])
        if path:
            paths.append(path)
    return paths
