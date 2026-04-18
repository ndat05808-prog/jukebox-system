from __future__ import annotations

from pathlib import Path

from . import track_library as lib

PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_DIR = ASSETS_DIR / "audio"

SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac")


def _resolve_stored_path(stored: str) -> Path | None:
    candidate = Path(stored)
    if not candidate.is_absolute():
        candidate = PROJECT_DIR / candidate
    return candidate if candidate.exists() else None


def _relative_to_project(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_DIR))
    except ValueError:
        return str(path.resolve())


def find_audio_path(track_key: str | None) -> Path | None:
    if track_key is None:
        return None
    item = lib.get_item(track_key)
    if item is not None and item.audio_path:
        resolved = _resolve_stored_path(item.audio_path)
        if resolved is not None:
            return resolved
    for extension in SUPPORTED_EXTENSIONS:
        candidate = AUDIO_DIR / f"{track_key}{extension}"
        if candidate.exists():
            return candidate
    return None


def assign_audio(track_key: str, src_path: str | Path) -> Path | None:
    src = Path(src_path)
    if not src.is_file():
        return None
    if src.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return None
    if not lib.set_audio_path(track_key, _relative_to_project(src)):
        return None
    return src


def remove_audio(track_key: str) -> bool:
    return lib.set_audio_path(track_key, None)


def has_audio(track_key: str) -> bool:
    item = lib.get_item(track_key)
    if item is None or not item.audio_path:
        return False
    return _resolve_stored_path(item.audio_path) is not None


def backfill_audio_paths() -> int:
    updated = 0
    for key, item in list(lib.library.items()):
        if item.audio_path:
            continue
        for extension in SUPPORTED_EXTENSIONS:
            candidate = AUDIO_DIR / f"{key}{extension}"
            if candidate.exists():
                item.audio_path = _relative_to_project(candidate)
                updated += 1
                break
    if updated:
        lib.save_library()
    return updated
