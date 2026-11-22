"""The main window: sets up the app, navigation (go), header menu and logout. Pages live in pages_*.py."""
import tkinter as tk
from tkinter import ttk
from config import BG, BLUE, NAVY
from store import db
from helpers import person_name
from widgets import WidgetMixin
from pages_public import PublicPagesMixin
from pages_student import StudentPagesMixin
from pages_staff import StaffPagesMixin
from pages_admin import AdminPagesMixin
from pages_common import CommonPagesMixin



class App(PublicPagesMixin, StudentPagesMixin, StaffPagesMixin, AdminPagesMixin, CommonPagesMixin, WidgetMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CWTS Management System")
        self.geometry("1100x700")
        self.minsize(950, 600)
        self.configure(bg=BG)
        self.username = self.role = None         # sino ang naka-login
        self.admin_portal = False                # nasa admin login/register screen ba?

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#f8fafc")

        self.header = tk.Frame(self)
        self.header.pack(fill="x")
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True, padx=25, pady=15)
        self.go(self.home)

    # ---------- navigation ----------
    @property
    def color(self):
        return NAVY if self.role == "admin" or self.admin_portal else BLUE

    def go(self, page, *args, admin=False):
        """Palitan ang page: burahin ang laman, iguhit ang header, tapos gumawa ng bagong page."""
        self.admin_portal = admin
        for w in self.body.winfo_children():
            w.destroy()
        self.draw_header()
        page(*args)

    def dashboard(self):
        self.go(self.student_dashboard if self.role == "student" else self.staff_dashboard)

    def draw_header(self):
        for w in self.header.winfo_children():
            w.destroy()
        self.header.configure(bg=self.color)
        tk.Button(self.header, text="CWTS  " + ("Admin Portal" if self.color == NAVY else "Management System"),
                  command=lambda: self.go(self.home), bg=self.color, fg="white", bd=0, activebackground=self.color,
                  activeforeground="white", font=("Segoe UI", 11, "bold"), cursor="hand2").pack(side="left", padx=15, pady=10)
        if not self.username:
            return
        menus = {
            "student": [("Dashboard", self.student_dashboard), ("Time In/Out", self.student_attendance),
                        ("My Reports", self.student_reports), ("Submit Report", self.report_form)],
            "instructor": [("Dashboard", self.staff_dashboard), ("Reports", self.staff_reports),
                           ("Attendance", self.staff_attendance), ("Evaluations", self.evaluations),
                           ("Activities", self.staff_activities)],
            "admin": [("Dashboard", self.staff_dashboard), ("Students", self.admin_students),
                      ("Activities", self.staff_activities), ("Reports", self.staff_reports),
                      ("Attendance", self.staff_attendance), ("Analytics", self.admin_analytics)],
        }
        for text, page in menus[self.role] + [("Announcements", self.announcements), ("Feedback", self.feedback)]:
            tk.Button(self.header, text=text, command=lambda p=page: self.go(p), bg=self.color, fg="white", bd=0,
                      activebackground=self.color, activeforeground="white", cursor="hand2").pack(side="left", padx=6)
        tk.Button(self.header, text="Logout", command=self.logout, bg=self.color, fg="white", bd=1, cursor="hand2",
                  relief="solid").pack(side="right", padx=15)
        tk.Label(self.header, text=f"{person_name(self.username)} ({self.role})", bg=self.color, fg="white").pack(side="right")
        unread = len([n for n in db.inbox if n.get("to") == self.username and not n.get("read")])
        tk.Button(self.header, text="\U0001F514" + (f" {unread}" if unread else ""), command=lambda: self.go(self.notifications),
                  bg=self.color, fg="white", bd=0, activebackground=self.color, cursor="hand2").pack(side="right", padx=10)

    def logout(self):
        self.username = self.role = None
        self.go(self.home)
