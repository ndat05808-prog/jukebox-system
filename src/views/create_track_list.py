import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from ..models import audio_manager
from ..models import audio_player
from . import font_manager as fonts
from ..models import track_library as lib
from .gui_helpers import bind_two_column_stacking, clear_tree, setup_page_container, stars_text
from ..models.validation import get_valid_position, normalise_playlist_name, normalise_track_number

PROJECT_DIR = Path(__file__).resolve().parent.parent
PLAYLIST_DIR = PROJECT_DIR / "playlists"
PLAYLIST_DIR.mkdir(exist_ok=True)


class CreateTrackList:
    def __init__(self, window):
        self.window = window
        self.app_ref = None
        self.playlist: list[str] = []
        self.current_index = None
        self.is_playing = False
        self.is_paused = False
        self._autoplay = False
        self._was_playing_last_tick = False
        self._tick_job = None

        setup_page_container(
            window,
            title="Playlist Builder",
            geometry="1380x820",
            minsize=(1180, 740),
        )

        window.columnconfigure(0, weight=3)
        window.columnconfigure(1, weight=2)
        window.rowconfigure(2, weight=1)

        # Header riêng để tiêu đề không bị chồng lên mô tả
        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Playlist Builder",
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            header,
            text="Refined into a clearer workspace while keeping your save/load logic.",
            style="Muted.TLabel"
        ).grid(row=1, column=0, sticky="w")

        self._build_toolbar()
        self._build_main_panels()

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.list_tracks_clicked()
        self.refresh_playlist_tree()

        try:
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        except AttributeError:
            self.window.bind("<Destroy>", self._on_destroy, add="+")
        self._tick_job = self.window.after(400, self._tick_playback)

    def _build_toolbar(self):
        toolbar_card = ttk.Frame(self.window, style="Card.TFrame", padding=18)
        toolbar_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))
        toolbar_card.columnconfigure(0, weight=2, uniform="tb")
        toolbar_card.columnconfigure(1, weight=3, uniform="tb")

        # ---- Add to Playlist section ----
        add_section = ttk.Frame(toolbar_card, style="Card.TFrame")
        add_section.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        add_section.columnconfigure(1, weight=1)

        ttk.Label(add_section, text="ADD TO PLAYLIST", style="Tag.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        ttk.Label(add_section, text="Track #", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8))

        self.input_txt = ttk.Entry(add_section)
        self.input_txt.grid(row=1, column=1, sticky="ew", padx=(0, 8))
        self.input_txt.bind("<Return>", lambda event: self.add_track_clicked())

        ttk.Button(
            add_section,
            text="Add Track",
            style="Neon.TButton",
            command=self.add_track_clicked,
        ).grid(row=1, column=2, sticky="ew")

        ttk.Label(
            add_section,
            text="Tip: double-click a library row to add it instantly.",
            style="Muted.TLabel",
            font=fonts._ff(9),
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))

        # ---- Playback section ----
        play_section = ttk.Frame(toolbar_card, style="Card.TFrame")
        play_section.grid(row=0, column=1, sticky="nsew")
        for i in range(4):
            play_section.columnconfigure(i, weight=1, uniform="play")

        ttk.Label(play_section, text="PLAYBACK", style="Tag.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8)
        )

        ttk.Button(
            play_section,
            text="▶  Play All",
            style="Neon.TButton",
            command=self.play_playlist_clicked,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            play_section,
            text="Load Current",
            style="Ghost.TButton",
            command=self.load_current_track_clicked,
        ).grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ttk.Button(
            play_section,
            text="Pause / Resume",
            style="Ghost.TButton",
            command=self.pause_resume_clicked,
        ).grid(row=1, column=2, sticky="ew", padx=(0, 6))

        ttk.Button(
            play_section,
            text="⏭  Skip",
            style="Ghost.TButton",
            command=self.skip_track_clicked,
        ).grid(row=1, column=3, sticky="ew")

    def _build_main_panels(self):
        left = ttk.Frame(self.window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        right = ttk.Frame(self.window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=0)

        bind_two_column_stacking(
            self.window, left, right,
            breakpoint=960, left_weight=3, right_weight=2,
        )

        # Library card
        library_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        library_card.grid(row=0, column=0, sticky="nsew")
        library_card.columnconfigure(0, weight=1)
        library_card.rowconfigure(1, weight=1)

        ttk.Label(
            library_card,
            text="Library",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        library_wrap = ttk.Frame(library_card, style="Card.TFrame")
        library_wrap.grid(row=1, column=0, sticky="nsew")
        library_wrap.columnconfigure(0, weight=1)
        library_wrap.rowconfigure(0, weight=1)

        self.library_tree = ttk.Treeview(
            library_wrap,
            columns=("key", "title", "artist", "album", "rating"),
            show="headings"
        )

        config = {
            "key": ("#", 55),
            "title": ("Song Title", 260),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "rating": ("Rating", 120),
        }

        for column, (label, width) in config.items():
            self.library_tree.heading(column, text=label)
            self.library_tree.column(column, width=width, anchor="w", stretch=True)

        library_y_scroll = ttk.Scrollbar(library_wrap, orient="vertical", command=self.library_tree.yview)
        library_x_scroll = ttk.Scrollbar(library_wrap, orient="horizontal", command=self.library_tree.xview)
        self.library_tree.configure(
            yscrollcommand=library_y_scroll.set,
            xscrollcommand=library_x_scroll.set
        )

        self.library_tree.grid(row=0, column=0, sticky="nsew")
        library_y_scroll.grid(row=0, column=1, sticky="ns")
        library_x_scroll.grid(row=1, column=0, sticky="ew")

        self.library_tree.bind("<Double-1>", self._double_click_library)

        # Playlist card
        playlist_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        playlist_card.grid(row=0, column=0, sticky="nsew")
        playlist_card.columnconfigure(0, weight=1)
        playlist_card.rowconfigure(1, weight=1)

        ttk.Label(
            playlist_card,
            text="Current Playlist",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        playlist_wrap = ttk.Frame(playlist_card, style="Card.TFrame")
        playlist_wrap.grid(row=1, column=0, sticky="nsew")
        playlist_wrap.columnconfigure(0, weight=1)
        playlist_wrap.rowconfigure(0, weight=1)

        # Action bar under the tree: position + remove / move buttons
        action_bar = ttk.Frame(playlist_card, style="Card.TFrame")
        action_bar.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        action_bar.columnconfigure(1, weight=1)
        for col in range(2, 5):
            action_bar.columnconfigure(col, weight=1, uniform="pl_actions")

        ttk.Label(action_bar, text="Position", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )

        self.position_input = ttk.Entry(action_bar, width=6)
        self.position_input.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        # Aliases keep existing handlers working unchanged
        self.remove_input = self.position_input
        self.move_input = self.position_input

        ttk.Button(
            action_bar,
            text="Remove",
            style="Danger.TButton",
            command=self.remove_track_clicked,
        ).grid(row=0, column=2, sticky="ew", padx=(0, 6))

        ttk.Button(
            action_bar,
            text="Move Up",
            style="Ghost.TButton",
            command=self.move_up_clicked,
        ).grid(row=0, column=3, sticky="ew", padx=(0, 6))

        ttk.Button(
            action_bar,
            text="Move Down",
            style="Ghost.TButton",
            command=self.move_down_clicked,
        ).grid(row=0, column=4, sticky="ew")

        self.playlist_tree = ttk.Treeview(
            playlist_wrap,
            columns=("position", "track", "title", "state"),
            show="headings"
        )

        for column, label, width in (
            ("position", "Pos", 60),
            ("track", "Track", 70),
            ("title", "Song Title", 250),
            ("state", "State", 130),
        ):
            self.playlist_tree.heading(column, text=label)
            self.playlist_tree.column(column, width=width, anchor="w", stretch=True)

        playlist_y_scroll = ttk.Scrollbar(playlist_wrap, orient="vertical", command=self.playlist_tree.yview)
        playlist_x_scroll = ttk.Scrollbar(playlist_wrap, orient="horizontal", command=self.playlist_tree.xview)
        self.playlist_tree.configure(
            yscrollcommand=playlist_y_scroll.set,
            xscrollcommand=playlist_x_scroll.set
        )

        self.playlist_tree.grid(row=0, column=0, sticky="nsew")
        playlist_y_scroll.grid(row=0, column=1, sticky="ns")
        playlist_x_scroll.grid(row=1, column=0, sticky="ew")

        self.playlist_tree.bind("<<TreeviewSelect>>", self._select_playlist_position)

        # Playlist files card
        controls_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        controls_card.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        for i in range(2):
            controls_card.columnconfigure(i, weight=1, uniform="pl_files")

        ttk.Label(
            controls_card,
            text="Playlist Files",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(
            controls_card,
            text="Playlist name",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 4))

        self.playlist_name_input = ttk.Combobox(controls_card, values=self._list_playlist_names())
        self.playlist_name_input.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.playlist_name_input.set("")
        self.playlist_name_input.bind("<<ComboboxSelected>>", self._on_playlist_picked)

        ttk.Button(
            controls_card,
            text="Save",
            style="Neon.TButton",
            command=self.save_playlist_clicked,
        ).grid(row=3, column=0, sticky="ew", padx=(0, 6), pady=(0, 8))

        ttk.Button(
            controls_card,
            text="Rename",
            style="Ghost.TButton",
            command=self.rename_playlist_clicked,
        ).grid(row=3, column=1, sticky="ew", padx=(6, 0), pady=(0, 8))

        ttk.Button(
            controls_card,
            text="Create New",
            style="Ghost.TButton",
            command=self.create_new_playlist_clicked,
        ).grid(row=4, column=0, sticky="ew", padx=(0, 6), pady=(0, 8))

        ttk.Button(
            controls_card,
            text="Reset",
            style="Danger.TButton",
            command=self.reset_playlist_clicked,
        ).grid(row=4, column=1, sticky="ew", padx=(6, 0), pady=(0, 8))

        ttk.Button(
            controls_card,
            text="Delete File",
            style="Danger.TButton",
            command=self.delete_playlist_clicked,
        ).grid(row=5, column=0, columnspan=2, sticky="ew")

    def _double_click_library(self, event=None):
        selected = self.library_tree.selection()
        if not selected:
            return
        values = self.library_tree.item(selected[0], "values")
        self.input_txt.delete(0, tk.END)
        self.input_txt.insert(0, values[0])
        self.add_track_clicked()

    def _select_playlist_position(self, event=None):
        selected = self.playlist_tree.selection()
        if not selected:
            return
        values = self.playlist_tree.item(selected[0], "values")
        self.position_input.delete(0, tk.END)
        self.position_input.insert(0, values[0])

    def _reset_playback_state(self):
        self.current_index = None
        self.is_playing = False
        self.is_paused = False
        self._autoplay = False
        self._was_playing_last_tick = False

    def _tick_playback(self):
        try:
            if (
                self.app_ref is not None
                and self.app_ref.queue == self.playlist
                and self.app_ref.queue_index is not None
                and self.app_ref.queue_index != self.current_index
            ):
                self.current_index = self.app_ref.queue_index
                self.is_playing = self.app_ref.is_playing
                self.is_paused = False
                self._autoplay = True
                self._was_playing_last_tick = audio_player.is_playing()
                self.refresh_playlist_tree()
                track_key = self.playlist[self.current_index]
                track_name = lib.get_name(track_key) or "Unknown Track"
                self.status_lbl.configure(
                    text=f"Now playing: '{track_name}' (track {track_key})."
                )

            if self.is_playing and not audio_player.is_paused():
                if self._was_playing_last_tick and not audio_player.is_playing():
                    self._on_track_finished()
                self._was_playing_last_tick = audio_player.is_playing()
        except tk.TclError:
            self._tick_job = None
            return
        try:
            self._tick_job = self.window.after(400, self._tick_playback)
        except tk.TclError:
            self._tick_job = None

    def _on_track_finished(self):
        if not self._autoplay or self.current_index is None or len(self.playlist) == 0:
            self.is_playing = False
            self.is_paused = False
            self._was_playing_last_tick = False
            self.refresh_playlist_tree()
            self.status_lbl.configure(text="Track finished.")
            return

        next_index = self.current_index + 1
        if next_index >= len(self.playlist):
            self.is_playing = False
            self.is_paused = False
            self._autoplay = False
            self._was_playing_last_tick = False
            self.refresh_playlist_tree()
            self.status_lbl.configure(text="Playlist finished.")
            return

        self.current_index = next_index
        self._play_current_track(source="playlist_auto")

    def _on_close(self):
        self._stop_tick_and_audio()
        self.window.destroy()

    def _on_destroy(self, event=None):
        if event is not None and event.widget is not self.window:
            return
        self._stop_tick_and_audio()

    def _stop_tick_and_audio(self):
        if self._tick_job is not None:
            try:
                self.window.after_cancel(self._tick_job)
            except Exception:
                pass
            self._tick_job = None
        try:
            audio_player.stop()
        except Exception:
            pass

    def _remove_missing_tracks(self, show_status=False):
        removed_keys = []
        valid_keys = []
        for track_key in self.playlist:
            if lib.get_name(track_key) is None:
                removed_keys.append(track_key)
            else:
                valid_keys.append(track_key)

        if removed_keys:
            self.playlist = valid_keys
            if len(self.playlist) == 0:
                self._reset_playback_state()
            elif self.current_index is not None and self.current_index >= len(self.playlist):
                self.current_index = len(self.playlist) - 1

            if show_status:
                self.status_lbl.configure(
                    text=f"Removed {len(removed_keys)} missing track(s) from the playlist."
                )
        return removed_keys

    def _play_current_track(self, source="playlist_single"):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return False

        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0

        track_key = self.playlist[self.current_index]
        track_name = lib.get_name(track_key) or "Unknown Track"

        if self.app_ref is not None:
            self.app_ref.set_queue(self.playlist, self.current_index)
            ok = self.app_ref.play_track(track_key, source=source)
        else:
            ok = self._play_track_standalone(track_key, source=source)

        if not ok:
            self.is_playing = False
            self.is_paused = False
            self._was_playing_last_tick = False
            self.refresh_playlist_tree()
            return False

        self.is_playing = True
        self.is_paused = False
        self._was_playing_last_tick = True
        self.refresh_playlist_tree()
        self.list_tracks_clicked()
        self.status_lbl.configure(text=f"Now playing: '{track_name}' (track {track_key}).")
        return True

    def _play_track_standalone(self, track_key, source):
        audio_path = audio_manager.find_audio_path(track_key)
        if audio_path is None:
            messagebox.showwarning(
                "No audio attached",
                f"Track {track_key} has no audio file attached.",
                parent=self.window,
            )
            return False
        if not audio_player.load_and_play(audio_path):
            messagebox.showerror(
                "Playback failed",
                f"Could not play track {track_key}.",
                parent=self.window,
            )
            return False
        if lib.increment_play_count(track_key, auto_save=False):
            lib.add_history_entry(track_key, source=source)
            lib.save_library()
        return True

    def list_tracks_clicked(self):
        clear_tree(self.library_tree)
        for record in lib.get_track_records():
            self.library_tree.insert(
                "",
                "end",
                values=(
                    record["key"],
                    record["name"],
                    record["artist"],
                    record["album"] or "—",
                    stars_text(record["rating"]),
                ),
            )
        self.status_lbl.configure(text="Library tracks are displayed.")

    def refresh_playlist_tree(self):
        self._remove_missing_tracks(show_status=False)
        clear_tree(self.playlist_tree)

        if not self.playlist:
            self.status_lbl.configure(text="Playlist is empty.")
            return

        for number, track_key in enumerate(self.playlist, start=1):
            title = lib.get_name(track_key) or "[Missing Track]"
            state = "Ready"

            if self.current_index == number - 1:
                if self.is_playing:
                    state = "Playing"
                elif self.is_paused:
                    state = "Paused"
                else:
                    state = "Loaded"

            self.playlist_tree.insert("", "end", values=(number, track_key, title, state))

    def add_track_clicked(self):
        track_key = normalise_track_number(self.input_txt.get())
        if track_key is None:
            self.status_lbl.configure(text="Please enter digits only for the track number.")
            return

        track_name = lib.get_name(track_key)
        if track_name is None:
            self.status_lbl.configure(text=f"Track {track_key} does not exist.")
            return

        self.playlist.append(track_key)
        self.refresh_playlist_tree()
        self.input_txt.delete(0, tk.END)
        self.status_lbl.configure(text=f"Added '{track_name}' to the playlist.")

    def remove_track_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="There is nothing to remove because the playlist is empty.")
            return

        position = get_valid_position(self.remove_input.get(), len(self.playlist))
        if position is None:
            self.status_lbl.configure(text=f"Enter a valid position between 1 and {len(self.playlist)}.")
            return

        removed_index = position - 1
        removed_key = self.playlist.pop(removed_index)
        removed_name = lib.get_name(removed_key) or "Unknown Track"

        if len(self.playlist) == 0:
            audio_player.stop()
            self._reset_playback_state()
        elif self.current_index is not None:
            if removed_index < self.current_index:
                self.current_index -= 1
            elif removed_index == self.current_index:
                audio_player.stop()
                self.is_playing = False
                self.is_paused = False
                self._was_playing_last_tick = False
                if self.current_index >= len(self.playlist):
                    self.current_index = len(self.playlist) - 1

        self.refresh_playlist_tree()
        self.remove_input.delete(0, tk.END)
        self.status_lbl.configure(text=f"Removed '{removed_name}' from position {position}.")

    def _get_move_position(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty, so there is nothing to move.")
            return None

        position = get_valid_position(self.move_input.get(), len(self.playlist))
        if position is None:
            self.status_lbl.configure(text=f"Enter a valid position between 1 and {len(self.playlist)}.")
            return None
        return position

    def move_up_clicked(self):
        position = self._get_move_position()
        if position is None:
            return
        if position == 1:
            self.status_lbl.configure(text="That track is already at the top of the playlist.")
            return

        index = position - 1
        self.playlist[index - 1], self.playlist[index] = self.playlist[index], self.playlist[index - 1]

        if self.current_index == index:
            self.current_index -= 1
        elif self.current_index == index - 1:
            self.current_index += 1

        self.refresh_playlist_tree()
        self.status_lbl.configure(text=f"Moved the track from position {position} to {position - 1}.")

    def move_down_clicked(self):
        position = self._get_move_position()
        if position is None:
            return
        if position == len(self.playlist):
            self.status_lbl.configure(text="That track is already at the bottom of the playlist.")
            return

        index = position - 1
        self.playlist[index], self.playlist[index + 1] = self.playlist[index + 1], self.playlist[index]

        if self.current_index == index:
            self.current_index += 1
        elif self.current_index == index + 1:
            self.current_index -= 1

        self.refresh_playlist_tree()
        self.status_lbl.configure(text=f"Moved the track from position {position} to {position + 1}.")

    def load_current_track_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return

        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0

        self._autoplay = False
        self._play_current_track(source="playlist_load")

    def play_playlist_clicked(self):
        self._remove_missing_tracks(show_status=False)

        # Stop the function if the playlist has no tracks.
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return

        audio_player.stop()
        self._reset_playback_state()

        played_count = 0

        for track_key in self.playlist:
            if lib.increment_play_count(track_key, auto_save=False):
                lib.add_history_entry(track_key, source="playlist", action="play")
                played_count += 1

        lib.save_library()

        self.refresh_playlist_tree()
        self.list_tracks_clicked()

        if self.app_ref is not None:
            self.app_ref.refresh_library()

        self.status_lbl.configure(
            text=f"Simulated playlist play complete: {played_count} track(s) had their play count increased by 1."
        )

    def pause_resume_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return

        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.status_lbl.configure(text="Load or play a track first.")
            return

        track_key = self.playlist[self.current_index]
        track_name = lib.get_name(track_key) or "Unknown Track"

        if self.is_playing:
            if self.app_ref is not None:
                self.app_ref.toggle_play()
            else:
                audio_player.pause()
            self.is_playing = False
            self.is_paused = True
            self._was_playing_last_tick = False
            self.refresh_playlist_tree()
            self.status_lbl.configure(text=f"Paused '{track_name}'.")
        elif self.is_paused:
            if self.app_ref is not None:
                self.app_ref.toggle_play()
            else:
                audio_player.resume()
            self.is_playing = True
            self.is_paused = False
            self._was_playing_last_tick = True
            self.refresh_playlist_tree()
            self.status_lbl.configure(text=f"Resumed '{track_name}'.")
        else:
            self.status_lbl.configure(text="Track is loaded but not playing.")

    def skip_track_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return

        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)

        self._play_current_track(source="playlist_skip")

    def reset_playlist_clicked(self):
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is already empty.")
            return

        confirmed = messagebox.askyesno(
            "Reset Playlist",
            "Are you sure you want to clear the current playlist?",
            parent=self.window
        )
        if not confirmed:
            self.status_lbl.configure(text="Reset playlist cancelled.")
            return

        audio_player.stop()
        self.playlist.clear()
        self._reset_playback_state()
        clear_tree(self.playlist_tree)
        self.status_lbl.configure(text="Playlist reset complete.")

    def _get_playlist_path(self):
        playlist_name = normalise_playlist_name(self.playlist_name_input.get())
        if playlist_name is None:
            return None
        return PLAYLIST_DIR / f"{playlist_name}.txt"

    def _list_playlist_names(self):
        return sorted(path.stem for path in PLAYLIST_DIR.glob("*.txt"))

    def _refresh_playlist_choices(self):
        self.playlist_name_input.configure(values=self._list_playlist_names())

    def _on_playlist_picked(self, event=None):
        if self.playlist_name_input.get().strip():
            self.load_playlist_clicked()

    def create_new_playlist_clicked(self):
        new_name_text = simpledialog.askstring(
            "Create New Playlist",
            "Enter the new playlist name:",
            parent=self.window
        )
        if new_name_text is None:
            self.status_lbl.configure(text="Create new playlist cancelled.")
            return

        new_name = normalise_playlist_name(new_name_text)
        if new_name is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return

        new_path = PLAYLIST_DIR / f"{new_name}.txt"
        if new_path.exists():
            self.status_lbl.configure(text="A playlist with that name already exists.")
            return

        audio_player.stop()
        self.playlist.clear()
        self._reset_playback_state()
        clear_tree(self.playlist_tree)
        self.playlist_name_input.set(new_name)

        try:
            new_path.write_text("", encoding="utf-8")
        except OSError:
            self.status_lbl.configure(text="Could not create the new playlist file.")
            return

        self._refresh_playlist_choices()
        self.status_lbl.configure(text=f"Created new playlist '{new_name}'.")

    def save_playlist_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="Nothing to save because the playlist is empty.")
            return

        path = self._get_playlist_path()
        if path is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return

        try:
            path.write_text("\n".join(self.playlist), encoding="utf-8")
        except OSError:
            self.status_lbl.configure(text="Could not save the playlist file.")
            return

        self._refresh_playlist_choices()
        self.status_lbl.configure(text=f"Playlist saved to {path.stem}.")

    def load_playlist_clicked(self):
        path = self._get_playlist_path()
        if path is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return

        if not path.exists():
            self.status_lbl.configure(text="That playlist does not exist yet.")
            return

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            self.status_lbl.configure(text="Could not load the playlist file.")
            return

        loaded_playlist = []
        skipped_count = 0
        for track_key in lines:
            if lib.get_name(track_key) is not None:
                loaded_playlist.append(track_key)
            else:
                skipped_count += 1

        audio_player.stop()
        self.playlist = loaded_playlist
        self._reset_playback_state()
        self.refresh_playlist_tree()

        if skipped_count > 0:
            self.status_lbl.configure(
                text=f"Loaded {len(self.playlist)} track(s) from {path.stem}. Skipped {skipped_count} missing track(s)."
            )
        else:
            self.status_lbl.configure(text=f"Loaded {len(self.playlist)} track(s) from {path.stem}.")

    def rename_playlist_clicked(self):
        old_path = self._get_playlist_path()
        if old_path is None:
            self.status_lbl.configure(text="Please enter the current playlist name first.")
            return

        if not old_path.exists():
            self.status_lbl.configure(text="That playlist does not exist yet.")
            return

        new_name_text = simpledialog.askstring(
            "Rename Playlist",
            "Enter the new playlist name:",
            parent=self.window
        )
        if new_name_text is None:
            self.status_lbl.configure(text="Rename cancelled.")
            return

        new_name = normalise_playlist_name(new_name_text)
        if new_name is None:
            self.status_lbl.configure(text="Please enter a valid new playlist name.")
            return

        new_path = PLAYLIST_DIR / f"{new_name}.txt"
        if old_path == new_path:
            self.status_lbl.configure(text="The new playlist name is the same as the current name.")
            return

        if new_path.exists():
            self.status_lbl.configure(text="A playlist with that name already exists.")
            return

        try:
            old_path.rename(new_path)
        except OSError:
            self.status_lbl.configure(text="Could not rename the playlist file.")
            return

        self.playlist_name_input.set(new_name)
        self._refresh_playlist_choices()
        self.status_lbl.configure(text=f"Renamed playlist to {new_name}.")
        messagebox.showinfo(
            "Playlist renamed",
            f"Renamed to '{new_name}'.",
            parent=self.window,
        )

    def delete_playlist_clicked(self):
        path = self._get_playlist_path()
        if path is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return

        if not path.exists():
            self.status_lbl.configure(text="That playlist does not exist yet.")
            return

        confirmed = messagebox.askyesno(
            "Delete Playlist",
            f"Are you sure you want to delete '{path.stem}'?",
            parent=self.window
        )
        if not confirmed:
            self.status_lbl.configure(text="Delete playlist cancelled.")
            return

        try:
            path.unlink()
        except OSError:
            self.status_lbl.configure(text="Could not delete the playlist file.")
            return

        deleted_name = path.stem
        remaining = self._list_playlist_names()
        self.playlist_name_input.configure(values=remaining)
        self.playlist_name_input.set(remaining[0] if remaining else "")
        self.status_lbl.configure(text=f"Deleted playlist file {deleted_name}.")
        messagebox.showinfo(
            "Playlist deleted",
            f"Deleted '{deleted_name}'.",
            parent=self.window,
        )


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    CreateTrackList(root)
    root.mainloop()