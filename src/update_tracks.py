import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import set_text
from .library_item import AlbumTrack
from .validation import get_valid_rating, get_valid_year, normalise_track_number


class UpdateTracks:
    def __init__(self, window):
        self.window = window

        window.geometry("1180x620")
        window.title("Edit Track Information")
        fonts.apply_theme(window)
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)

        title_lbl = ttk.Label(window, text="Edit Track Information", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6))

        control_frame = ttk.LabelFrame(window, text="Controls", style="Section.TLabelframe")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        list_tracks_btn = ttk.Button(control_frame, text="List All Tracks", command=self.list_tracks_clicked)
        list_tracks_btn.grid(row=0, column=0, padx=8, pady=8)

        track_lbl = ttk.Label(control_frame, text="Track Number")
        track_lbl.grid(row=0, column=1, padx=8, pady=8)

        self.track_input = ttk.Entry(control_frame, width=8)
        self.track_input.grid(row=0, column=2, padx=8, pady=8)

        load_btn = ttk.Button(control_frame, text="Load Track", command=self.load_track_clicked)
        load_btn.grid(row=0, column=3, padx=8, pady=8)

        name_lbl = ttk.Label(control_frame, text="Name")
        name_lbl.grid(row=1, column=0, padx=8, pady=8)

        self.name_input = ttk.Entry(control_frame, width=24)
        self.name_input.grid(row=1, column=1, padx=8, pady=8)

        artist_lbl = ttk.Label(control_frame, text="Artist")
        artist_lbl.grid(row=1, column=2, padx=8, pady=8)

        self.artist_input = ttk.Entry(control_frame, width=24)
        self.artist_input.grid(row=1, column=3, padx=8, pady=8)

        rating_lbl = ttk.Label(control_frame, text="Rating (0-5)")
        rating_lbl.grid(row=1, column=4, padx=8, pady=8)

        self.rating_input = ttk.Entry(control_frame, width=8)
        self.rating_input.grid(row=1, column=5, padx=8, pady=8)

        album_lbl = ttk.Label(control_frame, text="Album")
        album_lbl.grid(row=2, column=0, padx=8, pady=8)

        self.album_input = ttk.Entry(control_frame, width=24)
        self.album_input.grid(row=2, column=1, padx=8, pady=8)

        year_lbl = ttk.Label(control_frame, text="Year")
        year_lbl.grid(row=2, column=2, padx=8, pady=8)

        self.year_input = ttk.Entry(control_frame, width=12)
        self.year_input.grid(row=2, column=3, padx=8, pady=8)

        update_btn = ttk.Button(control_frame, text="Update Track", command=self.update_track_clicked)
        update_btn.grid(row=2, column=4, columnspan=2, padx=8, pady=8, sticky="ew")

        list_frame = ttk.LabelFrame(window, text="Library", style="Section.TLabelframe")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(12, 6), pady=8)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        detail_frame = ttk.LabelFrame(window, text="Selected Track", style="Section.TLabelframe")
        detail_frame.grid(row=2, column=1, sticky="nsew", padx=(6, 12), pady=8)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)

        self.list_txt = tkst.ScrolledText(list_frame, width=56, height=20, wrap="none")
        self.list_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.track_txt = tkst.ScrolledText(detail_frame, width=40, height=20, wrap="word")
        self.track_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.status_lbl = ttk.Label(window, text="", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        self.list_tracks_clicked()
        set_text(
            self.track_txt,
            "Enter a track number, click 'Load Track', edit the fields, then click 'Update Track'.",
        )

    def list_tracks_clicked(self):
        set_text(self.list_txt, lib.list_all())
        self.status_lbl.configure(text="Library tracks are displayed.")

    def _clear_edit_fields(self):
        self.name_input.delete(0, tk.END)
        self.artist_input.delete(0, tk.END)
        self.rating_input.delete(0, tk.END)
        self.album_input.delete(0, tk.END)
        self.year_input.delete(0, tk.END)

    def load_track_clicked(self):
        track_key = normalise_track_number(self.track_input.get())
        if track_key is None:
            set_text(self.track_txt, "Track number must contain digits only.")
            self.status_lbl.configure(text="Please enter digits only for the track number.")
            return

        item = lib.get_item(track_key)
        if item is None:
            self._clear_edit_fields()
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        self._clear_edit_fields()
        self.name_input.insert(0, item.name)
        self.artist_input.insert(0, item.artist)
        self.rating_input.insert(0, str(item.rating))

        if isinstance(item, AlbumTrack):
            self.album_input.insert(0, item.album)
            if item.year is not None:
                self.year_input.insert(0, str(item.year))

        set_text(self.track_txt, lib.get_details(track_key))
        self.status_lbl.configure(text=f"Track {track_key} loaded successfully.")

    def update_track_clicked(self):
        track_key = normalise_track_number(self.track_input.get())
        if track_key is None:
            set_text(self.track_txt, "Track number must contain digits only.")
            self.status_lbl.configure(text="Please enter digits only for the track number.")
            return

        if lib.get_name(track_key) is None:
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()
        if name == "" or artist == "":
            set_text(self.track_txt, "Name and artist cannot be empty.")
            self.status_lbl.configure(text="Please enter both name and artist.")
            return

        rating = get_valid_rating(self.rating_input.get(), allow_zero=True)
        if rating is None:
            set_text(self.track_txt, "Rating must be a whole number from 0 to 5.")
            self.status_lbl.configure(text="Please enter a rating between 0 and 5.")
            return

        year_text = self.year_input.get().strip()
        year = get_valid_year(year_text)
        if year_text != "" and year is None:
            set_text(self.track_txt, "Year must be between 1900 and 2100, or left blank.")
            self.status_lbl.configure(text="Year must be between 1900 and 2100, or left blank.")
            return

        album = self.album_input.get().strip()

        success = lib.update_track_info(
            track_key,
            name,
            artist,
            rating,
            album=album,
            year=year,
        )

        if not success:
            set_text(self.track_txt, "The track could not be updated.")
            self.status_lbl.configure(text="Update failed. The file may not have been saved.")
            return

        details = lib.get_details(track_key)
        set_text(self.track_txt, details)
        self.list_tracks_clicked()
        self.status_lbl.configure(text=f"Track {track_key} was updated successfully.")


if __name__ == "__main__":
    window = tk.Tk()
    fonts.configure()
    UpdateTracks(window)
    window.mainloop()