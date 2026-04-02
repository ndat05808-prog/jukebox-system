import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

import font_manager as fonts
import track_library as lib


def set_text(text_area, content):
    text_area.configure(state="normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", content)
    text_area.configure(state="disabled")


class TrackStatistics:
    def __init__(self, window):
        self.window = window
        window.geometry("760x620")
        window.title("Track Statistics")
        fonts.apply_theme(window)

        title_lbl = ttk.Label(window, text="Library Statistics", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        refresh_btn = ttk.Button(window, text="Refresh Statistics", command=self.refresh)
        refresh_btn.grid(row=1, column=0, sticky="w", padx=12, pady=6)

        self.stats_txt = tkst.ScrolledText(window, width=82, height=30, wrap="word")
        self.stats_txt.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)

        window.columnconfigure(0, weight=1)
        window.rowconfigure(2, weight=1)
        self.refresh()

    def refresh(self):
        stats = lib.get_statistics()
        output = self.generate_statistics_text(stats)
        set_text(self.stats_txt, output)

    def generate_statistics_text(self, stats):
        if stats["total_tracks"] == 0:
            return "No tracks are available in the library."

        output = []
        output.append("=" * 56)
        output.append("J U K E B O X   S T A T I S T I C S")
        output.append("=" * 56)
        output.append("")
        output.append(f"Total tracks:   {stats['total_tracks']}")
        output.append(f"Total plays:    {stats['total_plays']}")
        output.append(f"Average rating: {stats['average_rating']:.1f} / 5")
        output.append("")

        most_played = stats["most_played"]
        highest_rated = stats["highest_rated"]
        output.append("Most played track:")
        output.append(f"- {most_played['name']} by {most_played['artist']} ({most_played['play_count']} plays)")
        output.append("")
        output.append("Highest rated track:")
        output.append(f"- {highest_rated['name']} by {highest_rated['artist']} ({highest_rated['rating']} stars)")
        output.append("")
        output.append("Play count chart:")
        for track in sorted(stats["tracks"], key=lambda item: (-item["play_count"], item["key"])):
            bar = "#" * track["play_count"]
            output.append(f"{track['key']} {track['name'][:24]:24} | {bar} ({track['play_count']})")
        output.append("")
        output.append("Rating chart:")
        for track in sorted(stats["tracks"], key=lambda item: (-item["rating"], item["key"])):
            stars = "*" * track["rating"]
            output.append(f"{track['key']} {track['name'][:24]:24} | {stars}")
        output.append("")
        output.append("Track types:")
        for track in stats["tracks"]:
            output.append(f"- {track['key']} {track['name']} -> {track['type']}")
        return "\n".join(output)


if __name__ == "__main__":
    window = tk.Tk()
    fonts.configure()
    TrackStatistics(window)
    window.mainloop()