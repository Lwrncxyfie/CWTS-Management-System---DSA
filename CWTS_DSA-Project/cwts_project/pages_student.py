"""Student pages: dashboard, time in/out, attendance log, reports."""
import hashlib, os, shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from config import BG, RED, GRAY, UPLOAD_DIR
from store import db
from helpers import (person_name, activity_title, fmt, hours_text)



class StudentPagesMixin:
    def active_session(self, username):
        """Attendance record na naka-time in pero wala pang time out."""
        return next((a for a in db.attendance if a["student"] == username and not a.get("time_out")), None)

    def activity_choices(self):
        return [f"{a['id']} - {a['title']}" for a in db.activities]

    def report_rows(self, reports, with_student=False):
        rows = []
        for r in reports:
            values = (person_name(r["student"]),) if with_student else ()
            rows.append((r["id"], values + (r["title"], activity_title(r["activity_id"]), r["date"], r["status"], fmt(r["created"]))))
        return rows

    def student_dashboard(self):
        u = self.username
        mine = [r for r in db.reports if r["student"] == u]
        active = self.active_session(u)
        self.title_label("Student Dashboard")
        self.stats([("%.2f" % db.hours.get(u, 0.0), "Total Service Hours"), (len(mine), "Reports Submitted"),
                    (fmt(active["time_in"]) if active else "None", "Active Time-In")])

        card = self.card()
        self.label(card, "Active Activity Time In / Time Out", bold=True, size=12)
        if active:
            self.label(card, f"Timed in at: {fmt(active['time_in'])}")
            self.button(card, "Time Out Now", self.time_out, color=RED, pady=(6, 0))
        else:
            choice = self.combo(card, "Select Activity", self.activity_choices())
            self.button(card, "Time In Now", lambda: self.time_in(choice.get()), pady=(8, 0))

        card = self.card(fill="both", expand=True)
        self.label(card, "Recent Activity Reports", bold=True, size=12)
        self.table(card, [("Title", 300), ("Date", 120), ("Area (sq.m)", 100), ("Status", 100)],
                   [(r["id"], (r["title"], r["date"], r["area"], r["status"])) for r in mine[:5]],
                   on_open=lambda rid: self.go(self.report_detail, int(rid)), empty="No reports submitted yet.")
        self.label(card, "Double-click a report to view it.", muted=True, size=8)

    def time_in(self, choice):
        if not choice:
            return messagebox.showerror("Time In", "Please select an activity.")
        if self.active_session(self.username):
            return messagebox.showerror("Time In", "You are already timed in to an activity.")
        db.attendance.append({"id": db.next_id("att"), "student": self.username, "activity_id": choice.split(" - ")[0],
                              "time_in": datetime.now().isoformat(), "time_out": None, "hours": None})
        db.save()
        messagebox.showinfo("Time In", "Timed in successfully!")
        self.go(self.student_dashboard)

    def time_out(self):
        u = self.username
        record = self.active_session(u)
        if record:
            now = datetime.now()
            hours = max(0.0, (now - datetime.fromisoformat(record["time_in"])).total_seconds() / 3600)
            record["time_out"], record["hours"] = now.isoformat(), hours
            db.hours[u] = db.hours.get(u, 0.0) + hours
            db.save()
            messagebox.showinfo("Time Out", f"Timed out. Service hours recorded: {hours:.2f} hrs.")
        self.go(self.student_dashboard)

    def attendance_rows(self, records, with_student=False):
        rows = []
        for r in records:
            values = (person_name(r["student"]),) if with_student else ()
            rows.append((r["id"], values + (activity_title(r["activity_id"]), fmt(r["time_in"]),
                                           fmt(r["time_out"]) if r["time_out"] else "In Progress", hours_text(r["hours"]))))
        return rows

    def student_attendance(self):
        self.title_label("My Attendance Log")
        card = self.card(fill="both", expand=True)
        self.table(card, [("Activity", 300), ("Time In", 200), ("Time Out", 200), ("Hours", 80)],
                   self.attendance_rows([a for a in db.attendance if a["student"] == self.username]),
                   empty="No attendance history found.", height=15)

    def student_reports(self):
        self.title_label("My Activity Reports")
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 8))
        self.button(row, "+ Submit New Report", self.report_form, side="left")
        card = self.card(fill="both", expand=True)
        self.table(card, [("Title", 250), ("Activity", 250), ("Date", 100), ("Status", 90), ("Submitted", 180)],
                   self.report_rows([r for r in db.reports if r["student"] == self.username]),
                   on_open=lambda rid: self.go(self.report_detail, int(rid)), empty="No reports submitted.", height=15)
        self.label(card, "Double-click a report to view it.", muted=True, size=8)

    def report_form(self):
        self.title_label("Submit Activity Report")
        card = self.card()
        activity = self.combo(card, "Activity", [f"{a['id']} - {a['title']} (Limit: {a['area_limit']} sq. m)" for a in db.activities])
        title = self.entry(card, "Report Title")
        row = tk.Frame(card, bg="white")
        row.pack(fill="x")
        left, right = tk.Frame(row, bg="white"), tk.Frame(row, bg="white")
        left.pack(side="left", fill="x", expand=True, padx=(0, 8))
        right.pack(side="left", fill="x", expand=True)
        date = self.entry(left, "Activity Date (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
        area = self.entry(right, "Area Covered (sq. m)")
        desc = self.textbox(card, "What was done")
        photos = []                                           # mga piniling photo (full path)

        self.label(card, "Photos (required) - duplicate photos will be rejected", bold=True, size=9, pady=(8, 0))
        photo_label = self.label(card, "No photos selected.", muted=True)

        def choose():
            files = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")])
            if files:
                photos[:] = list(files)
                photo_label.config(text=", ".join(os.path.basename(p) for p in photos))

        self.button(card, "Choose Photos...", choose, color=GRAY, pady=(4, 0))

        def submit():
            try:
                datetime.strptime(date.get(), "%Y-%m-%d")
                area_value = float(area.get())
                assert area_value > 0
            except (ValueError, AssertionError):
                return messagebox.showerror("Report", "Please enter a valid date (YYYY-MM-DD) and an area greater than 0.")
            if not (activity.get() and title.get().strip() and desc.get("1.0", "end").strip() and photos):
                return messagebox.showerror("Report", "Please fill in all fields and choose at least one photo.")
            # fingerprint (MD5 hash) ng bawat photo; kapareho ng dati = duplicate
            prints = []
            for path in photos:
                with open(path, "rb") as f:
                    prints.append(hashlib.md5(f.read()).hexdigest())
            if any(p in db.photo_fingerprints for p in prints):
                return messagebox.showerror("Report", "Duplicate photo detected. Please upload unique images.")
            rid = db.next_id("rep")
            for path, fp in zip(photos, prints):
                db.photo_fingerprints.add(fp)
                stored = f"{rid}_photo_{os.path.basename(path)}".replace(" ", "_")
                shutil.copy(path, os.path.join(UPLOAD_DIR, stored))
                db.documents.append({"report_id": rid, "kind": "photo", "original": os.path.basename(path), "stored": stored})
            db.reports.append({"id": rid, "student": self.username, "activity_id": activity.get().split(" - ")[0],
                               "title": title.get().strip(), "date": date.get(), "area": area_value,
                               "description": desc.get("1.0", "end").strip(), "status": "Pending",
                               "created": datetime.now().isoformat(), "comments": []})
            db.save()
            messagebox.showinfo("Report", "Report submitted successfully!")
            self.go(self.student_reports)

        self.button(card, "Submit Report", submit, pady=(12, 0))
