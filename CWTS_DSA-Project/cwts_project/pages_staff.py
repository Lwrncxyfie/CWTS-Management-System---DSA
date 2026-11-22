"""Instructor and admin pages: reports review, attendance, activities, QR, evaluations."""
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from config import BG, RED, GRAY, BORDER, UPLOAD_DIR
from store import db
from helpers import (find, person_name, activity_title, fmt, open_file,
                     all_students)

try:                                   # optional: QR code
    import qrcode
except ImportError:
    qrcode = None



class StaffPagesMixin:
    def staff_dashboard(self):
        pending = [r for r in db.reports if r["status"] == "Pending"]
        self.title_label(("Administrator" if self.role == "admin" else "Instructor") + " Dashboard")
        self.stats([(len(all_students()), "Students"), (len(db.activities), "Activities"),
                    (len(db.reports), "Total Reports"), (len(pending), "Pending Review")])
        card = self.card(fill="both", expand=True)
        self.label(card, "Pending Reports Needing Review", bold=True, size=12)
        self.table(card, [("Student", 200), ("Report Title", 350), ("Submitted", 200)],
                   [(r["id"], (person_name(r["student"]), r["title"], fmt(r["created"]))) for r in pending],
                   on_open=lambda rid: self.go(self.report_detail, int(rid)), empty="No pending reports!")
        self.label(card, "Double-click a report to review it.", muted=True, size=8)

    def staff_reports(self):
        self.title_label("Student Reports Management")
        card = self.card(fill="both", expand=True)
        self.table(card, [("Student", 160), ("Title", 250), ("Activity", 220), ("Date", 90), ("Status", 90), ("Submitted", 160)],
                   self.report_rows(db.reports, with_student=True), on_open=lambda rid: self.go(self.report_detail, int(rid)),
                   empty="No reports found.", height=15)
        self.label(card, "Double-click a report to view/review it.", muted=True, size=8)

    def staff_attendance(self):
        self.title_label("Attendance Log")
        card = self.card(fill="both", expand=True)
        self.table(card, [("Student", 200), ("Activity", 250), ("Time In", 180), ("Time Out", 180), ("Hours", 70)],
                   self.attendance_rows(db.attendance, with_student=True), empty="No attendance logs found.", height=15)

    def report_detail(self, rid):
        rep = find(db.reports, id=rid)
        head = tk.Frame(self.body, bg=BG)
        head.pack(fill="x")
        tk.Label(head, text=rep["title"], bg=BG, font=("Segoe UI", 18, "bold")).pack(side="left")
        self.pill(head, rep["status"]).pack(side="left", padx=10)

        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=8)
        details = tk.Frame(row, bg="white", highlightbackground=BORDER, highlightthickness=1, padx=15, pady=12)
        details.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.label(details, "Details", bold=True, size=12)
        self.label(details, f"Student: {person_name(rep['student'])}\nActivity: {activity_title(rep['activity_id'])}\n"
                            f"Date: {rep['date']}\nArea: {rep['area']} sq. m")
        self.label(details, rep["description"], pady=(8, 0))
        for c in rep["comments"]:
            self.label(details, f"{person_name(c['by'])} ({c['role']}): {c['text']}", muted=True, pady=(4, 0))

        proof = tk.Frame(row, bg="white", highlightbackground=BORDER, highlightthickness=1, padx=15, pady=12)
        proof.pack(side="left", fill="both", expand=True)
        self.label(proof, "Proof Files", bold=True, size=12)
        files = [d for d in db.documents if d["report_id"] == rid and d["kind"] == "photo"]
        for d in files:
            self.button(proof, f"Open {d['original']}", lambda s=d["stored"]: open_file(os.path.join(UPLOAD_DIR, s)),
                        color=GRAY, side="top", anchor="w", pady=2)
        if not files:
            self.label(proof, "No photos.", muted=True)

        if self.role in ("instructor", "admin"):
            card = self.card()
            self.label(card, "Review & Action", bold=True, size=12)
            comment = self.textbox(card, "Comment / Remarks")
            btns = tk.Frame(card, bg="white")
            btns.pack(anchor="w", pady=(10, 0))
            self.button(btns, "Approve", lambda: self.review(rid, "Approved", comment.get("1.0", "end")), side="left")
            self.button(btns, "Reject", lambda: self.review(rid, "Rejected", comment.get("1.0", "end")), color=RED, side="left")

    def review(self, rid, status, comment):
        rep = find(db.reports, id=rid)
        rep["status"] = status
        now = datetime.now().isoformat()
        if comment.strip():
            rep["comments"].append({"by": self.username, "role": self.role, "text": comment.strip(), "at": now})
        db.inbox.append({"to": rep["student"], "message": f"Your report '{rep['title']}' was {status}.", "read": False, "at": now})
        db.save()
        messagebox.showinfo("Review", f"Report status updated to {status}.")
        self.go(self.report_detail, rid)

    def staff_activities(self):
        self.title_label("Activities Management")
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 8))
        card = self.card(fill="both", expand=True)
        tree = self.table(card, [("Title", 220), ("Location", 180), ("Limit (sq.m)", 90), ("Max", 60), ("Goal", 380)],
                          [(a["id"], (a["title"], a["location"], a["area_limit"], a["max_participants"], a["goal"])) for a in db.activities],
                          empty="No activities found.", height=14)

        def selected(action):
            if tree is None or not tree.selection():
                return messagebox.showinfo("Activities", "Please select an activity first.")
            action(int(tree.selection()[0]))

        self.button(row, "+ Add New Activity", lambda: self.go(self.activity_form, None), side="left")
        self.button(row, "Edit Selected", lambda: selected(lambda aid: self.go(self.activity_form, aid)), color=GRAY, side="left")
        self.button(row, "QR Code", lambda: selected(self.show_qr), color=GRAY, side="left")

    def show_qr(self, aid):
        if qrcode is None:
            return messagebox.showerror("QR Code", "QR code library not installed.\nRun: pip install qrcode[pil]")
        path = os.path.join(UPLOAD_DIR, f"qr_{aid}.png")
        qrcode.make(f"CWTS-ACTIVITY-{aid}").save(path)
        win = tk.Toplevel(self)
        win.title(f"QR Code - {activity_title(aid)}")
        img = tk.PhotoImage(file=path)
        lab = tk.Label(win, image=img)
        lab.image = img                      # itago para hindi mawala ang larawan
        lab.pack(padx=20, pady=20)

    def activity_form(self, aid):
        act = find(db.activities, id=aid) if aid else None
        self.title_label(("Edit" if act else "Add") + " Activity")
        card = self.card()
        title = self.entry(card, "Title", act["title"] if act else "")
        goal = self.textbox(card, "Goal / Expected Outcome", act["goal"] if act else "")
        location = self.entry(card, "Location", act["location"] if act else "")
        start = self.entry(card, "Start (YYYY-MM-DD HH:MM)", act["start"].replace("T", " ") if act else "")
        end = self.entry(card, "End (YYYY-MM-DD HH:MM)", act["end"].replace("T", " ") if act else "")
        limit = self.entry(card, "Area Limit (sq. m)", act["area_limit"] if act else "")
        maxp = self.entry(card, "Max Participants", act["max_participants"] if act else "")

        def submit():
            try:
                data = {"title": title.get().strip(), "goal": goal.get("1.0", "end").strip(), "location": location.get().strip(),
                        "start": datetime.strptime(start.get(), "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M"),
                        "end": datetime.strptime(end.get(), "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M"),
                        "area_limit": float(limit.get()), "max_participants": int(maxp.get())}
                assert data["title"] and data["goal"] and data["location"]
            except (ValueError, AssertionError):
                return messagebox.showerror("Activity", "Please fill in all fields correctly (dates: YYYY-MM-DD HH:MM).")
            if act:
                act.update(data)
            else:
                data.update({"id": db.next_id("act"), "created_by": self.username})
                db.activities.append(data)
            db.save()
            messagebox.showinfo("Activity", "Activity saved!")
            self.go(self.staff_activities)

        self.button(card, "Save Activity", submit, pady=(12, 0))

    def evaluations(self):
        self.title_label("Evaluate Student Involvement")
        card = self.card()
        student = self.combo(card, "Student", [f"{s['username']} - {s['name']}" for s in all_students()])
        rating = self.combo(card, "Rating", ["5 - Excellent", "4 - Very Good", "3 - Good", "2 - Fair", "1 - Poor"], "5 - Excellent")
        remarks = self.entry(card, "Remarks")

        def submit():
            if not student.get() or not remarks.get().strip():
                return messagebox.showerror("Evaluation", "Please choose a student and enter remarks.")
            db.evaluations.append({"student": student.get().split(" - ")[0], "evaluator": self.username,
                                   "rating": int(rating.get()[0]), "remarks": remarks.get().strip(),
                                   "created": datetime.now().isoformat()})
            db.save()
            messagebox.showinfo("Evaluation", "Evaluation saved.")
            self.go(self.evaluations)

        self.button(card, "Save Evaluation", submit, pady=(12, 0))
        card = self.card(fill="both", expand=True)
        self.label(card, "Evaluation History", bold=True, size=12)
        self.table(card, [("Student", 200), ("Rating", 70), ("Remarks", 450), ("Date", 180)],
                   [(i, (person_name(e["student"]), e["rating"], e["remarks"], fmt(e["created"])))
                    for i, e in enumerate(reversed(db.evaluations))], empty="No evaluations yet.")
