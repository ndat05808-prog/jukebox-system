"""Functions that manage the track library and persistent storage."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .library_item import AlbumTrack, LibraryItem

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATA_FILE = DATA_DIR / "library_data.json"
HISTORY_FILE = DATA_DIR / "history_data.json"

DEFAULT_LIBRARY = {
    "01": {
        "type": "LibraryItem",
        "name": "What a Wonderful World",
        "artist": "Louis Armstrong",
        "rating": 5,
        "play_count": 0,
    },
    "02": {
        "type": "AlbumTrack",
        "name": "Here Comes the Sun",
        "artist": "The Beatles",
        "album": "Abbey Road",
        "year": 1969,
        "rating": 5,
        "play_count": 0,
    },
    "03": {
        "type": "LibraryItem",
        "name": "Count on Me",
        "artist": "Bruno Mars",
        "rating": 3,
        "play_count": 0,
    },
    "04": {
        "type": "AlbumTrack",
        "name": "Three Little Birds",
        "artist": "Bob Marley",
        "album": "Exodus",
        "year": 1977,
        "rating": 1,
        "play_count": 0,
    },
    "05": {
        "type": "LibraryItem",
        "name": "You've Got a Friend",
        "artist": "James Taylor",
        "rating": 3,
        "play_count": 0,
    },
}

library: dict[str, LibraryItem] = {}


def _make_item(data: dict) -> LibraryItem:
    item_type = data.get("type", "LibraryItem")
    if item_type == "AlbumTrack":
        return AlbumTrack.from_dict(data)
    return LibraryItem.from_dict(data)


def reset_library_to_default(save: bool = False) -> None:
    """Restore the in-memory library to the bundled default data."""
    global library
    library = {key: _make_item(info) for key, info in DEFAULT_LIBRARY.items()}
    if save:
        save_library()


reset_library_to_default(save=False)


def load_library() -> None:
    """Load the library from JSON, falling back to defaults when needed."""
    global library
    if not DATA_FILE.exists():
        reset_library_to_default(save=True)
        return

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        reset_library_to_default(save=True)
        return

    library = {key: _make_item(info) for key, info in data.items()}


def save_library() -> None:
    """Write the current library to JSON."""
    data = {key: item.to_dict() for key, item in library.items()}
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_history() -> list[dict]:
    """Load play history from JSON."""
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
        return []

    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        HISTORY_FILE.write_text("[]", encoding="utf-8")
        return []

    if not isinstance(history, list):
        HISTORY_FILE.write_text("[]", encoding="utf-8")
        return []

    return history


def save_history(history: list[dict]) -> None:
    """Write play history to JSON."""
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def add_history_entry(track_key: str, source: str = "playlist") -> bool:
    """Add one play-history entry for a track."""
    item = get_item(track_key)
    if item is None:
        return False

    history = load_history()
    history.append(
        {
            "track_key": track_key,
            "name": item.name,
            "artist": item.artist,
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
        }
    )
    save_history(history)
    return True


def clear_history() -> None:
    """Delete all history entries."""
    save_history([])


def all_keys() -> list[str]:
    return sorted(library.keys(), key=int)


def list_all() -> str:
    output_lines = []
    for key in all_keys():
        output_lines.append(f"{key} {library[key].info()}")
    return "\n".join(output_lines) + ("\n" if output_lines else "")


def get_item(key: str) -> LibraryItem | None:
    return library.get(key)


def get_name(key: str) -> str | None:
    item = get_item(key)
    if item is None:
        return None
    return item.name


def get_artist(key: str) -> str | None:
    item = get_item(key)
    if item is None:
        return None
    return item.artist


def get_rating(key: str) -> int:
    item = get_item(key)
    if item is None:
        return -1
    return item.rating


def set_rating(key: str, rating: int, auto_save: bool = True) -> bool:
    item = get_item(key)
    if item is None:
        return False
    item.set_rating(rating)
    if auto_save:
        save_library()
    return True


def update_track_info(
    key: str,
    name: str,
    artist: str,
    rating: int,
    album: str = "",
    year: int | None = None,
    auto_save: bool = True,
) -> bool:
    item = get_item(key)
    if item is None:
        return False

    name = name.strip()
    artist = artist.strip()
    album = album.strip()

    if name == "" or artist == "":
        return False

    play_count = item.play_count

    if album != "" or year is not None:
        library[key] = AlbumTrack(name, artist, rating, play_count, album, year)
    else:
        library[key] = LibraryItem(name, artist, rating, play_count)

    if auto_save:
        save_library()
    return True


def get_play_count(key: str) -> int:
    item = get_item(key)
    if item is None:
        return -1
    return item.play_count


def increment_play_count(key: str, auto_save: bool = True) -> bool:
    item = get_item(key)
    if item is None:
        return False
    item.increment_play_count()
    if auto_save:
        save_library()
    return True


def get_details(key: str) -> str | None:
    item = get_item(key)
    if item is None:
        return None
    return item.details(key)


def search_tracks(keyword: str) -> str:
    keyword = keyword.strip().lower()
    if keyword == "":
        return list_all()

    output_lines = []
    for key in all_keys():
        item = library[key]
        if item.matches(keyword):
            output_lines.append(f"{key} {item.info()}")
    return "\n".join(output_lines) + ("\n" if output_lines else "")


def filter_tracks_by_rating(rating: int) -> str:
    output_lines = []
    for key in all_keys():
        item = library[key]
        if item.rating == rating:
            output_lines.append(f"{key} {item.info()}")
    return "\n".join(output_lines) + ("\n" if output_lines else "")


def get_next_key() -> str:
    if not library:
        return "01"
    max_key = max(int(key) for key in library)
    return str(max_key + 1).zfill(2)


def add_track(name: str, artist: str, rating: int = 0) -> str:
    key = get_next_key()
    library[key] = LibraryItem(name, artist, rating)
    save_library()
    return key


def delete_track(key: str) -> bool:
    if key not in library:
        return False
    del library[key]
    save_library()
    return True


def get_statistics() -> dict:
    tracks = []
    for key in all_keys():
        item = library[key]
        tracks.append(
            {
                "key": key,
                "name": item.name,
                "artist": item.artist,
                "rating": item.rating,
                "play_count": item.play_count,
                "type": item.__class__.__name__,
            }
        )

    total_tracks = len(tracks)
    total_plays = sum(track["play_count"] for track in tracks)
    average_rating = 0.0 if total_tracks == 0 else sum(track["rating"] for track in tracks) / total_tracks
    most_played = max(tracks, key=lambda track: track["play_count"], default=None)
    highest_rated = max(tracks, key=lambda track: track["rating"], default=None)
    return {
        "tracks": tracks,
        "total_tracks": total_tracks,
        "total_plays": total_plays,
        "average_rating": average_rating,
        "most_played": most_played,
        "highest_rated": highest_rated,
    }


load_library()