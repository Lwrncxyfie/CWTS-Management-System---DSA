"""Data layer: the Store class that holds all records and saves/loads them as JSON."""
import json, os, threading
from config import DATA_FILE, UPLOAD_DIR


class Store:
    DICTS = ["users", "admins", "hours", "counters"]
    LISTS = ["attendance", "reports", "documents", "activities",
             "inbox", "feedback", "announcements", "evaluations"]

    def __init__(self):
        for name in self.DICTS:
            setattr(self, name, {})
        for name in self.LISTS:
            setattr(self, name, [])
        self.photo_fingerprints = set()          # hash ng mga photo, para mahuli ang duplicate
        self._lock = threading.Lock()

    def next_id(self, kind):
        self.counters[kind] = self.counters.get(kind, 0) + 1
        return self.counters[kind]

    def save(self):
        with self._lock:
            data = {name: getattr(self, name) for name in self.DICTS + self.LISTS}
            data["photo_fingerprints"] = sorted(self.photo_fingerprints)
            with open(DATA_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(DATA_FILE + ".tmp", DATA_FILE)

    def load(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        for name in self.DICTS:
            getattr(self, name).update(data.get(name, {}))
        for name in self.LISTS:
            getattr(self, name).extend(data.get(name, []))
        self.photo_fingerprints.update(data.get("photo_fingerprints", []))


db = Store()
db.load()
