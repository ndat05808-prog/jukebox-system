import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import set_text


TEXT_BG = "#FFFFFF"
TEXT_FG = "#111827"


class TrackStatistics:
    def __init__(self, window):
        self.window = window
        window.geometry("860x660")
        window.title("Track Statistics")
        fonts.apply_theme(window)

        title_lbl = ttk.Label(window, text="Library Statistics and History", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        button_frame = ttk.Frame(window)
        button_frame.grid(row=1, column=0, sticky="w", padx=12, pady=6)

        refresh_btn = ttk.Button(button_frame, text="Refresh Statistics", command=self.show_statistics_clicked)
        refresh_btn.grid(row=0, column=0, padx=(0, 8))

        load_history_btn = ttk.Button(button_frame, text="Load History", command=self.load_history_clicked)
        load_history_btn.grid(row=0, column=1, padx=(0, 8))

        delete_history_btn = ttk.Button(
            button_frame,
            text="Delete History",
            command=self.delete_history_clicked,
            style="Danger.TButton",
        )
        delete_history_btn.grid(row=0, column=2)

        self.stats_txt = tkst.ScrolledText(
            window,
            width=92,
            height=32,
            wrap="word",
            bg=TEXT_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG,
            relief="solid",
            borderwidth=1,
        )
        self.stats_txt.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)

        self.status_lbl = ttk.Label(window, text="", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, sticky="w", padx=12, pady=(0, 10))

        window.columnconfigure(0, weight=1)
        window.rowconfigure(2, weight=1)
        window.bind("<FocusIn>", self._handle_focus_refresh)

        self.show_statistics_clicked()

    def _handle_focus_refresh(self, event=None):
        self.show_statistics_clicked()

    def show_statistics_clicked(self):
        stats = lib.get_statistics()
        output = self.generate_statistics_text(stats)
        set_text(self.stats_txt, output)
        self.status_lbl.configure(text="Statistics displayed.")

    def load_history_clicked(self):
        history = lib.load_history()
        output = self.generate_history_text(history)
        set_text(self.stats_txt, output)
        self.status_lbl.configure(text=f"Loaded {len(history)} history entries.")

    def delete_history_clicked(self):
        confirmed = messagebox.askyesno(
            "Delete History",
            "Are you sure you want to delete all play history?",
            parent=self.window,
        )
        if not confirmed:
            self.status_lbl.configure(text="Delete history cancelled.")
            return

        if not lib.clear_history():
            self.status_lbl.configure(text="History could not be deleted.")
            return

        set_text(self.stats_txt, "Play history has been deleted.")
        self.status_lbl.configure(text="History deleted successfully.")

    def generate_statistics_text(self, stats):
        if stats["total_tracks"] == 0:
            return "No tracks are available in the library."

        output = []
        output.append("=" * 58)
        output.append("J U K E B O X   S T A T I S T I C S")
        output.append("=" * 58)
        output.append("")
        output.append(f"Total tracks:   {stats['total_tracks']}")
        output.append(f"Total plays:    {stats['total_plays']}")
        output.append(f"Average rating: {stats['average_rating']:.1f} / 5")
        output.append("")

        most_played = stats["most_played"]
        highest_rated = stats["highest_rated"]

        if most_played is not None:
            output.append("Most played track:")
            output.append(
                f"- {most_played['name']} by {most_played['artist']} ({most_played['play_count']} plays)"
            )
            output.append("")

        if highest_rated is not None:
            output.append("Highest rated track:")
            output.append(
                f"- {highest_rated['name']} by {highest_rated['artist']} ({highest_rated['rating']} stars)"
            )
            output.append("")

        output.append("Play count chart:")
        max_play_count = max((track["play_count"] for track in stats["tracks"]), default=0)
        scale = max(1, max_play_count // 25 + 1)

        for track in sorted(stats["tracks"], key=lambda item: (-item["play_count"], item["key"])):
            bar_length = track["play_count"] // scale if track["play_count"] > 0 else 0
            bar = "#" * bar_length
            output.append(
                f"{track['key']} {track['name'][:24]:24} | {bar} ({track['play_count']})"
            )

        output.append("")
        output.append("Rating chart:")
        for track in sorted(stats["tracks"], key=lambda item: (-item["rating"], item["key"])):
            stars = "*" * track["rating"]
            output.append(f"{track['key']} {track['name'][:24]:24} | {stars}")

        output.append("")
        output.append("Track types:")
        for track in stats["tracks"]:
            output.append(f"- {track['key']} {track['name']} -> {track['type']}")

        if scale > 1:
            output.append("")
            output.append(f"Note: play-count bars are scaled by 1 character = {scale} plays.")

        return "\n".join(output)

    def generate_history_text(self, history):
        if len(history) == 0:
            return "No play history is available."

        output = []
        output.append("=" * 58)
        output.append("J U K E B O X   P L A Y   H I S T O R Y")
        output.append("=" * 58)
        output.append("")
        output.append(f"Total history entries: {len(history)}")
        output.append("")

        for number, entry in enumerate(history, start=1):
            output.append(
                f"{number}. [{entry.get('played_at', 'Unknown time')}] "
                f"{entry.get('track_key', '--')} - "
                f"{entry.get('name', 'Unknown Track')} by "
                f"{entry.get('artist', 'Unknown Artist')} "
                f"(source: {entry.get('source', 'unknown')})"
            )

        return "\n".join(output)


if __name__ == "__main__":
    window = tk.Tk()
    fonts.configure()
    TrackStatistics(window)
    window.mainloop()