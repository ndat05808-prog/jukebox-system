from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import auth_manager
from . import font_manager as fonts
from .track_player import JukeBoxApp


class AuthApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JukeBox Login")
        self.root.geometry("900x560")
        self.root.minsize(760, 500)

        fonts.configure()
        fonts.apply_theme(self.root)

        self._build_ui()
        self.show_sign_in()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        wrapper = ttk.Frame(self.root, style="Root.TFrame", padding=24)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.columnconfigure(0, weight=1)
        wrapper.columnconfigure(1, weight=1)
        wrapper.rowconfigure(0, weight=1)

        left = ttk.Frame(wrapper, style="Card.TFrame", padding=24)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="JukeBox", style="Hero.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            left,
            text="Simple sign in system for your music application.",
            style="CardMuted.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(8, 18))

        info = (
            "Default account:\n"
            "Username: td123\n"
            "Password: td456\n\n"
            "New users can create an account with Sign Up.\n"
            "All created accounts are saved in data/users.json."
        )

        ttk.Label(
            left,
            text=info,
            style="Card.TLabel",
            justify="left"
        ).grid(row=2, column=0, sticky="nw")

        right = ttk.Frame(wrapper, style="Card.TFrame", padding=24)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        toggle = ttk.Frame(right, style="Card.TFrame")
        toggle.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        toggle.columnconfigure(0, weight=1)
        toggle.columnconfigure(1, weight=1)

        self.sign_in_tab = ttk.Button(toggle, text="Sign In", command=self.show_sign_in)
        self.sign_in_tab.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.sign_up_tab = ttk.Button(toggle, text="Sign Up", command=self.show_sign_up)
        self.sign_up_tab.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.forms_host = ttk.Frame(right, style="Card.TFrame")
        self.forms_host.grid(row=1, column=0, sticky="nsew")
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
            font=("Segoe UI", 10),
            anchor="w",
            justify="left"
        )
        self.status_lbl.grid(row=2, column=0, sticky="ew", pady=(16, 0))

    def _build_sign_in_form(self):
        ttk.Label(self.sign_in_frame, text="Username", style="Card.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.login_username = ttk.Entry(self.sign_in_frame)
        self.login_username.grid(row=1, column=0, sticky="ew", pady=(6, 12))

        ttk.Label(self.sign_in_frame, text="Password", style="Card.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        self.login_password = ttk.Entry(self.sign_in_frame, show="*")
        self.login_password.grid(row=3, column=0, sticky="ew", pady=(6, 14))
        self.login_password.bind("<Return>", lambda event: self.sign_in_clicked())

        ttk.Button(
            self.sign_in_frame,
            text="Sign In",
            style="Neon.TButton",
            command=self.sign_in_clicked
        ).grid(row=4, column=0, sticky="ew")

    def _build_sign_up_form(self):
        ttk.Label(self.sign_up_frame, text="Username", style="Card.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.signup_username = ttk.Entry(self.sign_up_frame)
        self.signup_username.grid(row=1, column=0, sticky="ew", pady=(6, 12))

        ttk.Label(self.sign_up_frame, text="Password", style="Card.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        self.signup_password = ttk.Entry(self.sign_up_frame, show="*")
        self.signup_password.grid(row=3, column=0, sticky="ew", pady=(6, 12))

        ttk.Label(self.sign_up_frame, text="Confirm Password", style="Card.TLabel").grid(
            row=4, column=0, sticky="w"
        )
        self.signup_confirm = ttk.Entry(self.sign_up_frame, show="*")
        self.signup_confirm.grid(row=5, column=0, sticky="ew", pady=(6, 14))
        self.signup_confirm.bind("<Return>", lambda event: self.sign_up_clicked())

        ttk.Button(
            self.sign_up_frame,
            text="Create Account",
            style="Neon.TButton",
            command=self.sign_up_clicked
        ).grid(row=6, column=0, sticky="ew")

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
        self.set_status("Sign in with your account.", "info")

    def show_sign_up(self):
        self.sign_in_frame.grid_remove()
        self.sign_up_frame.grid()
        self.sign_in_tab.configure(style="Ghost.TButton")
        self.sign_up_tab.configure(style="Neon.TButton")
        self.set_status("Create a new account.", "info")

    def open_main_app(self, user: dict):
        display_name = user.get("display_name") or user.get("username") or "User"
        self.root.destroy()

        app = JukeBoxApp(
            current_user=display_name,
            on_logout=launch_auth_app
        )
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