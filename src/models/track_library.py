"""Functions that manage the track library and persistent storage."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .library_item import AlbumTrack, LibraryItem

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
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
    try:
        if item_type == "AlbumTrack":
            return AlbumTrack.from_dict(data)
        return LibraryItem.from_dict(data)
    except (TypeError, ValueError):
        return LibraryItem(
            data.get("name", "Unknown Track"),
            data.get("artist", "Unknown Artist"),
            0,
            0,
        )


def reset_library_to_default(save: bool = False) -> bool:
    global library
    library = {key: _make_item(info) for key, info in DEFAULT_LIBRARY.items()}
    if save:
        return save_library()
    return True


def load_library() -> bool:
    global library
    if not DATA_FILE.exists():
        reset_library_to_default(save=False)
        return save_library()
    try:
        raw_text = DATA_FILE.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except (json.JSONDecodeError, OSError):
        reset_library_to_default(save=False)
        return save_library()
    if not isinstance(data, dict):
        reset_library_to_default(save=False)
        return save_library()
    loaded_library = {}
    for key, info in data.items():
        if not isinstance(key, str) or not isinstance(info, dict):
            continue
        loaded_library[key] = _make_item(info)
    if len(loaded_library) == 0:
        reset_library_to_default(save=False)
        return save_library()
    library = loaded_library
    return True


def save_library() -> bool:
    data = {key: item.to_dict() for key, item in library.items()}
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        try:
            HISTORY_FILE.write_text("[]", encoding="utf-8")
        except OSError:
            return []
        return []
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        try:
            HISTORY_FILE.write_text("[]", encoding="utf-8")
        except OSError:
            pass
        return []
    if not isinstance(history, list):
        try:
            HISTORY_FILE.write_text("[]", encoding="utf-8")
        except OSError:
            pass
        return []
    return history


def save_history(history: list[dict]) -> bool:
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False


def add_history_entry(
    track_key: str,
    source: str = "playlist",
    name: str | None = None,
    artist: str | None = None,
    action: str = "play",
) -> bool:
    if name is None or artist is None:
        item = get_item(track_key)
        if item is None:
            return False
        name = item.name
        artist = item.artist
    history = load_history()
    history.append(
        {
            "track_key": track_key,
            "name": name,
            "artist": artist,
            "action": action,
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
        }
    )
    return save_history(history)


def clear_history() -> bool:
    return save_history([])


def set_cover_path(key: str, cover_path: str | None) -> bool:
    item = library.get(key)
    if item is None:
        return False
    item.cover_path = cover_path or None
    return save_library()


def set_lyrics(key: str, lyrics: str | None) -> bool:
    item = library.get(key)
    if item is None:
        return False
    if lyrics is not None:
        lyrics = lyrics.strip()
    item.lyrics = lyrics or None
    return save_library()


def set_audio_path(key: str, audio_path: str | None) -> bool:
    item = library.get(key)
    if item is None:
        return False
    item.audio_path = audio_path or None
    return save_library()


def all_keys() -> list[str]:
    numeric_keys = [key for key in library.keys() if key.isdigit()]
    non_numeric_keys = [key for key in library.keys() if not key.isdigit()]
    return sorted(numeric_keys, key=int) + sorted(non_numeric_keys)


def list_all() -> str:
    output_lines = []
    for key in all_keys():
        output_lines.append(f"{key} {library[key].info()}")
    return "\n".join(output_lines) + ("\n" if output_lines else "")


def get_item(key: str) -> LibraryItem | None:
    return library.get(key)


def get_name(key: str) -> str | None:
    item = get_item(key)
    return item.name if item is not None else None


def get_artist(key: str) -> str | None:
    item = get_item(key)
    return item.artist if item is not None else None


def get_rating(key: str) -> int | None:
    item = get_item(key)
    return item.rating if item is not None else None


def get_album(key: str) -> str:
    item = get_item(key)
    if isinstance(item, AlbumTrack):
        return item.album
    return ""


def get_year(key: str) -> int | None:
    item = get_item(key)
    if isinstance(item, AlbumTrack):
        return item.year
    return None


def set_rating(key: str, rating: int, auto_save: bool = True) -> bool:
    item = get_item(key)
    if item is None:
        return False
    old_rating = item.rating
    item.set_rating(rating)
    if auto_save and not save_library():
        item.set_rating(old_rating)
        return False
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
    old_item = item
    play_count = item.play_count
    cover_path = item.cover_path
    lyrics = item.lyrics
    audio_path = item.audio_path
    should_be_album_track = album != "" or year is not None
    if should_be_album_track:
        new_item = AlbumTrack(name, artist, rating, play_count, album, year, cover_path, lyrics, audio_path)
    else:
        new_item = LibraryItem(name, artist, rating, play_count, cover_path, lyrics, audio_path)
    library[key] = new_item
    if auto_save and not save_library():
        library[key] = old_item
        return False
    return True


def get_play_count(key: str) -> int | None:
    item = get_item(key)
    return item.play_count if item is not None else None


def increment_play_count(key: str, auto_save: bool = True) -> bool:
    item = get_item(key)
    if item is None:
        return False
    old_count = item.play_count
    item.increment_play_count()
    if auto_save and not save_library():
        item.set_play_count(old_count)
        return False
    return True


def get_details(key: str) -> str | None:
    item = get_item(key)
    return item.details(key) if item is not None else None


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
    numeric_keys = [int(key) for key in library.keys() if key.isdigit()]
    if not numeric_keys:
        return "01"
    return str(max(numeric_keys) + 1).zfill(2)


def add_track(name: str, artist: str, rating: int = 0, album: str = "", year: int | None = None) -> str | None:
    name = name.strip()
    artist = artist.strip()
    album = album.strip()
    if name == "" or artist == "":
        return None
    key = get_next_key()
    if album != "" or year is not None:
        library[key] = AlbumTrack(name, artist, rating, 0, album, year)
    else:
        library[key] = LibraryItem(name, artist, rating)
    if not save_library():
        del library[key]
        return None
    return key


def delete_track(key: str) -> bool:
    if key not in library:
        return False
    old_item = library[key]
    del library[key]
    if not save_library():
        library[key] = old_item
        return False
    return True


def get_track_records() -> list[dict]:
    records = []
    for key in all_keys():
        item = library[key]
        records.append(
            {
                "key": key,
                "name": item.name,
                "artist": item.artist,
                "album": item.album if isinstance(item, AlbumTrack) else "",
                "year": item.year if isinstance(item, AlbumTrack) else None,
                "rating": item.rating,
                "play_count": item.play_count,
                "type": item.__class__.__name__,
            }
        )
    return records


def get_statistics() -> dict:
    tracks = get_track_records()
    total_tracks = len(tracks)
    total_plays = sum(track["play_count"] for track in tracks)
    average_rating = 0.0 if total_tracks == 0 else sum(track["rating"] for track in tracks) / total_tracks
    most_played = max(tracks, key=lambda track: track["play_count"], default=None)
    highest_rated = max(tracks, key=lambda track: track["rating"], default=None)
    album_tracks = sum(1 for track in tracks if track["type"] == "AlbumTrack")
    standard_tracks = total_tracks - album_tracks
    return {
        "tracks": tracks,
        "total_tracks": total_tracks,
        "total_plays": total_plays,
        "average_rating": average_rating,
        "most_played": most_played,
        "highest_rated": highest_rated,
        "album_tracks": album_tracks,
        "standard_tracks": standard_tracks,
    }


load_library()
