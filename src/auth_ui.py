from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import auth_manager
from . import font_manager as fonts
from .track_player import JukeBoxApp


class AuthApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JukeBox — Sign in")
        self.root.geometry("980x620")
        self.root.minsize(820, 560)

        fonts.configure()
        fonts.apply_theme(self.root)

        self._show_sign_in_password = False
        self._show_sign_up_password = False
        self._show_sign_up_confirm = False

        self._build_ui()
        self.show_sign_in()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        wrapper = ttk.Frame(self.root, style="Root.TFrame", padding=28)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.columnconfigure(0, weight=5)
        wrapper.columnconfigure(1, weight=4)
        wrapper.rowconfigure(0, weight=1)

        self._build_left_panel(wrapper)
        self._build_right_panel(wrapper)

    def _build_left_panel(self, parent):
        left = ttk.Frame(parent, style="Card.TFrame", padding=32)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)

        ttk.Label(left, text="♪  JUKEBOX", style="Tag.TLabel").grid(row=0, column=0, sticky="w")

        ttk.Label(
            left,
            text="Your music,\nbeautifully organised.",
            background=fonts.CARD,
            foreground=fonts.TEXT,
            font=fonts.ff(28, "bold"),
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(18, 10))

        ttk.Label(
            left,
            text=(
                "Build playlists, track what you play and discover\n"
                "insights about your listening habits — all in one place."
            ),
            style="CardMuted.TLabel",
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 22))

        features = [
            ("♫", "Smart library", "Search, filter and rate your entire collection."),
            ("▤", "Live statistics", "See top tracks and listening trends at a glance."),
            ("♡", "Playlists", "Create, rename and save custom playlists."),
        ]
        feature_wrap = ttk.Frame(left, style="Card.TFrame")
        feature_wrap.grid(row=3, column=0, sticky="ew")
        feature_wrap.columnconfigure(0, weight=1)

        for row_index, (icon, title, desc) in enumerate(features):
            row = ttk.Frame(feature_wrap, style="Card.TFrame")
            row.grid(row=row_index, column=0, sticky="ew", pady=6)
            row.columnconfigure(1, weight=1)

            ttk.Label(
                row,
                text=icon,
                background=fonts.CARD,
                foreground=fonts.ACCENT_GLOW,
                font=fonts.ff(18, "bold"),
            ).grid(row=0, column=0, rowspan=2, padx=(0, 14))

            ttk.Label(
                row,
                text=title,
                background=fonts.CARD,
                foreground=fonts.TEXT,
                font=fonts.ff(11, "bold"),
            ).grid(row=0, column=1, sticky="w")

            ttk.Label(
                row,
                text=desc,
                style="CardMuted.TLabel",
                wraplength=300,
                justify="left",
            ).grid(row=1, column=1, sticky="w")

        hint = ttk.Frame(left, style="Soft.TFrame", padding=14)
        hint.grid(row=5, column=0, sticky="ew", pady=(22, 0))
        hint.columnconfigure(1, weight=1)

        ttk.Label(
            hint,
            text="ⓘ",
            background=fonts.INPUT_BG,
            foreground=fonts.ACCENT,
            font=fonts.ff(14, "bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 10))

        ttk.Label(
            hint,
            text="Default account",
            background=fonts.INPUT_BG,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(row=0, column=1, sticky="w")

        ttk.Label(
            hint,
            text="td123  •  password: td456",
            background=fonts.INPUT_BG,
            foreground=fonts.TEXT,
            font=fonts.ff(11, "bold"),
        ).grid(row=1, column=1, sticky="w")

    def _build_right_panel(self, parent):
        right = ttk.Frame(parent, style="Card.TFrame", padding=32)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        toggle = ttk.Frame(right, style="Soft.TFrame", padding=4)
        toggle.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        toggle.columnconfigure(0, weight=1)
        toggle.columnconfigure(1, weight=1)

        self.sign_in_tab = ttk.Button(
            toggle, text="Sign In", style="Neon.TButton", command=self.show_sign_in
        )
        self.sign_in_tab.grid(row=0, column=0, sticky="ew", padx=2)

        self.sign_up_tab = ttk.Button(
            toggle, text="Sign Up", style="Ghost.TButton", command=self.show_sign_up
        )
        self.sign_up_tab.grid(row=0, column=1, sticky="ew", padx=2)

        self.header_lbl = ttk.Label(
            right,
            text="Welcome back",
            background=fonts.CARD,
            foreground=fonts.TEXT,
            font=fonts.ff(22, "bold"),
        )
        self.header_lbl.grid(row=1, column=0, sticky="w")

        self.subheader_lbl = ttk.Label(
            right,
            text="Sign in to continue to your library.",
            style="CardMuted.TLabel",
        )
        self.subheader_lbl.grid(row=2, column=0, sticky="nw", pady=(4, 0))

        self.forms_host = ttk.Frame(right, style="Card.TFrame")
        self.forms_host.grid(row=3, column=0, sticky="nsew", pady=(20, 0))
        self.forms_host.columnconfigure(0, weight=1)

        self.sign_in_frame = ttk.Frame(self.forms_host, style="Card.TFrame")
        self.sign_in_frame.grid(row=0, column=0, sticky="nsew")
        self.sign_in_frame.columnconfigure(0, weight=1)

        self.sign_up_frame = ttk.Frame(self.forms_host, style="Card.TFrame")
        self.sign_up_frame.grid(row=0, column=0, sticky="nsew")
        self.sign_up_frame.columnconfigure(0, weight=1)

        self._build_sign_in_form()
        self._build_sign_up_form()

        self.status_lbl = tk.Label(
            right,
            text="",
            bg=fonts.CARD,
            fg=fonts.MUTED,
            font=fonts.ff(10),
            anchor="w",
            justify="left",
            wraplength=360,
        )
        self.status_lbl.grid(row=4, column=0, sticky="ew", pady=(18, 0))

    def _build_labelled_entry(self, parent, label: str, show: str | None = None):
        ttk.Label(
            parent,
            text=label,
            background=fonts.CARD,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(sticky="w")

        entry_wrap = ttk.Frame(parent, style="Soft.TFrame", padding=(12, 0))
        entry_wrap.grid(sticky="ew", pady=(6, 12))
        entry_wrap.columnconfigure(1, weight=1)
        return entry_wrap

    def _build_sign_in_form(self):
        frame = self.sign_in_frame
        frame.columnconfigure(0, weight=1)

        ttk.Label(
            frame,
            text="USERNAME",
            background=fonts.CARD,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(row=0, column=0, sticky="w")

        user_wrap = ttk.Frame(frame, style="Soft.TFrame", padding=(12, 0))
        user_wrap.grid(row=1, column=0, sticky="ew", pady=(6, 14))
        user_wrap.columnconfigure(1, weight=1)

        ttk.Label(
            user_wrap, text="◐", background=fonts.INPUT_BG, foreground=fonts.ACCENT, font=fonts.ff(12)
        ).grid(row=0, column=0, padx=(0, 6))

        self.login_username = ttk.Entry(user_wrap, style="TEntry")
        self.login_username.grid(row=0, column=1, sticky="ew", pady=8)

        ttk.Label(
            frame,
            text="PASSWORD",
            background=fonts.CARD,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(row=2, column=0, sticky="w")

        pass_wrap = ttk.Frame(frame, style="Soft.TFrame", padding=(12, 0))
        pass_wrap.grid(row=3, column=0, sticky="ew", pady=(6, 18))
        pass_wrap.columnconfigure(1, weight=1)

        ttk.Label(
            pass_wrap, text="⚷", background=fonts.INPUT_BG, foreground=fonts.ACCENT, font=fonts.ff(12)
        ).grid(row=0, column=0, padx=(0, 6))

        self.login_password = ttk.Entry(pass_wrap, show="•")
        self.login_password.grid(row=0, column=1, sticky="ew", pady=8)
        self.login_password.bind("<Return>", lambda e: self.sign_in_clicked())

        self.login_password_toggle = ttk.Button(
            pass_wrap,
            text="Show",
            style="Link.TButton",
            command=self._toggle_sign_in_password,
        )
        self.login_password_toggle.grid(row=0, column=2, padx=(6, 0))

        ttk.Button(
            frame,
            text="Sign In →",
            style="Neon.TButton",
            command=self.sign_in_clicked,
        ).grid(row=4, column=0, sticky="ew", ipady=6)

        ttk.Label(
            frame,
            text="New to JukeBox? Switch to Sign Up above.",
            style="CardMuted.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(14, 0))

    def _build_sign_up_form(self):
        frame = self.sign_up_frame
        frame.columnconfigure(0, weight=1)

        ttk.Label(
            frame,
            text="USERNAME",
            background=fonts.CARD,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(row=0, column=0, sticky="w")

        u_wrap = ttk.Frame(frame, style="Soft.TFrame", padding=(12, 0))
        u_wrap.grid(row=1, column=0, sticky="ew", pady=(6, 12))
        u_wrap.columnconfigure(1, weight=1)
        ttk.Label(
            u_wrap, text="◐", background=fonts.INPUT_BG, foreground=fonts.ACCENT, font=fonts.ff(12)
        ).grid(row=0, column=0, padx=(0, 6))
        self.signup_username = ttk.Entry(u_wrap)
        self.signup_username.grid(row=0, column=1, sticky="ew", pady=8)

        ttk.Label(
            frame,
            text="PASSWORD",
            background=fonts.CARD,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(row=2, column=0, sticky="w")

        p_wrap = ttk.Frame(frame, style="Soft.TFrame", padding=(12, 0))
        p_wrap.grid(row=3, column=0, sticky="ew", pady=(6, 12))
        p_wrap.columnconfigure(1, weight=1)
        ttk.Label(
            p_wrap, text="⚷", background=fonts.INPUT_BG, foreground=fonts.ACCENT, font=fonts.ff(12)
        ).grid(row=0, column=0, padx=(0, 6))
        self.signup_password = ttk.Entry(p_wrap, show="•")
        self.signup_password.grid(row=0, column=1, sticky="ew", pady=8)
        self.signup_password_toggle = ttk.Button(
            p_wrap,
            text="Show",
            style="Link.TButton",
            command=self._toggle_sign_up_password,
        )
        self.signup_password_toggle.grid(row=0, column=2, padx=(6, 0))

        ttk.Label(
            frame,
            text="CONFIRM PASSWORD",
            background=fonts.CARD,
            foreground=fonts.MUTED,
            font=fonts.ff(9, "bold"),
        ).grid(row=4, column=0, sticky="w")

        c_wrap = ttk.Frame(frame, style="Soft.TFrame", padding=(12, 0))
        c_wrap.grid(row=5, column=0, sticky="ew", pady=(6, 18))
        c_wrap.columnconfigure(1, weight=1)
        ttk.Label(
            c_wrap, text="⚷", background=fonts.INPUT_BG, foreground=fonts.ACCENT, font=fonts.ff(12)
        ).grid(row=0, column=0, padx=(0, 6))
        self.signup_confirm = ttk.Entry(c_wrap, show="•")
        self.signup_confirm.grid(row=0, column=1, sticky="ew", pady=8)
        self.signup_confirm.bind("<Return>", lambda e: self.sign_up_clicked())
        self.signup_confirm_toggle = ttk.Button(
            c_wrap,
            text="Show",
            style="Link.TButton",
            command=self._toggle_sign_up_confirm,
        )
        self.signup_confirm_toggle.grid(row=0, column=2, padx=(6, 0))

        ttk.Button(
            frame,
            text="Create Account →",
            style="Neon.TButton",
            command=self.sign_up_clicked,
        ).grid(row=6, column=0, sticky="ew", ipady=6)

        ttk.Label(
            frame,
            text="Already registered? Switch to Sign In above.",
            style="CardMuted.TLabel",
        ).grid(row=7, column=0, sticky="w", pady=(14, 0))

    def _toggle_sign_in_password(self):
        self._show_sign_in_password = not self._show_sign_in_password
        self.login_password.configure(show="" if self._show_sign_in_password else "•")
        self.login_password_toggle.configure(text="Hide" if self._show_sign_in_password else "Show")

    def _toggle_sign_up_password(self):
        self._show_sign_up_password = not self._show_sign_up_password
        self.signup_password.configure(show="" if self._show_sign_up_password else "•")
        self.signup_password_toggle.configure(text="Hide" if self._show_sign_up_password else "Show")

    def _toggle_sign_up_confirm(self):
        self._show_sign_up_confirm = not self._show_sign_up_confirm
        self.signup_confirm.configure(show="" if self._show_sign_up_confirm else "•")
        self.signup_confirm_toggle.configure(text="Hide" if self._show_sign_up_confirm else "Show")

    def set_status(self, text: str, level: str = "info"):
        colours = {
            "info": fonts.MUTED,
            "success": fonts.SUCCESS,
            "error": fonts.DANGER,
        }
        self.status_lbl.configure(text=text, fg=colours.get(level, fonts.MUTED))

    def show_sign_in(self):
        self.sign_up_frame.grid_remove()
        self.sign_in_frame.grid()
        self.sign_in_tab.configure(style="Neon.TButton")
        self.sign_up_tab.configure(style="Ghost.TButton")
        self.header_lbl.configure(text="Welcome back")
        self.subheader_lbl.configure(text="Sign in to continue to your library.")
        self.set_status("", "info")

    def show_sign_up(self):
        self.sign_in_frame.grid_remove()
        self.sign_up_frame.grid()
        self.sign_in_tab.configure(style="Ghost.TButton")
        self.sign_up_tab.configure(style="Neon.TButton")
        self.header_lbl.configure(text="Create an account")
        self.subheader_lbl.configure(text="Start building your own music library.")
        self.set_status("", "info")

    def open_main_app(self, user: dict):
        display_name = user.get("display_name") or user.get("username") or "User"
        self.root.destroy()

        app = JukeBoxApp(current_user=display_name, on_logout=launch_auth_app)
        app.run()

    def sign_in_clicked(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        success, message, user = auth_manager.authenticate_user(username, password)
        if not success:
            self.set_status(message, "error")
            return

        self.set_status(message, "success")
        self.open_main_app(user)

    def sign_up_clicked(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm_password = self.signup_confirm.get().strip()

        if password != confirm_password:
            self.set_status("Passwords do not match.", "error")
            return

        success, message = auth_manager.create_user(username, password)
        if not success:
            self.set_status(message, "error")
            return

        login_success, login_message, user = auth_manager.authenticate_user(username, password)
        if not login_success or user is None:
            self.set_status(login_message, "error")
            return

        self.set_status("Account created successfully.", "success")
        self.open_main_app(user)

    def run(self):
        self.root.mainloop()


def launch_auth_app():
    app = AuthApp()
    app.run()
