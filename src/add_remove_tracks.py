import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from . import font_manager as fonts
from . import track_library as lib
from .validation import get_valid_rating, normalise_track_number


def set_text(text_area, content):
    text_area.configure(state="normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", content)
    text_area.configure(state="disabled")


class AddRemoveTracks:
    def __init__(self, window):
        self.window = window
        window.geometry("1040x560")
        window.title("Add / Remove Tracks")
        fonts.apply_theme(window)

        title_lbl = ttk.Label(window, text="Library Management", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6))

        add_frame = ttk.LabelFrame(window, text="Add New Track", style="Section.TLabelframe")
        add_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        ttk.Label(add_frame, text="Name").grid(row=0, column=0, padx=8, pady=8)
        self.name_input = ttk.Entry(add_frame, width=26)
        self.name_input.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(add_frame, text="Artist").grid(row=0, column=2, padx=8, pady=8)
        self.artist_input = ttk.Entry(add_frame, width=26)
        self.artist_input.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(add_frame, text="Rating (0-5)").grid(row=0, column=4, padx=8, pady=8)
        self.rating_input = ttk.Entry(add_frame, width=8)
        self.rating_input.grid(row=0, column=5, padx=8, pady=8)

        add_btn = ttk.Button(add_frame, text="Add Track", command=self.add_track_clicked)
        add_btn.grid(row=0, column=6, padx=8, pady=8)

        remove_frame = ttk.LabelFrame(window, text="Delete Track", style="Section.TLabelframe")
        remove_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        ttk.Label(remove_frame, text="Track Number").grid(row=0, column=0, padx=8, pady=8)
        self.remove_input = ttk.Entry(remove_frame, width=8)
        self.remove_input.grid(row=0, column=1, padx=8, pady=8)

        remove_btn = ttk.Button(remove_frame, text="Delete Track", command=self.remove_track_clicked)
        remove_btn.grid(row=0, column=2, padx=8, pady=8)

        list_frame = ttk.LabelFrame(window, text="Current Library", style="Section.TLabelframe")
        list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=12, pady=8)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.list_txt = tkst.ScrolledText(list_frame, width=92, height=20, wrap="none")
        self.list_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.status_lbl = ttk.Label(window, text="", style="Status.TLabel")
        self.status_lbl.grid(row=4, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(3, weight=1)

        self.refresh_list()

    def refresh_list(self):
        set_text(self.list_txt, lib.list_all())
        self.status_lbl.configure(text="Library list refreshed.")

    def add_track_clicked(self):
        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()
        rating_text = self.rating_input.get().strip()

        if name == "" or artist == "":
            self.status_lbl.configure(text="Name and artist cannot be empty.")
            return

        rating = get_valid_rating(rating_text, allow_zero=True)
        if rating is None:
            self.status_lbl.configure(text="Rating must be a whole number from 0 to 5.")
            return

        key = lib.add_track(name, artist, rating)
        self.refresh_list()
        self.status_lbl.configure(text=f"Added track {key}: '{name}' by {artist}.")
        self.name_input.delete(0, tk.END)
        self.artist_input.delete(0, tk.END)
        self.rating_input.delete(0, tk.END)

    def remove_track_clicked(self):
        track_key = normalise_track_number(self.remove_input.get())
        if track_key is None:
            self.status_lbl.configure(text="Please enter a valid track number.")
            return

        track_name = lib.get_name(track_key)
        if track_name is None:
            self.status_lbl.configure(text=f"Track {track_key} does not exist.")
            return

        lib.delete_track(track_key)
        self.refresh_list()
        self.status_lbl.configure(text=f"Deleted track {track_key}: '{track_name}'.")
        self.remove_input.delete(0, tk.END)


if __name__ == "__main__":
    window = tk.Tk()
    fonts.configure()
    AddRemoveTracks(window)
    window.mainloop()