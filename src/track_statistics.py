import tkinter as tk
from tkinter import messagebox, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import create_metric_card, draw_bar_chart, set_text


class TrackStatistics:
    def __init__(self, window):
        self.window = window
        window.geometry("1180x760")
        window.minsize(1040, 680)
        window.title("Track Statistics")
        fonts.apply_theme(window)

        window.columnconfigure(0, weight=2)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(2, weight=1)

        ttk.Label(window, text="Statistics Dashboard", style="Hero.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 6))
        ttk.Label(window, text="A clearer visual summary than the original plain-text statistics window.", style="Muted.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(56, 12))

        toolbar = ttk.Frame(window, style="Root.TFrame")
        toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=10)
        ttk.Button(toolbar, text="Refresh Statistics", style="Neon.TButton", command=self.show_statistics_clicked).pack(side="left")
        ttk.Button(toolbar, text="Load History", style="Ghost.TButton", command=self.load_history_clicked).pack(side="left", padx=10)
        ttk.Button(toolbar, text="Delete History", style="Danger.TButton", command=self.delete_history_clicked).pack(side="left")

        metrics_frame = ttk.Frame(window, style="Root.TFrame")
        metrics_frame.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
        metrics_frame.rowconfigure(1, weight=1)

        right_frame = ttk.Frame(window, style="Root.TFrame")
        right_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        cards_row = ttk.Frame(metrics_frame, style="Root.TFrame")
        cards_row.grid(row=0, column=0, columnspan=2, sticky="ew")
        cards_row.columnconfigure(0, weight=1)
        cards_row.columnconfigure(1, weight=1)
        cards_row.columnconfigure(2, weight=1)
        cards_row.columnconfigure(3, weight=1)

        self.total_tracks_card = create_metric_card(cards_row, "Tracks", "0", "Total items in the library")
        self.total_tracks_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.total_plays_card = create_metric_card(cards_row, "Total Plays", "0", "All play counts combined")
        self.total_plays_card.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.avg_rating_card = create_metric_card(cards_row, "Average Rating", "0.0", "Across the full library")
        self.avg_rating_card.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        self.types_card = create_metric_card(cards_row, "Album Tracks", "0", "Tracks with album metadata")
        self.types_card.grid(row=0, column=3, sticky="ew")

        chart_card = ttk.Frame(metrics_frame, style="Card.TFrame", padding=18)
        chart_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        chart_card.columnconfigure(0, weight=1)
        chart_card.rowconfigure(1, weight=1)
        ttk.Label(chart_card, text="Most Played Tracks", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.chart_canvas = tk.Canvas(chart_card, height=260)
        fonts.style_canvas(self.chart_canvas)
        self.chart_canvas.grid(row=1, column=0, sticky="nsew")

        top_card = ttk.Frame(metrics_frame, style="Card.TFrame", padding=18)
        top_card.grid(row=1, column=1, sticky="nsew", padx=(14, 0), pady=(14, 0))
        top_card.columnconfigure(0, weight=1)
        ttk.Label(top_card, text="Highlights", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.top_text = tk.Text(top_card, height=15, wrap="word")
        fonts.style_text_widget(self.top_text)
        self.top_text.grid(row=1, column=0, sticky="nsew")

        history_card = ttk.Frame(right_frame, style="Card.TFrame", padding=18)
        history_card.grid(row=0, column=0, sticky="nsew")
        history_card.columnconfigure(0, weight=1)
        history_card.rowconfigure(1, weight=1)
        ttk.Label(history_card, text="History / Details", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.stats_txt = tk.Text(history_card, height=28, wrap="word")
        fonts.style_text_widget(self.stats_txt)
        self.stats_txt.grid(row=1, column=0, sticky="nsew")

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.chart_canvas.bind("<Configure>", lambda event: self._redraw_chart())
        self._last_stats = None
        self.show_statistics_clicked()

    def _set_card_value(self, card, value: str):
        for child in card.winfo_children():
            if isinstance(child, ttk.Label) and "Metric.TLabel" in str(child.cget("style")):
                child.configure(text=value)
                return

    def _redraw_chart(self):
        if self._last_stats is None:
            return
        top_tracks = sorted(self._last_stats["tracks"], key=lambda item: (-item["play_count"], item["key"]))[:6]
        values = [track["play_count"] for track in top_tracks]
        labels = [track["key"] for track in top_tracks]
        draw_bar_chart(self.chart_canvas, values, labels)

    def show_statistics_clicked(self):
        stats = lib.get_statistics()
        self._last_stats = stats
        self._set_card_value(self.total_tracks_card, str(stats["total_tracks"]))
        self._set_card_value(self.total_plays_card, str(stats["total_plays"]))
        self._set_card_value(self.avg_rating_card, f"{stats['average_rating']:.1f}")
        self._set_card_value(self.types_card, str(stats["album_tracks"]))
        self._redraw_chart()

        highlights = []
        if stats["most_played"]:
            highlights.append(
                f"Most played:\n{stats['most_played']['name']} by {stats['most_played']['artist']}\n{stats['most_played']['play_count']} plays"
            )
        if stats["highest_rated"]:
            highlights.append(
                f"\nHighest rated:\n{stats['highest_rated']['name']} by {stats['highest_rated']['artist']}\n{stats['highest_rated']['rating']} / 5"
            )
        highlights.append(
            f"\nTrack types:\nAlbumTrack: {stats['album_tracks']}\nLibraryItem: {stats['standard_tracks']}"
        )
        set_text(self.top_text, "\n\n".join(highlights))

        lines = [
            "JukeBox Statistics",
            "=" * 48,
            f"Total tracks: {stats['total_tracks']}",
            f"Total plays: {stats['total_plays']}",
            f"Average rating: {stats['average_rating']:.1f} / 5",
            "",
            "Tracks:",
        ]
        for track in stats["tracks"]:
            lines.append(
                f"{track['key']} | {track['name']} | {track['artist']} | plays: {track['play_count']} | rating: {track['rating']}"
            )
        set_text(self.stats_txt, "\n".join(lines))
        self.status_lbl.configure(text="Statistics displayed.")

    def load_history_clicked(self):
        history = lib.load_history()
        if not history:
            set_text(self.stats_txt, "No play history is available.")
            self.status_lbl.configure(text="Loaded 0 history entries.")
            return
        lines = ["JukeBox Play History", "=" * 48, f"Total history entries: {len(history)}", ""]
        for number, entry in enumerate(history, start=1):
            lines.append(
                f"{number}. [{entry.get('played_at', 'Unknown time')}] {entry.get('track_key', '--')} - {entry.get('name', 'Unknown Track')} by {entry.get('artist', 'Unknown Artist')} (source: {entry.get('source', 'unknown')})"
            )
        set_text(self.stats_txt, "\n".join(lines))
        self.status_lbl.configure(text=f"Loaded {len(history)} history entries.")

    def delete_history_clicked(self):
        confirmed = messagebox.askyesno("Delete History", "Are you sure you want to delete all play history?", parent=self.window)
        if not confirmed:
            self.status_lbl.configure(text="Delete history cancelled.")
            return
        if not lib.clear_history():
            self.status_lbl.configure(text="History could not be deleted.")
            return
        set_text(self.stats_txt, "Play history has been deleted.")
        self.status_lbl.configure(text="History deleted successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    TrackStatistics(root)
    root.mainloop()