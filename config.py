import os

# ── Service URLs ───────────────────────────────────────────────────────────────
MEMORY_PEG_BASE_URL = os.environ.get("MEMORY_PEG_BASE_URL", "http://100.88.124.124:3000/getCharacters")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://100.68.156.34:11434")
OLLAMA_VISION_MODEL = os.environ.get("OLLAMA_VISION_MODEL", "qwen3-vl:8b")
OLLAMA_TEXT_MODEL = os.environ.get("OLLAMA_TEXT_MODEL", "qwen3-coder:30b")

# ── Storage ────────────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("MNEMO_DB_PATH", "mnemo.db")
SCREENSHOTS_DIR = os.environ.get("MNEMO_SCREENSHOTS_DIR", "screenshots")
EXPORTS_DIR = os.environ.get("MNEMO_EXPORTS_DIR", "exports")
ACTIVE_SESSION_FILE = os.environ.get("MNEMO_SESSION_FILE", ".mnemo_session")

# ── Session defaults — edit these directly ─────────────────────────────────────
SESSION_TITLE = "Study Session"
SESSION_TOPIC = ""
SESSION_CATEGORY = ""

# Screenshot paths for the current session.
# Add paths here instead of passing them via `add-screenshot` on the command line.
SCREENSHOT_PATHS: list[str] = [
    # "/path/to/screenshot1.png",
    # "/path/to/screenshot2.png",
]
