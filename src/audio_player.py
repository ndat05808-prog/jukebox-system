"""Thin wrapper around ``pygame.mixer`` for streaming track playback."""

from __future__ import annotations

from pathlib import Path

try:
    import pygame
except ImportError:
    pygame = None  # type: ignore[assignment]

_initialised = False
_current_path: Path | None = None
_duration_seconds: float = 0.0
_paused: bool = False


def available() -> bool:
    return pygame is not None


def _ensure_init() -> bool:
    global _initialised
    if pygame is None:
        return False
    if _initialised:
        return True
    try:
        pygame.mixer.init()
    except pygame.error:
        return False
    _initialised = True
    return True


def _probe_duration(path: Path) -> float:
    if pygame is None:
        return 0.0
    try:
        sound = pygame.mixer.Sound(str(path))
    except pygame.error:
        return 0.0
    try:
        return float(sound.get_length())
    except pygame.error:
        return 0.0


def load_and_play(path: Path | str) -> bool:
    global _current_path, _duration_seconds, _paused
    if not _ensure_init():
        return False
    src = Path(path)
    if not src.is_file():
        return False
    try:
        pygame.mixer.music.load(str(src))
        pygame.mixer.music.play()
    except pygame.error:
        return False
    _current_path = src
    _duration_seconds = _probe_duration(src)
    _paused = False
    return True


def pause() -> None:
    global _paused
    if _ensure_init() and pygame.mixer.music.get_busy() and not _paused:
        pygame.mixer.music.pause()
        _paused = True


def resume() -> None:
    global _paused
    if _ensure_init() and _paused:
        pygame.mixer.music.unpause()
        _paused = False


def stop() -> None:
    global _paused, _current_path, _duration_seconds
    if _initialised and pygame is not None:
        pygame.mixer.music.stop()
    _paused = False
    _current_path = None
    _duration_seconds = 0.0


def is_loaded() -> bool:
    return _current_path is not None


def is_playing() -> bool:
    if not _initialised or pygame is None:
        return False
    return pygame.mixer.music.get_busy() and not _paused


def is_paused() -> bool:
    return _paused


def set_volume(fraction: float) -> None:
    if not _ensure_init():
        return
    fraction = max(0.0, min(1.0, fraction))
    pygame.mixer.music.set_volume(fraction)


def get_position_seconds() -> float:
    if not _initialised or pygame is None or _current_path is None:
        return 0.0
    pos_ms = pygame.mixer.music.get_pos()
    if pos_ms < 0:
        return 0.0
    return pos_ms / 1000.0


def get_duration_seconds() -> float:
    return _duration_seconds


def seek(seconds: float) -> bool:
    if not _ensure_init() or _current_path is None:
        return False
    seconds = max(0.0, seconds)
    try:
        pygame.mixer.music.play(start=seconds)
        if _paused:
            pygame.mixer.music.pause()
    except pygame.error:
        return False
    return True
