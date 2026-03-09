"""Helper utilities."""

from datetime import datetime, timedelta
from typing import Optional
import re


def parse_time_duration(time_str: str) -> Optional[datetime]:
    """
    Parse time duration strings like '1h', '2d', '30m' into future datetime.

    Formats:
    - '30m' or '30min' -> 30 minutes
    - '2h' or '2hr' -> 2 hours
    - '3d' or '3day' -> 3 days
    - '1w' or '1wk' -> 1 week
    """
    time_str = time_str.lower().strip()

    # Pattern: number followed by unit
    match = re.match(r"^(\d+)(m(?:in)?|h(?:r)?|d(?:ay)?|w(?:k)?)$", time_str)

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    now = datetime.now()

    if unit.startswith("m"):
        return now + timedelta(minutes=amount)
    elif unit.startswith("h"):
        return now + timedelta(hours=amount)
    elif unit.startswith("d"):
        return now + timedelta(days=amount)
    elif unit.startswith("w"):
        return now + timedelta(weeks=amount)

    return None


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")


def is_market_closed(close_time: datetime) -> bool:
    """Check if market has closed."""
    return datetime.now() >= close_time


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
