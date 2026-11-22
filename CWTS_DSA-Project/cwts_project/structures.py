"""Activity 2 data structures: Dictionary, List and Queue.
Not used by the app yet. Phase 4 of WORK_PLAN.md plugs them into store.py and the pages."""
from collections import deque


class RecordDictionary:
    """Stores records by ID for fast lookup."""

    def __init__(self):
        self.d = {}

    def add(self, key, value):
        """Add a record. Returns False if the key is blank or already exists."""
        if not key or key in self.d:
            return False
        self.d[key] = value
        return True

    def get(self, key):
        """Return the record for a key, or None if it is not found."""
        return self.d.get(key)

    def update(self, key, value):
        """Change an existing record. Returns False if the key is not found."""
        if key not in self.d:
            return False
        self.d[key] = value
        return True

    def remove(self, key):
        """Delete and return a record, or None if it is not found."""
        return self.d.pop(key, None)

    def view_all(self):
        """Return all records as (key, value) pairs (empty list if none)."""
        return list(self.d.items())

    def is_empty(self):
        return len(self.d) == 0

    def size(self):
        return len(self.d)


class RecordList:
    """Keeps records in the order they were added."""

    def __init__(self):
        self.items = []

    def add(self, record):
        """Add a record to the end of the list."""
        self.items.append(record)

    def remove(self, record):
        """Remove a record. Returns None if it is not in the list."""
        if record not in self.items:
            return None
        self.items.remove(record)
        return record

    def get(self, index):
        """Return the record at an index, or None if the index is invalid."""
        if index < 0 or index >= len(self.items):
            return None
        return self.items[index]

    def view_all(self):
        """Return all records (empty list if there are none)."""
        return list(self.items)

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class ServiceQueue:
    """Waiting line of service requests. First in, first out."""

    def __init__(self):
        self.q = deque()

    def enqueue(self, req):
        """Add a request to the back of the line."""
        self.q.append(req)

    def dequeue(self):
        """Remove and return the front request, or None if the queue is empty."""
        if not self.q:
            return None
        return self.q.popleft()

    def peek(self):
        """Look at the front request without removing it (None if empty)."""
        return self.q[0] if self.q else None

    def is_empty(self):
        return len(self.q) == 0

    def size(self):
        return len(self.q)

    def to_list(self):
        return list(self.q)
