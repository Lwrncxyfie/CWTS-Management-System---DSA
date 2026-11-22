"""Small helper functions: passwords, searching, name/date formatting, opening files."""
import hashlib, os, webbrowser
from datetime import datetime
from store import db



def hash_password(password):
    """Gawing 'scrambled' ang password (may random salt)."""
    salt = os.urandom(8).hex()
    return salt + "$" + hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()


def check_password(stored, password):
    salt, hashed = stored.split("$")
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex() == hashed


def find(items, **match):
    """Hanapin ang unang dictionary sa list na tugma. Hal: find(db.reports, id=5)"""
    for item in items:
        if all(str(item.get(k)) == str(v) for k, v in match.items()):
            return item
    return None


def person_name(username):
    user = db.users.get(username) or db.admins.get(username)
    return user["name"] if user else username


def activity_title(aid):
    act = find(db.activities, id=aid)
    return act["title"] if act else f"Activity #{aid}"


def fmt(value):
    """'2026-10-05T14:30:00' -> 'Oct 05, 2026 02:30 PM'"""
    if not value:
        return ""
    try:
        return datetime.fromisoformat(str(value)).strftime("%b %d, %Y %I:%M %p")
    except ValueError:
        return str(value)


def hours_text(h):
    return "%.2f" % h if h is not None else "-"


def open_file(path):
    """Buksan ang file gamit ang default program ng computer."""
    try:
        os.startfile(path)                       # Windows
    except AttributeError:
        webbrowser.open("file://" + path)        # Mac/Linux


def all_students():
    return [u for u in db.users.values() if u["role"] == "student"]
