from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.json"

DEFAULT_USERNAME = "123"
DEFAULT_PASSWORD = "123"


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _normalise_username(username: str) -> str:
    return username.strip().casefold()


def _make_password_hash(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    if salt_hex is None:
        salt_hex = os.urandom(16).hex()

    salted = f"{salt_hex}:{password}".encode("utf-8")
    password_hash = hashlib.sha256(salted).hexdigest()
    return salt_hex, password_hash


def _verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
    _, actual_hash = _make_password_hash(password, salt_hex)
    return hmac.compare_digest(actual_hash, expected_hash)


def _default_user_record() -> dict:
    salt_hex, password_hash = _make_password_hash(DEFAULT_PASSWORD)
    return {
        _normalise_username(DEFAULT_USERNAME): {
            "username": DEFAULT_USERNAME,
            "display_name": DEFAULT_USERNAME,
            "salt": salt_hex,
            "password_hash": password_hash,
            "created_at": _now_text(),
            "last_login": None,
        }
    }


def _save_users(users: dict) -> bool:
    try:
        USERS_FILE.write_text(
            json.dumps(users, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except OSError:
        return False


def load_users() -> dict:
    if not USERS_FILE.exists():
        users = _default_user_record()
        _save_users(users)
        return users

    try:
        raw = USERS_FILE.read_text(encoding="utf-8")
        users = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        users = _default_user_record()
        _save_users(users)
        return users

    if not isinstance(users, dict):
        users = _default_user_record()
        _save_users(users)
        return users

    default_key = _normalise_username(DEFAULT_USERNAME)
    if default_key not in users:
        users[default_key] = _default_user_record()[default_key]
        _save_users(users)

    return users


def validate_username(username: str) -> str | None:
    username = username.strip()
    if username == "":
        return "Username cannot be empty."
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if len(username) > 30:
        return "Username must be 30 characters or fewer."
    return None


def validate_password(password: str) -> str | None:
    if password == "":
        return "Password cannot be empty."
    if len(password) < 4:
        return "Password must be at least 4 characters."
    return None


def create_user(username: str, password: str, display_name: str = "") -> tuple[bool, str]:
    username = username.strip()
    display_name = display_name.strip() or username

    username_error = validate_username(username)
    if username_error:
        return False, username_error

    password_error = validate_password(password)
    if password_error:
        return False, password_error

    users = load_users()
    lookup_key = _normalise_username(username)

    if lookup_key in users:
        return False, "That username already exists."

    salt_hex, password_hash = _make_password_hash(password)
    users[lookup_key] = {
        "username": username,
        "display_name": display_name,
        "salt": salt_hex,
        "password_hash": password_hash,
        "created_at": _now_text(),
        "last_login": None,
    }

    if not _save_users(users):
        return False, "Could not save the new account."

    return True, "Account created successfully."


def authenticate_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    username = username.strip()
    password = password.strip()

    if username == "" or password == "":
        return False, "Please enter both username and password.", None

    users = load_users()
    lookup_key = _normalise_username(username)
    user = users.get(lookup_key)

    if user is None:
        return False, "That account does not exist.", None

    salt_hex = user.get("salt", "")
    password_hash = user.get("password_hash", "")

    if not _verify_password(password, salt_hex, password_hash):
        return False, "Incorrect password.", None

    user["last_login"] = _now_text()
    users[lookup_key] = user
    _save_users(users)

    return True, "Login successful.", user