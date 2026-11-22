"""Pages shared by all roles: announcements, feedback, notifications."""
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from config import GRAY
from store import db
from helpers import (person_name, fmt)



class CommonPagesMixin:
    def announcements(self):
        self.title_label("Announcements")
        if self.role in ("instructor", "admin"):
            card = self.card()
            title, message = self.entry(card, "Title"), self.textbox(card, "Message", height=3)

            def post():
                if not (title.get().strip() and message.get("1.0", "end").strip()):
                    return messagebox.showerror("Announcement", "Please enter a title and a message.")
                db.announcements.append({"id": db.next_id("anc"), "title": title.get().strip(), "body": message.get("1.0", "end").strip(),
                                         "author": self.username, "author_role": self.role, "created": datetime.now().isoformat()})
                db.save()
                self.go(self.announcements)

            self.button(card, "Post Announcement", post, pady=(10, 0))
        box = tk.Text(self.body, wrap="word", relief="solid", bd=1, font=("Segoe UI", 10), padx=10, pady=8)
        box.tag_configure("h", font=("Segoe UI", 13, "bold"))
        box.tag_configure("m", foreground=GRAY)
        for a in reversed(db.announcements):
            box.insert("end", a["title"] + "\n", "h")
            box.insert("end", a["body"] + "\n")
            box.insert("end", f"Posted by {person_name(a['author'])} on {fmt(a['created'])}\n\n", "m")
        if not db.announcements:
            box.insert("end", "No announcements yet.", "m")
        box.configure(state="disabled")
        box.pack(fill="both", expand=True, pady=8)

    def feedback(self):
        self.title_label("Feedback & Suggestions")
        card = self.card()
        kind = self.combo(card, "Type", ["Feedback", "Suggestion"], "Feedback")
        message = self.textbox(card, "Message", height=3)

        def send():
            if not message.get("1.0", "end").strip():
                return messagebox.showerror("Feedback", "Please type a message.")
            db.feedback.append({"from": self.username, "role": self.role, "kind": kind.get(),
                                "message": message.get("1.0", "end").strip(), "created": datetime.now().isoformat()})
            db.save()
            messagebox.showinfo("Feedback", "Feedback sent!")
            self.go(self.feedback)

        self.button(card, "Send", send, pady=(10, 0))
        # students: sarili lang nilang feedback ang makikita; staff: lahat
        items = [f for f in db.feedback if self.role != "student" or f["from"] == self.username]
        card = self.card(fill="both", expand=True)
        self.label(card, "History", bold=True, size=12)
        self.table(card, [("Date", 180), ("Type", 100), ("Message", 600)],
                   [(i, (fmt(f["created"]), f["kind"], f["message"])) for i, f in enumerate(reversed(items))], empty="No entries.")

    def notifications(self):
        self.title_label("Notifications")
        items = [n for n in db.inbox if n.get("to") == self.username]
        card = self.card(fill="both", expand=True)
        if not items:
            self.label(card, "No notifications.", muted=True)
        for n in reversed(items):
            self.label(card, f"{fmt(n['at'])}:  {n['message']}", pady=3)
            n["read"] = True                         # nabasa na
        db.save()
        self.draw_header()                           # i-refresh ang bilang ng unread sa kampana
