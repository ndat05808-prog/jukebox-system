import tkinter as tk
from tkinter import ttk

# Assuming font_manager is imported as fonts in your actual project
# from . import font_manager as fonts

class ModernJukeBoxUI:
    def __init__(self, window):
        self.window = window
        self.window.geometry("950x550")
        self.window.title("JukeBox Music Manager")
        self.window.configure(bg="#F5F7FB") # Background from your font_manager

        # Apply your existing theme (assuming fonts.apply_theme(window) is called here)

        # Configure main grid
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_main_content()
        self.create_player_panel()

    def create_sidebar(self):
        """Left panel for navigation."""
        sidebar = tk.Frame(self.window, bg="#FFFFFF", width=200, relief="flat")
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 1))
        sidebar.grid_propagate(False) # Keep width fixed

        # Brand / Title
        brand_lbl = ttk.Label(sidebar, text="Library Menu", font=("Segoe UI", 14, "bold"), background="#FFFFFF")
        brand_lbl.pack(pady=(20, 30), padx=15, anchor="w")

        # Navigation Buttons
        buttons = [
            ("View All Tracks", self.dummy_command),
            ("Build Playlist", self.dummy_command),
            ("Add / Remove", self.dummy_command),
            ("Statistics", self.dummy_command),
            ("Update Tracks", self.dummy_command)
        ]

        for text, command in buttons:
            btn = ttk.Button(sidebar, text=text, command=command)
            btn.pack(fill="x", padx=15, pady=5)

    def create_main_content(self):
        """Center panel for the track list."""
        main_frame = tk.Frame(self.window, bg="#F5F7FB")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Header
        header_lbl = ttk.Label(main_frame, text="Your Music", font=("Segoe UI", 20, "bold"), background="#F5F7FB")
        header_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Treeview (Modern Table for Tracks)
        columns = ("Track", "Title", "Artist", "Rating")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("Track", text="#")
        self.tree.column("Track", width=40, anchor="center")
        self.tree.heading("Title", text="Title")
        self.tree.column("Title", width=200)
        self.tree.heading("Artist", text="Artist")
        self.tree.column("Artist", width=150)
        self.tree.heading("Rating", text="Rating")
        self.tree.column("Rating", width=80, anchor="center")

        self.tree.grid(row=1, column=0, sticky="nsew")

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Insert some dummy data to see how it looks
        self.tree.insert("", "end", values=("01", "What a Wonderful World", "Louis Armstrong", "⭐⭐⭐⭐⭐"))
        self.tree.insert("", "end", values=("02", "Here Comes the Sun", "The Beatles", "⭐⭐⭐⭐⭐"))

    def create_player_panel(self):
        """Right panel for track details and playback."""
        player_frame = tk.Frame(self.window, bg="#FFFFFF", width=250, relief="flat")
        player_frame.grid(row=0, column=2, sticky="ns", padx=(1, 0))
        player_frame.grid_propagate(False)

        # Placeholder for Album Art
        self.art_canvas = tk.Canvas(player_frame, width=190, height=190, bg="#EEF2FF", highlightthickness=0)
        self.art_canvas.pack(pady=(30, 15))
        self.art_canvas.create_text(95, 95, text="Album Art\nAppears Here", justify="center", fill="#475569")

        # Track Details
        self.lbl_title = ttk.Label(player_frame, text="Select a Track", font=("Segoe UI", 12, "bold"), background="#FFFFFF", anchor="center")
        self.lbl_title.pack(fill="x", padx=10)

        self.lbl_artist = ttk.Label(player_frame, text="--", font=("Segoe UI", 10), foreground="#475569", background="#FFFFFF", anchor="center")
        self.lbl_artist.pack(fill="x", padx=10, pady=(0, 20))

        # Playback Controls
        play_btn = ttk.Button(player_frame, text="▶ PLAY", command=self.dummy_command)
        play_btn.pack(fill="x", padx=30, pady=5)

        stop_btn = ttk.Button(player_frame, text="⏹ STOP", command=self.dummy_command, style="Danger.TButton")
        stop_btn.pack(fill="x", padx=30, pady=5)

        # Status Bar at the bottom of the right pane
        self.status_lbl = ttk.Label(player_frame, text="Status: Ready", background="#FFFFFF", foreground="#475569")
        self.status_lbl.pack(side="bottom", pady=20)

    def dummy_command(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernJukeBoxUI(root)
    root.mainloop()