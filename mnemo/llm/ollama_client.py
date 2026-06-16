import base64
import logging
import re
from pathlib import Path

import requests

import config

logger = logging.getLogger(__name__)

VISION_TIMEOUT = 120  # VLM inference can be slow
TEXT_TIMEOUT = 120

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

SCREENSHOT_EXTRACT_SYSTEM = """You are an expert educational content extractor.
Your job is to extract ALL learning content from a screenshot and format it as clean, structured Markdown.

Rules:
- OCR text verbatim where it is the actual content.
- Format tables as Markdown tables.
- Wrap code in fenced code blocks with the correct language tag.
- Render mathematical formulas in LaTeX ($ inline, $$ block).
- For diagrams, charts, or images that cannot be represented as text, write [FIGURE: brief description of what is shown].
- Capture the educational meaning and context, not just raw text.
- Do NOT add commentary about your extraction process.
- Output ONLY the structured Markdown."""

SCREENSHOT_EXTRACT_USER = "Extract all learning content from this screenshot."


def _strip_think(text: str) -> str:
    """Remove <think>...</think> blocks emitted by reasoning models (e.g. deepseek-r1)."""
    return _THINK_RE.sub("", text).strip()


def _image_to_b64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _chat(model: str, messages: list[dict], timeout: int) -> str:
    url = f"{config.OLLAMA_BASE_URL}/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}
    logger.debug("Ollama chat request: model=%s url=%s", model, url)
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        return _strip_think(content)
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Ollama unreachable at {config.OLLAMA_BASE_URL}: {e}") from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"Ollama timed out after {timeout}s") from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama HTTP error: {e}") from e


def extract_screenshot(image_path: str) -> str:
    """Send a screenshot to the vision model and return extracted Markdown text."""
    logger.info("Extracting screenshot via VLM: %s", image_path)
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Screenshot not found: {image_path}")

    b64 = _image_to_b64(image_path)
    messages = [
        {"role": "system", "content": SCREENSHOT_EXTRACT_SYSTEM},
        {"role": "user", "content": SCREENSHOT_EXTRACT_USER, "images": [b64]},
    ]
    result = _chat(config.OLLAMA_VISION_MODEL, messages, VISION_TIMEOUT)
    logger.info("Screenshot extracted: %d chars from %s", len(result), image_path)
    return result


def generate_text(prompt: str, system: str | None = None) -> str:
    """Send a text prompt to the text model and return the response."""
    logger.info("Text generation: model=%s prompt_len=%d", config.OLLAMA_TEXT_MODEL, len(prompt))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    result = _chat(config.OLLAMA_TEXT_MODEL, messages, TEXT_TIMEOUT)
    logger.info("Text generated: %d chars", len(result))
    return result
