import os

MEMORY_PEG_BASE_URL = os.environ.get("MEMORY_PEG_BASE_URL", "http://100.88.124.124:3000/getCharacters")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://100.68.156.34:11434")
OLLAMA_VISION_MODEL = os.environ.get("OLLAMA_VISION_MODEL", "qwen3-vl:8b")
OLLAMA_TEXT_MODEL = os.environ.get("OLLAMA_TEXT_MODEL", "qwen3-coder:30b")
DB_PATH = os.environ.get("MNEMO_DB_PATH", "mnemo.db")
SCREENSHOTS_DIR = os.environ.get("MNEMO_SCREENSHOTS_DIR", "screenshots")
EXPORTS_DIR = os.environ.get("MNEMO_EXPORTS_DIR", "exports")
ACTIVE_SESSION_FILE = os.environ.get("MNEMO_SESSION_FILE", ".mnemo_session")
