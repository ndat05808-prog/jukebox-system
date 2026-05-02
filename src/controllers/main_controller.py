"""Main JukeBox controller: orchestrates the main view, pages, and playback model."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from ..models import audio_manager
from ..models import audio_player
from ..models import cover_manager
from ..models import track_library as lib
from ..models.validation import normalise_track_number
from ..views import font_manager as fonts
from ..views.main_view import MainView
from ..views.pages import (
    LibraryPage,
    ManagePage,
    NowPlayingPage,
    PlaylistsPage,
    StatisticsPage,
)
from ..views.view_tracks import TrackViewer


class JukeBoxApp:
    def __init__(self, current_user: str = "Guest", on_logout=None):
        self.view = MainView(current_user=current_user)
        self.window = self.view.window
        self.current_user = self.view.current_user
        self.on_logout = on_logout

        self.current_track_key: str | None = None
        self.selected_track_key: str | None = None
        self.is_playing = False
        self.queue: list[str] = []
        self.queue_index: int | None = None
        self.player_cover_image = None
        self._progress_dragging = False
        self._tick_job = None
        self._pages: dict[str, object] = {}
        self._active_page = "now_playing"
        self._child_pages: dict[str, object] = {}
        self._view_tracks_window = None

        cover_manager.backfill_cover_paths()
        audio_manager.backfill_audio_paths()

        self._wire_view_callbacks()

        self._build_pages()
        self.switch_page("now_playing")
        self._refresh_player_bar()

        audio_player.set_volume(self.view.volume.get() / 100.0)
        self.view.update_volume_visuals(self.view.volume.get())
        self.window.after(300, self._tick_progress)

    def _wire_view_callbacks(self):
        self.view.on_nav_click = self.switch_page
        self.view.on_view_tracks = self.open_view_tracks_window
        self.view.on_logout = self.logout
        self.view.on_close = self._on_close
        self.view.on_play_pause = self.toggle_play
        self.view.on_previous = self._player_previous
        self.view.on_next = self._player_next
        self.view.on_volume_change = self._on_volume_change
        self.view.on_volume_up = self._volume_up
        self.view.on_volume_down = self._volume_down
        self.view.on_progress_press = self._on_progress_press
        self.view.on_progress_release = self._on_progress_release

    # --- Page registration / navigation ---

    def _build_pages(self):
        self._pages["now_playing"] = NowPlayingPage(self.view.page_host, self).frame
        self._pages["library"] = LibraryPage(self.view.page_host, self).frame
        self._pages["manage"] = ManagePage(self.view.page_host, self).frame
        self._pages["playlists"] = PlaylistsPage(self.view.page_host, self).frame
        self._pages["statistics"] = StatisticsPage(self.view.page_host, self).frame

        for frame in self._pages.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def switch_page(self, key: str):
        if key not in self._pages:
            return
        self._active_page = key
        self._pages[key].tkraise()

        self.view.highlight_nav(key)

        handler = self._child_pages.get(key)
        if handler and hasattr(handler, "on_show"):
            handler.on_show()

    def register_page(self, key: str, handler):
        self._child_pages[key] = handler

    def open_view_tracks_window(self):
        if self._view_tracks_window is not None:
            try:
                if self._view_tracks_window.winfo_exists():
                    self._view_tracks_window.lift()
                    self._view_tracks_window.focus_force()
                    return
            except tk.TclError:
                self._view_tracks_window = None

        view_window = tk.Toplevel(self.window)
        self._view_tracks_window = view_window
        TrackViewer(view_window)

        def on_close():
            self._view_tracks_window = None
            view_window.destroy()

        view_window.protocol("WM_DELETE_WINDOW", on_close)

    # --- Player logic ---

    def play_track(self, track_key: str, source: str = "dashboard"):
        track_key = normalise_track_number(track_key)
        if track_key is None:
            self.status("Track number must contain digits only.")
            return False
        if lib.get_name(track_key) is None:
            self.status(f"Track {track_key} does not exist.")
            return False

        audio_path = audio_manager.find_audio_path(track_key)
        if audio_path is None:
            messagebox.showwarning(
                "No audio file",
                f"Track {track_key} does not have an audio file attached.",
                parent=self.window,
            )
            return False

        if not audio_player.load_and_play(audio_path):
            messagebox.showerror(
                "Playback failed",
                f"Could not play audio file: {audio_path.name}",
                parent=self.window,
            )
            return False

        audio_player.set_volume(self.view.volume.get() / 100.0)

        if not lib.increment_play_count(track_key, auto_save=False):
            self.status(f"Track {track_key} could not be played.")
            return False

        lib.add_history_entry(track_key, source=source)
        lib.save_library()

        self.current_track_key = track_key
        self.selected_track_key = track_key
        self.is_playing = True

        self.view.progress.set(0)
        self._refresh_player_bar()
        self._notify_pages_refresh()

        if not (source.startswith("playlist") or source == "queue"):
            self.clear_queue()

        self.status(f"Now playing: {lib.get_name(track_key)}")
        return True

    def set_queue(self, keys: list[str], index: int = 0):
        self.queue = list(keys)
        if self.queue and 0 <= index < len(self.queue):
            self.queue_index = index
        else:
            self.queue_index = None

    def clear_queue(self):
        self.queue = []
        self.queue_index = None

    def toggle_play(self):
        if self.current_track_key is None or not audio_player.is_loaded():
            records = lib.get_track_records()
            if records:
                self.play_track(records[0]["key"])
            return

        if audio_player.is_paused():
            audio_player.resume()
            self.is_playing = True
            self.status("Playing")
        else:
            audio_player.pause()
            self.is_playing = False
            self.status("Paused")
        self.view.play_btn.configure(text="⏸" if self.is_playing else "▶")

    def _player_previous(self):
        if self.queue and self.queue_index is not None:
            prev_idx = self.queue_index - 1
            if prev_idx >= 0:
                self.queue_index = prev_idx
                self.play_track(self.queue[prev_idx], source="queue")
                return
        records = lib.get_track_records()
        if not records:
            return
        keys = [r["key"] for r in records]
        if self.current_track_key not in keys:
            self.play_track(keys[0])
            return
        idx = keys.index(self.current_track_key)
        self.play_track(keys[(idx - 1) % len(keys)])

    def _player_next(self):
        if self.queue and self.queue_index is not None:
            next_idx = self.queue_index + 1
            if next_idx < len(self.queue):
                self.queue_index = next_idx
                self.play_track(self.queue[next_idx], source="queue")
                return
        records = lib.get_track_records()
        if not records:
            return
        keys = [r["key"] for r in records]
        if self.current_track_key not in keys:
            self.play_track(keys[0])
            return
        idx = keys.index(self.current_track_key)
        self.play_track(keys[(idx + 1) % len(keys)])

    def _refresh_player_bar(self):
        if self.current_track_key is None:
            self.view.player_title_lbl.configure(text="No track loaded")
            self.view.player_artist_lbl.configure(text="Pick a song from your library")
            self.player_cover_image = None
            self.view.player_cover_canvas.delete("all")
            self._draw_cover_placeholder(self.view.player_cover_canvas, 56, "♪")
            self.view.play_btn.configure(text="▶")
            self.view.time_cur_lbl.configure(text="0:00")
            self.view.time_total_lbl.configure(text="0:00")
            return

        item = lib.get_item(self.current_track_key)
        if item is None:
            self.current_track_key = None
            self._refresh_player_bar()
            return

        self.view.player_title_lbl.configure(text=item.name)
        self.view.player_artist_lbl.configure(text=item.artist)

        self.view.player_cover_canvas.delete("all")
        self.player_cover_image = cover_manager.load_cover_image(self.current_track_key, max_size=52)
        if self.player_cover_image is not None:
            self.view.player_cover_canvas.create_image(28, 28, image=self.player_cover_image)
        else:
            self._draw_cover_placeholder(self.view.player_cover_canvas, 56, "♪", accent=True)

        self.view.play_btn.configure(text="⏸" if self.is_playing else "▶")
        self.view.time_cur_lbl.configure(text="0:00")
        self.view.time_total_lbl.configure(
            text=self._format_time(audio_player.get_duration_seconds())
        )

    def _on_volume_change(self, value):
        try:
            pct = float(value)
        except (TypeError, ValueError):
            return
        audio_player.set_volume(pct / 100.0)
        self.view.update_volume_visuals(pct)

    def _volume_up(self):
        self.view.volume.set(min(100, int(self.view.volume.get()) + 5))

    def _volume_down(self):
        self.view.volume.set(max(0, int(self.view.volume.get()) - 5))

    def _on_progress_press(self, event=None):
        self._progress_dragging = True

    def _on_progress_release(self, event=None):
        self._progress_dragging = False
        duration = audio_player.get_duration_seconds()
        if duration <= 0 or not audio_player.is_loaded():
            return
        target_seconds = (self.view.progress.get() / 100.0) * duration
        audio_player.seek(target_seconds)

    def _tick_progress(self):
        try:
            if audio_player.is_loaded():
                duration = audio_player.get_duration_seconds()
                position = audio_player.get_position_seconds()

                if duration > 0 and not self._progress_dragging:
                    ratio = max(0.0, min(100.0, (position / duration) * 100.0))
                    self.view.progress.set(ratio)

                self.view.time_cur_lbl.configure(text=self._format_time(position))
                self.view.time_total_lbl.configure(text=self._format_time(duration))

                if self.is_playing and not audio_player.is_playing() and not audio_player.is_paused():
                    self.is_playing = False
                    self.view.play_btn.configure(text="▶")
        finally:
            self._tick_job = self.window.after(300, self._tick_progress)

    @staticmethod
    def _format_time(seconds: float) -> str:
        if seconds <= 0:
            return "0:00"
        total = int(seconds)
        return f"{total // 60}:{total % 60:02d}"

    def _on_close(self):
        if self._tick_job is not None:
            try:
                self.window.after_cancel(self._tick_job)
            except tk.TclError:
                pass
            self._tick_job = None
        audio_player.stop()
        self.window.destroy()

    def _draw_cover_placeholder(
        self, canvas: tk.Canvas, size: int, glyph: str, accent: bool = False
    ):
        canvas.delete("all")
        pad = max(2, size // 16)
        outline = fonts.ACCENT if accent else fonts.BORDER_SOFT
        fill = fonts.CARD_ALT
        canvas.create_rectangle(pad, pad, size - pad, size - pad, outline=outline, fill=fill, width=1)
        canvas.create_text(
            size // 2,
            size // 2,
            text=glyph,
            fill=fonts.ACCENT_GLOW if accent else fonts.MUTED,
            font=fonts._ff(max(14, size // 3), "bold"),
        )

    # --- Broadcast helpers ---

    def _notify_pages_refresh(self):
        for handler in self._child_pages.values():
            if hasattr(handler, "on_library_change"):
                handler.on_library_change()

    def refresh_library(self):
        self._notify_pages_refresh()
        self._refresh_player_bar()

    # --- Session ---

    def status(self, text: str):
        self.view.set_status_title(text)

    def logout(self):
        confirmed = messagebox.askyesno(
            "Log Out",
            f"Are you sure you want to sign out '{self.current_user}'?",
            parent=self.window,
        )
        if not confirmed:
            return

        if self._tick_job is not None:
            try:
                self.window.after_cancel(self._tick_job)
            except tk.TclError:
                pass
            self._tick_job = None
        audio_player.stop()

        self.window.destroy()

        if callable(self.on_logout):
            self.on_logout()

    def run(self):
        self.view.run()


def main():
    app = JukeBoxApp(current_user="Guest")
    app.run()


if __name__ == "__main__":
    main()
