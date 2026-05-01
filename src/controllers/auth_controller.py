"""Auth controller: handles sign-in / sign-up business flow.

Owns an ``AuthView`` and an ``auth_manager`` model.  The view renders forms;
the controller validates input, talks to the model, and on success destroys
the auth window and launches the main app.
"""

from __future__ import annotations

from ..models import auth_manager
from ..views.auth_view import AuthView


class AuthController:
    def __init__(self):
        self.view = AuthView()
        self.view.on_sign_in_clicked = self.handle_sign_in
        self.view.on_sign_up_clicked = self.handle_sign_up

    def handle_sign_in(self):
        username, password = self.view.get_login_inputs()

        success, message, user = auth_manager.authenticate_user(username, password)
        if not success:
            self.view.set_status(message, "error")
            return

        self.view.set_status(message, "success")
        self._open_main_app(user)

    def handle_sign_up(self):
        username, password, confirm = self.view.get_signup_inputs()

        if password != confirm:
            self.view.set_status("Passwords do not match.", "error")
            return

        success, message = auth_manager.create_user(username, password)
        if not success:
            self.view.set_status(message, "error")
            return

        login_success, login_message, user = auth_manager.authenticate_user(username, password)
        if not login_success or user is None:
            self.view.set_status(login_message, "error")
            return

        self.view.set_status("Account created successfully.", "success")
        self._open_main_app(user)

    def _open_main_app(self, user: dict):
        from .main_controller import JukeBoxApp

        display_name = user.get("display_name") or user.get("username") or "User"
        self.view.close()

        app = JukeBoxApp(current_user=display_name, on_logout=launch_auth_app)
        app.run()

    def run(self):
        self.view.run()


def launch_auth_app():
    AuthController().run()
