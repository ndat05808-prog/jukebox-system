from __future__ import annotations

from pathlib import Path
import tkinter as tk

PROJECT_DIR = Path(__file__).resolve().parent
COVERS_DIR = PROJECT_DIR / "assets" / "covers"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = (".png", ".gif", ".ppm", ".pgm")


def _find_cover_path(track_key: str | None) -> Path | None:
    if track_key is not None:
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