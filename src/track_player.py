import tkinter as tk
from tkinter import ttk

from . import font_manager as fonts
from .add_remove_tracks import AddRemoveTracks
from .create_track_list import CreateTrackList
from .track_statistics import TrackStatistics
from .update_tracks import UpdateTracks
from .view_tracks import TrackViewer


class JukeBoxApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("700x260")
        self.window.title("JukeBox")
        self.window.resizable(False, False)

        fonts.configure()
        fonts.apply_theme(self.window)

        self.open_windows = {}

        header_lbl = ttk.Label(
            self.window,
            text="Select an option by clicking one of the buttons below",
            style="Title.TLabel",
        )
        header_lbl.grid(row=0, column=0, columnspan=3, padx=12, pady=(18, 12))

        view_tracks_btn = ttk.Button(
            self.window,
            text="View Tracks",
            command=lambda: self.open_child_window("view_tracks", "Opening View Tracks window.", TrackViewer),
        )
        view_tracks_btn.grid(row=1, column=0, padx=12, pady=10, sticky="ew")

        create_track_list_btn = ttk.Button(
            self.window,
            text="Create Track List",
            command=lambda: self.open_child_window(
                "create_track_list",
                "Opening Create Track List window.",
                CreateTrackList,
            ),
        )
        create_track_list_btn.grid(row=1, column=1, padx=12, pady=10, sticky="ew")

        update_tracks_btn = ttk.Button(
            self.window,
            text="Update Tracks",
            command=lambda: self.open_child_window("update_tracks", "Opening Update Tracks window.", UpdateTracks),
        )
        update_tracks_btn.grid(row=1, column=2, padx=12, pady=10, sticky="ew")

        add_remove_tracks_btn = ttk.Button(
            self.window,
            text="Add / Remove Tracks",
            command=lambda: self.open_child_window(
                "add_remove_tracks",
                "Opening Add / Remove Tracks window.",
                AddRemoveTracks,
            ),
        )
        add_remove_tracks_btn.grid(row=2, column=0, padx=12, pady=10, sticky="ew")

        statistics_btn = ttk.Button(
            self.window,
            text="Statistics",
            command=lambda: self.open_child_window("statistics", "Opening Statistics window.", TrackStatistics),
        )
        statistics_btn.grid(row=2, column=1, padx=12, pady=10, sticky="ew")

        close_btn = ttk.Button(self.window, text="Close", command=self.window.destroy)
        close_btn.grid(row=2, column=2, padx=12, pady=10, sticky="ew")

        self.status_lbl = ttk.Label(self.window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=3, padx=12, pady=(8, 12), sticky="w")

        for column in range(3):
            self.window.columnconfigure(column, weight=1)

    def open_child_window(self, key, status_message, window_class):
        existing_window = self.open_windows.get(key)

        if existing_window is not None and existing_window.winfo_exists():
            existing_window.lift()
            existing_window.focus_force()
            self.status_lbl.configure(text=f"{window_class.__name__} is already open.")
            return

        child = tk.Toplevel(self.window)
        self.open_windows[key] = child

        def on_close():
            self.open_windows.pop(key, None)
            child.destroy()

        child.protocol("WM_DELETE_WINDOW", on_close)
        window_class(child)
        self.status_lbl.configure(text=status_message)

    def run(self):
        self.window.mainloop()


def main():
    app = JukeBoxApp()
    app.run()


if __name__ == "__main__":
    main()