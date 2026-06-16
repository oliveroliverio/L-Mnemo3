import logging
from typing import Any

import requests
from pydantic import BaseModel, field_validator

import config

logger = logging.getLogger(__name__)

TIMEOUT = 5  # seconds


class MemoryPeg(BaseModel):
    week_character: str | None = None
    day_theme: str | None = None
    time_character: str | None = None
    week_number: int | None = None
    weekday: str | None = None
    current_date: str | None = None

    @field_validator("week_number", mode="before")
    @classmethod
    def coerce_week_number(cls, v: Any) -> int | None:
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None


def _extract_name(obj: Any) -> str | None:
    """Pull a human-readable name from a peg character/theme object."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for key in ("name", "character", "theme", "title", "label"):
            if key in obj and obj[key]:
                return str(obj[key])
        return str(next(iter(obj.values()))) if obj else None
    return str(obj)


def get_memory_peg() -> MemoryPeg:
    """Fetch Memory Peg metadata. Returns empty MemoryPeg on any failure."""
    logger.info("Fetching Memory Peg from %s", config.MEMORY_PEG_BASE_URL)
    try:
        resp = requests.get(config.MEMORY_PEG_BASE_URL, timeout=TIMEOUT)
        resp.raise_for_status()
        data: dict = resp.json()
    except requests.exceptions.ConnectionError:
        logger.warning("Memory Peg API unreachable — continuing without peg metadata")
        return MemoryPeg()
    except requests.exceptions.Timeout:
        logger.warning("Memory Peg API timed out — continuing without peg metadata")
        return MemoryPeg()
    except Exception as exc:
        logger.warning("Memory Peg API error (%s) — continuing without peg metadata", exc)
        return MemoryPeg()

    week_obj = data.get("weekCharacter") or data.get("week_character")
    day_obj = data.get("dayTheme") or data.get("day_theme")
    time_obj = data.get("timeCharacter") or data.get("time_character")
    current = data.get("currentDate") or data.get("current_date") or data.get("datetime")

    week_num = None
    if isinstance(week_obj, dict):
        week_num = week_obj.get("weekNumber") or week_obj.get("week_number") or week_obj.get("number")
    weekday = None
    if isinstance(day_obj, dict):
        weekday = day_obj.get("weekday") or day_obj.get("day") or day_obj.get("name")

    peg = MemoryPeg(
        week_character=_extract_name(week_obj),
        day_theme=_extract_name(day_obj),
        time_character=_extract_name(time_obj),
        week_number=week_num,
        weekday=weekday,
        current_date=str(current) if current else None,
    )
    logger.info(
        "Memory Peg fetched: week=%r day=%r time=%r",
        peg.week_character,
        peg.day_theme,
        peg.time_character,
    )
    return peg
