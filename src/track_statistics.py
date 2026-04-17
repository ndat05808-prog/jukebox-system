import tkinter as tk
from tkinter import messagebox, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import create_metric_card, draw_bar_chart, set_text


class TrackStatistics:
    def __init__(self, window):
        self.window = window
        window.geometry("1420x820")
        window.minsize(1220, 760)
        window.title("Track Statistics")
        fonts.apply_theme(window)

        # Cập nhật: Ép tỷ lệ 2:1 tuyệt đối cho cột trái và phải
        window.columnconfigure(0, weight=2, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")
        window.rowconfigure(3, weight=1)

        self._last_stats = None

        # Header riêng để không bị chồng chữ
        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Statistics Dashboard",
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            header,
            text="A clearer visual summary than the original plain-text statistics window.",
            style="Muted.TLabel"
        ).grid(row=1, column=0, sticky="w")

        # Toolbar
        toolbar = ttk.Frame(window, style="Root.TFrame")
        toolbar.grid(row=1, column=0, columnspan=2, sticky="w", padx=18, pady=10)

        ttk.Button(
            toolbar,
            text="Refresh Statistics",
            style="Neon.TButton",
            command=self.show_statistics_clicked
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="Load History",
            style="Ghost.TButton",
            command=self.load_history_clicked
        ).pack(side="left", padx=10)

        ttk.Button(
            toolbar,
            text="Delete History",
            style="Danger.TButton",
            command=self.delete_history_clicked
        ).pack(side="left")

        # Metric cards
        metrics_row = ttk.Frame(window, style="Root.TFrame")
        metrics_row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 14))
        for i in range(4):
            metrics_row.columnconfigure(i, weight=1)

        self.total_tracks_card = create_metric_card(
            metrics_row,
            "Tracks",
            "0",
            "Total items in the library"
        )
        self.total_tracks_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.total_plays_card = create_metric_card(
            metrics_row,
            "Total Plays",
            "0",
            "All play counts combined"
        )
        self.total_plays_card.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        self.avg_rating_card = create_metric_card(
            metrics_row,
            "Average Rating",
            "0.0",
            "Across the full library"
        )
        self.avg_rating_card.grid(row=0, column=2, sticky="ew", padx=(0, 10))

        self.types_card = create_metric_card(
            metrics_row,
            "Album Tracks",
            "0",
            "Tracks with album metadata"
        )
        self.types_card.grid(row=0, column=3, sticky="ew")

        # Main content
        left_content = ttk.Frame(window, style="Root.TFrame")
        left_content.grid(row=3, column=0, sticky="nsew", padx=(18, 10), pady=10)

        # Cập nhật: Tỷ lệ 2:1 giữa Biểu đồ và Highlights
        left_content.columnconfigure(0, weight=2, uniform="left_cols")
        left_content.columnconfigure(1, weight=1, uniform="left_cols")
        left_content.rowconfigure(0, weight=1)

        right_content = ttk.Frame(window, style="Root.TFrame")
        right_content.grid(row=3, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right_content.columnconfigure(0, weight=1)
        right_content.rowconfigure(0, weight=1)

        # Most Played Tracks card
        chart_card = ttk.Frame(left_content, style="Card.TFrame", padding=18)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        chart_card.columnconfigure(0, weight=1)
        chart_card.rowconfigure(1, weight=1)

        ttk.Label(
            chart_card,
            text="Most Played Tracks",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Canvas cao hơn và khung rộng hơn
        self.chart_canvas = tk.Canvas(chart_card, height=360)
        fonts.style_canvas(self.chart_canvas)
        self.chart_canvas.grid(row=1, column=0, sticky="nsew")

        # Highlights card
        highlights_card = ttk.Frame(left_content, style="Card.TFrame", padding=18)
        highlights_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        highlights_card.columnconfigure(0, weight=1)
        highlights_card.rowconfigure(1, weight=1)

        ttk.Label(
            highlights_card,
            text="Highlights",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Cập nhật: Thêm width=1
        self.top_text = tk.Text(highlights_card, height=18, width=1, wrap="word")
        fonts.style_text_widget(self.top_text)
        self.top_text.grid(row=1, column=0, sticky="nsew")

        # History / Details card
        history_card = ttk.Frame(right_content, style="Card.TFrame", padding=18)
        history_card.grid(row=0, column=0, sticky="nsew")
        history_card.columnconfigure(0, weight=1)
        history_card.rowconfigure(1, weight=1)

        ttk.Label(
            history_card,
            text="History / Details",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Cập nhật: Thêm width=1
        self.stats_txt = tk.Text(history_card, height=28, width=1, wrap="word")
        fonts.style_text_widget(self.stats_txt)
        self.stats_txt.grid(row=1, column=0, sticky="nsew")

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=4, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.chart_canvas.bind("<Configure>", lambda event: self._redraw_chart())
        self.show_statistics_clicked()

    def _set_card_value(self, card, value: str):
        for child in card.winfo_children():
            if isinstance(child, ttk.Label) and "Metric.TLabel" in str(child.cget("style")):
                child.configure(text=value)
                return

    def _redraw_chart(self):
        if self._last_stats is None:
            return

        top_tracks = sorted(
            self._last_stats["tracks"],
            key=lambda item: (-item["play_count"], item["key"])
        )[:6]

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
                f"Most played:\n"
                f"{stats['most_played']['name']} by {stats['most_played']['artist']}\n"
                f"{stats['most_played']['play_count']} plays"
            )

        if stats["highest_rated"]:
            highlights.append(
                f"\nHighest rated:\n"
                f"{stats['highest_rated']['name']} by {stats['highest_rated']['artist']}\n"
                f"{stats['highest_rated']['rating']} / 5"
            )

        highlights.append(
            f"\nTrack types:\n"
            f"AlbumTrack: {stats['album_tracks']}\n"
            f"LibraryItem: {stats['standard_tracks']}"
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
                f"{track['key']} | {track['name']} | {track['artist']} | "
                f"plays: {track['play_count']} | rating: {track['rating']}"
            )

        set_text(self.stats_txt, "\n".join(lines))
        self.status_lbl.configure(text="Statistics displayed.")

    def load_history_clicked(self):
        history = lib.load_history()
        if not history:
            set_text(self.stats_txt, "No play history is available.")
            self.status_lbl.configure(text="Loaded 0 history entries.")
            return

        lines = [
            "JukeBox Play History",
            "=" * 48,
            f"Total history entries: {len(history)}",
            ""
        ]

        for number, entry in enumerate(history, start=1):
            lines.append(
                f"{number}. [{entry.get('played_at', 'Unknown time')}] "
                f"{entry.get('track_key', '--')} - "
                f"{entry.get('name', 'Unknown Track')} by "
                f"{entry.get('artist', 'Unknown Artist')} "
                f"(source: {entry.get('source', 'unknown')})"
            )

        set_text(self.stats_txt, "\n".join(lines))
        self.status_lbl.configure(text=f"Loaded {len(history)} history entries.")

    def delete_history_clicked(self):
        confirmed = messagebox.askyesno(
            "Delete History",
            "Are you sure you want to delete all play history?",
            parent=self.window
        )
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