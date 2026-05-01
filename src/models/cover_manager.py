from __future__ import annotations

from pathlib import Path
import tkinter as tk

from . import track_library as lib

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
COVERS_DIR = ASSETS_DIR / "covers"

SUPPORTED_EXTENSIONS = (".png", ".gif", ".ppm", ".pgm")


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


def _find_cover_path(track_key: str | None) -> Path | None:
    if track_key is not None:
        item = lib.get_item(track_key)
        if item is not None and item.cover_path:
            resolved = _resolve_stored_path(item.cover_path)
            if resolved is not None:
                return resolved
        for extension in SUPPORTED_EXTENSIONS:
            candidate = COVERS_DIR / f"{track_key}{extension}"
            if candidate.exists():
                return candidate
    for extension in SUPPORTED_EXTENSIONS:
        candidate = COVERS_DIR / f"default{extension}"
        if candidate.exists():
            return candidate
    return None


def load_cover_image(track_key: str | None, max_size: int = 220) -> tk.PhotoImage | None:
    path = _find_cover_path(track_key)
    if path is None:
        return None
    try:
        image = tk.PhotoImage(file=str(path))
    except tk.TclError:
        return None
    width = image.width()
    height = image.height()
    largest_side = max(width, height)
    if largest_side > max_size:
        scale_factor = max(1, (largest_side + max_size - 1) // max_size)
        image = image.subsample(scale_factor, scale_factor)
    return image


def get_cover_folder_text() -> str:
    return f"Put cover images in: {COVERS_DIR}"


def assign_cover_image(track_key: str, src_path: str | Path) -> Path | None:
    src = Path(src_path)
    if not src.is_file():
        return None

    extension = src.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        return None

    if not lib.set_cover_path(track_key, _relative_to_project(src)):
        return None
    return src


def remove_cover_image(track_key: str) -> bool:
    return lib.set_cover_path(track_key, None)


def has_custom_cover(track_key: str) -> bool:
    item = lib.get_item(track_key)
    if item is None or not item.cover_path:
        return False
    return _resolve_stored_path(item.cover_path) is not None


def find_cover_path(track_key: str | None) -> Path | None:
    return _find_cover_path(track_key)


def backfill_cover_paths() -> int:
    updated = 0
    for key, item in list(lib.library.items()):
        if item.cover_path:
            continue
        for extension in SUPPORTED_EXTENSIONS:
            candidate = COVERS_DIR / f"{key}{extension}"
            if candidate.exists():
                item.cover_path = _relative_to_project(candidate)
                updated += 1
                break
    if updated:
        lib.save_library()
    return updated
