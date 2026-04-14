import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox, ttk

from . import cover_manager
from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import set_text
from .validation import get_valid_rating, get_valid_year, normalise_track_number


TEXT_BG = "#FFFFFF"
TEXT_FG = "#111827"
CANVAS_BG = "#FFFFFF"
CANVAS_BORDER = "#D6DAE5"


class TrackViewer:
    """GUI window used to view, search, and inspect tracks."""

    def __init__(self, window):
        self.window = window
        self.cover_image = None

        window.geometry("1240x680")
        window.title("View Tracks")
        fonts.apply_theme(window)
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(2, weight=1)

        title_lbl = ttk.Label(window, text="Track Browser", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6))

        control_frame = ttk.LabelFrame(window, text="Controls", style="Section.TLabelframe")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)
        control_frame.columnconfigure(2, weight=1)

        list_tracks_btn = ttk.Button(control_frame, text="List All Tracks", command=self.list_tracks_clicked)
        list_tracks_btn.grid(row=0, column=0, padx=8, pady=8)

        enter_lbl = ttk.Label(control_frame, text="Track Number")
        enter_lbl.grid(row=0, column=1, padx=8, pady=8)

        self.input_txt = ttk.Entry(control_frame, width=8)
        self.input_txt.grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.input_txt.bind("<Return>", lambda event: self.view_track_clicked())

        check_track_btn = ttk.Button(control_frame, text="View Track Details", command=self.view_track_clicked)
        check_track_btn.grid(row=0, column=3, padx=8, pady=8)

        search_lbl = ttk.Label(control_frame, text="Search Name / Artist / Album")
        search_lbl.grid(row=1, column=0, padx=8, pady=8)

        self.search_txt = ttk.Entry(control_frame, width=28)
        self.search_txt.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=8)
        self.search_txt.bind("<Return>", lambda event: self.search_tracks_clicked())

        search_btn = ttk.Button(control_frame, text="Search", command=self.search_tracks_clicked)
        search_btn.grid(row=1, column=3, padx=8, pady=8)

        show_all_btn = ttk.Button(control_frame, text="Show All Again", command=self.list_tracks_clicked)
        show_all_btn.grid(row=1, column=4, padx=8, pady=8)

        filter_lbl = ttk.Label(control_frame, text="Filter By Score (0-5)")
        filter_lbl.grid(row=2, column=0, padx=8, pady=8)

        self.rating_filter_txt = ttk.Entry(control_frame, width=8)
        self.rating_filter_txt.grid(row=2, column=1, padx=8, pady=8, sticky="w")
        self.rating_filter_txt.bind("<Return>", lambda event: self.filter_by_score_clicked())

        filter_btn = ttk.Button(control_frame, text="Filter Score", command=self.filter_by_score_clicked)
        filter_btn.grid(row=2, column=3, padx=8, pady=8)

        library_frame = ttk.LabelFrame(window, text="Library List", style="Section.TLabelframe")
        library_frame.grid(row=2, column=0, sticky="nsew", padx=(12, 6), pady=8)
        library_frame.columnconfigure(0, weight=1)
        library_frame.rowconfigure(0, weight=1)

        details_frame = ttk.LabelFrame(window, text="Selected Track", style="Section.TLabelframe")
        details_frame.grid(row=2, column=1, sticky="nsew", padx=(6, 12), pady=8)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(2, weight=1)

        self.list_txt = tkst.ScrolledText(
            library_frame,
            width=56,
            height=18,
            wrap="none",
            bg=TEXT_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG,
            relief="solid",
            borderwidth=1,
        )
        self.list_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        cover_title_lbl = ttk.Label(details_frame, text="Track Cover")
        cover_title_lbl.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        self.cover_canvas = tk.Canvas(
            details_frame,
            width=240,
            height=240,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground=CANVAS_BORDER,
            bd=0,
        )
        self.cover_canvas.grid(row=1, column=0, sticky="n", padx=8, pady=(0, 8))

        self.cover_caption_lbl = ttk.Label(details_frame, text="No track selected yet.")
        self.cover_caption_lbl.grid(row=2, column=0, sticky="nw", padx=8, pady=(0, 6))

        self.track_txt = tkst.ScrolledText(
            details_frame,
            width=38,
            height=14,
            wrap="word",
            bg=TEXT_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG,
            relief="solid",
            borderwidth=1,
        )
        self.track_txt.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)

        self.status_lbl = ttk.Label(window, text="", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        window.bind("<FocusIn>", self._handle_focus_refresh)

        self.list_tracks_clicked()
        set_text(self.track_txt, "Choose a track number and click 'View Track Details'.")
        self.display_cover_placeholder()

    def _handle_focus_refresh(self, event=None):
        current_list = lib.list_all()
        set_text(self.list_txt, current_list)

    def display_cover_placeholder(self, title="No Track Selected", subtitle="Select a track to view its cover."):
        self.cover_image = None
        self.cover_canvas.delete("all")

        self.cover_canvas.create_rectangle(
            18,
            18,
            222,
            222,
            outline="#CBD5E1",
            width=2,
            fill="#F8FAFC",
        )
        self.cover_canvas.create_text(
            120,
            95,
            text=title,
            font=("Segoe UI", 13, "bold"),
            fill="#0F172A",
            width=180,
            justify="center",
        )
        self.cover_canvas.create_text(
            120,
            145,
            text=subtitle,
            font=("Segoe UI", 10),
            fill="#475569",
            width=180,
            justify="center",
        )

        self.cover_caption_lbl.configure(text="Add PNG cover files later if you want a richer interface.")

    def display_track_cover(self, track_key):
        track_name = lib.get_name(track_key) or "Unknown Track"
        artist_name = lib.get_artist(track_key) or "Unknown Artist"

        self.cover_canvas.delete("all")
        self.cover_image = cover_manager.load_cover_image(track_key, max_size=190)

        if self.cover_image is not None:
            self.cover_canvas.create_image(120, 120, image=self.cover_image)
            self.cover_caption_lbl.configure(
                text=f"Showing cover for track {track_key}: {track_name} — {artist_name}"
            )
            return

        self.cover_canvas.create_rectangle(
            18,
            18,
            222,
            222,
            outline="#C7D2FE",
            width=2,
            fill="#EEF2FF",
        )
        self.cover_canvas.create_text(
            120,
            78,
            text=track_name,
            font=("Segoe UI", 12, "bold"),
            fill="#312E81",
            width=180,
            justify="center",
        )
        self.cover_canvas.create_text(
            120,
            115,
            text=artist_name,
            font=("Segoe UI", 10),
            fill="#4338CA",
            width=180,
            justify="center",
        )
        self.cover_canvas.create_text(
            120,
            165,
            text=f"No cover image found for {track_key}.\nUse {track_key}.png or default.png",
            font=("Segoe UI", 10),
            fill="#475569",
            width=180,
            justify="center",
        )

        self.cover_caption_lbl.configure(text=cover_manager.get_cover_folder_text())

    def view_track_clicked(self):
        track_key = normalise_track_number(self.input_txt.get())

        if track_key is None:
            set_text(self.track_txt, "Please enter digits only for the track number.")
            self.display_cover_placeholder("Invalid Input", "Track number must contain digits only.")
            self.status_lbl.configure(text="Track number must contain digits only.")
            return

        track_details = lib.get_details(track_key)
        if track_details is None:
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.display_cover_placeholder("Track Not Found", f"No track exists with number {track_key}.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        set_text(self.track_txt, track_details)
        self.display_track_cover(track_key)
        self.status_lbl.configure(text=f"Showing details for track {track_key}.")

    def list_tracks_clicked(self):
        track_list = lib.list_all()
        set_text(self.list_txt, track_list)
        self.status_lbl.configure(text="All tracks are now displayed.")

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