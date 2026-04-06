import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from . import font_manager as fonts
from . import track_library as lib
from .validation import normalise_track_number, get_valid_rating


# This helper function replaces all of the old text inside a text widget.
# It is useful because many different buttons need to refresh the display area.
def set_text(text_area, content):
    text_area.configure(state="normal")          # allow the widget to be edited temporarily
    text_area.delete("1.0", tk.END)             # remove every character currently in the text box
    text_area.insert("1.0", content)            # insert the new content at the top of the widget
    text_area.configure(state="disabled")       # lock the widget again so the user cannot type into it


class TrackViewer:
    """GUI window used to view, search, and inspect tracks."""

    # The constructor runs when a TrackViewer object is created.
    # It builds every widget needed for the window and then shows all tracks.
    def __init__(self, window):
        self.window = window
        window.geometry("1040x560")
        window.title("View Tracks")
        fonts.apply_theme(window)
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)

        title_lbl = ttk.Label(window, text="Track Browser", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6))

        control_frame = ttk.LabelFrame(window, text="Controls", style="Section.TLabelframe")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        list_tracks_btn = ttk.Button(control_frame, text="List All Tracks", command=self.list_tracks_clicked)
        list_tracks_btn.grid(row=0, column=0, padx=8, pady=8)

        enter_lbl = ttk.Label(control_frame, text="Track Number")
        enter_lbl.grid(row=0, column=1, padx=8, pady=8)

        self.input_txt = ttk.Entry(control_frame, width=8)
        self.input_txt.grid(row=0, column=2, padx=8, pady=8)

        check_track_btn = ttk.Button(control_frame, text="View Track Details", command=self.view_track_clicked)
        check_track_btn.grid(row=0, column=3, padx=8, pady=8)

        search_lbl = ttk.Label(control_frame, text="Search Name / Artist / Album")
        search_lbl.grid(row=1, column=0, padx=8, pady=8)

        self.search_txt = ttk.Entry(control_frame, width=28)
        self.search_txt.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=8)

        search_btn = ttk.Button(control_frame, text="Search", command=self.search_tracks_clicked)
        search_btn.grid(row=1, column=3, padx=8, pady=8)

        show_all_btn = ttk.Button(control_frame, text="Show All Again", command=self.list_tracks_clicked)
        show_all_btn.grid(row=1, column=4, padx=8, pady=8)

        filter_lbl = ttk.Label(control_frame, text="Filter By Score (0-5)")
        filter_lbl.grid(row=2, column=0, padx=8, pady=8)

        self.rating_filter_txt = ttk.Entry(control_frame, width=8)
        self.rating_filter_txt.grid(row=2, column=1, padx=8, pady=8, sticky="w")

        filter_btn = ttk.Button(control_frame, text="Filter Score", command=self.filter_by_score_clicked)
        filter_btn.grid(row=2, column=3, padx=8, pady=8)

        library_frame = ttk.LabelFrame(window, text="Library List", style="Section.TLabelframe")
        library_frame.grid(row=2, column=0, sticky="nsew", padx=(12, 6), pady=8)
        library_frame.columnconfigure(0, weight=1)
        library_frame.rowconfigure(0, weight=1)

        details_frame = ttk.LabelFrame(window, text="Selected Track", style="Section.TLabelframe")
        details_frame.grid(row=2, column=1, sticky="nsew", padx=(6, 12), pady=8)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)

        self.list_txt = tkst.ScrolledText(library_frame, width=56, height=18, wrap="none")
        self.list_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.track_txt = tkst.ScrolledText(details_frame, width=34, height=18, wrap="word")
        self.track_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.status_lbl = ttk.Label(window, text="", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        self.list_tracks_clicked()
        set_text(self.track_txt, "Choose a track number and click 'View Track Details'.")

    # This method validates the typed track number and shows either the track details
    # or an error message if the input is empty, not numeric, or not found in the library.
    def view_track_clicked(self):
        track_key = normalise_track_number(self.input_txt.get())

        if track_key is None:
            set_text(self.track_txt, "Please enter digits only for the track number.")
            self.status_lbl.configure(text="Track number must contain digits only.")
            return

        track_details = lib.get_details(track_key)
        if track_details is None:
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        set_text(self.track_txt, track_details)
        self.status_lbl.configure(text=f"Showing details for track {track_key}.")

    # This method lists every track currently stored in the library.
    def list_tracks_clicked(self):
        track_list = lib.list_all()
        set_text(self.list_txt, track_list)
        self.status_lbl.configure(text="All tracks are now displayed.")

    # This method searches for a typed keyword and refreshes the list area.
    # If the keyword is empty, all tracks are shown again.
    def search_tracks_clicked(self):
        keyword = self.search_txt.get().strip()
        results = lib.search_tracks(keyword)

        if results == "":
            set_text(self.list_txt, "No matching tracks were found.")
            self.status_lbl.configure(text="Search finished: 0 matches.")
        else:
            set_text(self.list_txt, results)
            if keyword == "":
                self.status_lbl.configure(text="Search box was empty, so all tracks were shown.")
            else:
                self.status_lbl.configure(text=f"Showing search results for '{keyword}'.")

    def filter_by_score_clicked(self):
        rating = get_valid_rating(self.rating_filter_txt.get(), allow_zero=True)

        if rating is None:
            set_text(self.list_txt, "Please enter a whole number from 0 to 5.")
            self.status_lbl.configure(text="Filter score must be between 0 and 5.")
            return

        results = lib.filter_tracks_by_rating(rating)

        if results == "":
            set_text(self.list_txt, f"No tracks were found with rating {rating}.")
            self.status_lbl.configure(text=f"Filter finished: 0 tracks with rating {rating}.")
        else:
            set_text(self.list_txt, results)
            self.status_lbl.configure(text=f"Showing tracks with rating {rating}.")


if __name__ == "__main__":
    window = tk.Tk()
    fonts.configure()
    TrackViewer(window)
    window.mainloop()