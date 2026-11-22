"""Admin-only pages: student management and analytics."""
import tkinter as tk
from tkinter import messagebox
from config import BG, GRAY
from store import db
from helpers import (hash_password, all_students)



class AdminPagesMixin:
    def admin_students(self):
        self.title_label("Student Management")
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 8))
        card = self.card(fill="both", expand=True)
        tree = self.table(card, [("Name", 200), ("Username", 130), ("Email", 220), ("Section", 100), ("Hours", 80)],
                          [(s["username"], (s["name"], s["username"], s["email"], s["section"] or "-", "%.2f" % db.hours.get(s["username"], 0)))
                           for s in all_students()], empty="No students registered.", height=14)

        def edit():
            if tree is None or not tree.selection():
                return messagebox.showinfo("Students", "Please select a student first.")
            self.go(self.student_form, tree.selection()[0])

        self.button(row, "+ Add New Student", lambda: self.go(self.student_form, None), side="left")
        self.button(row, "Edit Selected", edit, color=GRAY, side="left")

    def student_form(self, username):
        stu = db.users.get(username) if username else None
        self.title_label(("Edit" if stu else "Add") + " Student")
        card = self.card()
        name, email = self.entry(card, "Full Name", stu["name"] if stu else ""), self.entry(card, "Email", stu["email"] if stu else "")
        section = self.entry(card, "Section", stu["section"] if stu else "")
        user = self.entry(card, "Username", stu["username"] if stu else "", state="disabled" if stu else "normal")
        pw = self.entry(card, "Password (leave blank to keep current)" if stu else "Password", show="*")

        def submit():
            if not (name.get().strip() and email.get().strip()) or (not stu and not (user.get().strip() and pw.get())):
                return messagebox.showerror("Student", "Please fill in all required fields.")
            if stu:
                stu.update({"name": name.get().strip(), "email": email.get().strip(), "section": section.get().strip()})
                if pw.get():
                    stu["password"] = hash_password(pw.get())
            else:
                uname = user.get().strip().lower()
                if uname in db.users or uname in db.admins:
                    return messagebox.showerror("Student", "Student already exists.")
                db.users[uname] = self.make_account("student", name.get(), email.get(), section.get(), uname, pw.get())
            db.save()
            messagebox.showinfo("Student", "Student saved.")
            self.go(self.admin_students)

        self.button(card, "Save", submit, pady=(12, 0))

    def admin_analytics(self):
        n, total = len(all_students()), sum(db.hours.values())
        self.title_label("Data Analytics")
        self.stats([(n, "Total Students"), ("%.2f" % total, "Total Hours"), ("%.2f" % (total / n if n else 0.0), "Avg Hours/Student")])
