"""Validation helper functions used by the GUI classes."""

from __future__ import annotations


def normalise_track_number(track_number: str) -> str | None:
    """Convert user input like 4 to 04.

    Returns None when the input is blank or contains non-digits.
    """
    track_number = track_number.strip()
    if track_number == "":
        return None
    if not track_number.isdigit():
        return None
    return track_number.zfill(2)


def get_valid_rating(rating_text: str, allow_zero: bool = False) -> int | None:
    """Return a whole-number rating when it is inside the allowed range."""
    rating_text = rating_text.strip()
    if rating_text == "":
        return 0 if allow_zero else None
    if not rating_text.isdigit():
        return None
    rating = int(rating_text)
    minimum = 0 if allow_zero else 1
    if minimum <= rating <= 5:
        return rating
    return None


def get_valid_position(position_text: str, maximum: int) -> int | None:
    """Return a valid playlist position between 1 and maximum inclusive."""
    position_text = position_text.strip()
    if not position_text.isdigit():
        return None
    position = int(position_text)
    if 1 <= position <= maximum:
        return position
    return None


def normalise_playlist_name(name: str) -> str | None:
    """Keep only safe filename characters for playlist names."""
    name = name.strip()
    if name == "":
        return None
    cleaned = "".join(character for character in name if character.isalnum() or character in "_- ")
    cleaned = " ".join(cleaned.split())
    if cleaned == "":
        return None
    return cleaned