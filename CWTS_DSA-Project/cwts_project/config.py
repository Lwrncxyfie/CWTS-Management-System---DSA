"""Settings and constants: file paths, admin limits, colours. Change look and limits here."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "cwts_data.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ADMIN_CODE, MAX_ADMINS = "ADMIN2026", 3


# kulay (galing sa orihinal na website)
BG, BLUE, NAVY, RED, GRAY, BORDER = "#f4f6f9", "#3c25eb", "#1b2a47", "#dc2626", "#b80000", "#e2e8f0"
STATUS_COLORS = {"Approved": ("#dcfce7", "#166534"), "Pending": ("#fef9c3", "#854d0e"), "Rejected": ("#fee2e2", "#991b1b")}
