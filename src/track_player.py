import tkinter as tk
from tkinter import ttk

from . import font_manager as fonts
from .add_remove_tracks import AddRemoveTracks
from .create_track_list import CreateTrackList
from .track_statistics import TrackStatistics
from .update_tracks import UpdateTracks
from .view_tracks import TrackViewer


def main():
    window = tk.Tk()
    window.geometry("700x260")
    window.title("JukeBox")
    window.resizable(False, False)

    fonts.configure()
    fonts.apply_theme(window)

    def view_tracks_clicked():
        status_lbl.configure(text="Opening View Tracks window.")
        TrackViewer(tk.Toplevel(window))

    def create_track_list_clicked():
        status_lbl.configure(text="Opening Create Track List window.")
        CreateTrackList(tk.Toplevel(window))

    def update_tracks_clicked():
        status_lbl.configure(text="Opening Update Tracks window.")
        UpdateTracks(tk.Toplevel(window))

    def add_remove_tracks_clicked():
        status_lbl.configure(text="Opening Add / Remove Tracks window.")
        AddRemoveTracks(tk.Toplevel(window))

    def statistics_clicked():
        status_lbl.configure(text="Opening Statistics window.")
        TrackStatistics(tk.Toplevel(window))

    header_lbl = ttk.Label(window, text="Select an option by clicking one of the buttons below", style="Title.TLabel")
    header_lbl.grid(row=0, column=0, columnspan=3, padx=12, pady=(18, 12))

    view_tracks_btn = ttk.Button(window, text="View Tracks", command=view_tracks_clicked)
    view_tracks_btn.grid(row=1, column=0, padx=12, pady=10, sticky="ew")

    create_track_list_btn = ttk.Button(window, text="Create Track List", command=create_track_list_clicked)
    create_track_list_btn.grid(row=1, column=1, padx=12, pady=10, sticky="ew")

    update_tracks_btn = ttk.Button(window, text="Update Tracks", command=update_tracks_clicked)
    update_tracks_btn.grid(row=1, column=2, padx=12, pady=10, sticky="ew")

    add_remove_tracks_btn = ttk.Button(window, text="Add / Remove Tracks", command=add_remove_tracks_clicked)
    add_remove_tracks_btn.grid(row=2, column=0, padx=12, pady=10, sticky="ew")

    statistics_btn = ttk.Button(window, text="Statistics", command=statistics_clicked)
    statistics_btn.grid(row=2, column=1, padx=12, pady=10, sticky="ew")

    close_btn = ttk.Button(window, text="Close", command=window.destroy)
    close_btn.grid(row=2, column=2, padx=12, pady=10, sticky="ew")

    status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
    status_lbl.grid(row=3, column=0, columnspan=3, padx=12, pady=(8, 12), sticky="w")

    for column in range(3):
        window.columnconfigure(column, weight=1)

    window.mainloop()
