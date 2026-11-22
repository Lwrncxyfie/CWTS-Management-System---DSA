"""Pages anyone can open: home, login, register, admin register."""
import tkinter as tk
from tkinter import messagebox
from config import BG, GRAY, BORDER, ADMIN_CODE, MAX_ADMINS
from store import db
from helpers import (hash_password, check_password)



class PublicPagesMixin:
    def home(self):
        box = self.card(pady=20, ipady=25)
        tk.Label(box, text="CWTS Activity Reporting & Monitoring System", bg="white", font=("Segoe UI", 20, "bold")).pack()
        tk.Label(box, text="Submit community service reports, track attendance, and keep CWTS records organised in one place.",
                 bg="white", fg=GRAY).pack(pady=8)
        row = tk.Frame(box, bg="white")
        row.pack()
        if self.username:
            self.button(row, "Go to My Dashboard", self.dashboard, side="left")
        else:
            self.button(row, "Log In", lambda: self.go(self.login, False), side="left")
            self.button(row, "Register (Student/Instructor)", lambda: self.go(self.register), color=GRAY, side="left")
        info = tk.Frame(self.body, bg=BG)
        info.pack(fill="x")
        for head, text in [("Students", "Time In & Out, activity reports, photo proof, service hour tracking."),
                           ("Instructors", "Verify & approve reports, monitor attendance, evaluate student involvement."),
                           ("Administrators", "Separate administrative portal, student management, analytics dashboard.")]:
            c = tk.Frame(info, bg="white", highlightbackground=BORDER, highlightthickness=1, padx=12, pady=10)
            c.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(c, text=head, bg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(c, text=text, bg="white", fg=GRAY, wraplength=280, justify="left").pack(anchor="w")
        if not self.username:
            tk.Button(self.body, text="Admin Portal", command=lambda: self.go(self.login, True, admin=True), bg=BG,
                      fg=GRAY, bd=0, cursor="hand2").pack(side="bottom", pady=10)

    def login(self, admin):
        card = self.card(pady=40)
        card.pack_configure(fill="none")
        self.label(card, "Administrator Login" if admin else "Log In", bold=True, size=16)
        user = self.entry(card, "Username")
        pw = self.entry(card, "Password", show="*")

        def submit(event=None):
            accounts = db.admins if admin else db.users
            acct = accounts.get(user.get().strip().lower())
            if acct and check_password(acct["password"], pw.get()):
                self.username, self.role = acct["username"], acct["role"]
                self.dashboard()
            else:
                messagebox.showerror("Login", "Invalid admin credentials." if admin else "Invalid username or password.")

        pw.bind("<Return>", submit)
        self.button(card, "Log In", submit, pady=(12, 0))
        if admin:
            self.label(card, f"No admin account yet? ({MAX_ADMINS - len(db.admins)} slots left)", muted=True, pady=(12, 0))
            self.button(card, "Register Admin", lambda: self.go(self.admin_register, admin=True), color=GRAY, pady=(4, 0))
            self.button(card, "Standard Login", lambda: self.go(self.login, False), color=GRAY, pady=(4, 0))
        else:
            self.button(card, "Create an account", lambda: self.go(self.register), color=GRAY, pady=(12, 0))

    def make_account(self, role, name, email, section, username, password):
        return {"username": username, "name": name.strip(), "email": email.strip(), "section": section.strip(),
                "role": role, "password": hash_password(password)}

    def register(self):
        card = self.card(pady=10)
        card.pack_configure(fill="none")
        self.label(card, "Create an Account", bold=True, size=16)
        role = self.combo(card, "I am a", ["student", "instructor"], "student")
        name, email = self.entry(card, "Full Name"), self.entry(card, "Email")
        section, user = self.entry(card, "Section / Course"), self.entry(card, "Username")
        pw, confirm = self.entry(card, "Password (min 6 characters)", show="*"), self.entry(card, "Confirm Password", show="*")

        def submit():
            username = user.get().strip().lower()
            if not (name.get().strip() and email.get().strip() and username and pw.get()):
                messagebox.showerror("Register", "Please fill in all required fields.")
            elif username in db.users or username in db.admins:
                messagebox.showerror("Register", "Username already exists.")
            elif len(pw.get()) < 6:
                messagebox.showerror("Register", "Password must be at least 6 characters.")
            elif pw.get() != confirm.get():
                messagebox.showerror("Register", "Passwords do not match.")
            else:
                db.users[username] = self.make_account(role.get(), name.get(), email.get(), section.get(), username, pw.get())
                db.save()
                messagebox.showinfo("Register", "Registration successful! Please log in.")
                self.go(self.login, False)

        self.button(card, "Register", submit, pady=(12, 0))
        self.button(card, "Back to Log In", lambda: self.go(self.login, False), color=GRAY, pady=(12, 0))

    def admin_register(self):
        slots = MAX_ADMINS - len(db.admins)
        card = self.card(pady=10)
        card.pack_configure(fill="none")
        self.label(card, "Admin Registration", bold=True, size=16)
        self.label(card, f"Max {MAX_ADMINS} administrator accounts allowed. {slots} slots left.", muted=True)
        if slots > 0:
            name, email, user = self.entry(card, "Full Name"), self.entry(card, "Email"), self.entry(card, "Username")
            pw, confirm = self.entry(card, "Password (min 8 characters)", show="*"), self.entry(card, "Confirm Password", show="*")
            code = self.entry(card, "Admin Registration Code", show="*")

            def submit():
                username = user.get().strip().lower()
                if code.get() != ADMIN_CODE:
                    messagebox.showerror("Admin", "Invalid registration code.")
                elif not (name.get().strip() and email.get().strip() and username):
                    messagebox.showerror("Admin", "Please fill in all required fields.")
                elif username in db.users or username in db.admins:
                    messagebox.showerror("Admin", "Username already exists.")
                elif len(pw.get()) < 8 or pw.get() != confirm.get():
                    messagebox.showerror("Admin", "Passwords must match and be at least 8 characters.")
                else:
                    db.admins[username] = self.make_account("admin", name.get(), email.get(), "", username, pw.get())
                    db.save()
                    messagebox.showinfo("Admin", "Admin registered! Please log in.")
                    self.go(self.login, True, admin=True)

            self.button(card, "Register Admin", submit, pady=(12, 0))
        self.button(card, "Back to Admin Login", lambda: self.go(self.login, True, admin=True), color=GRAY, pady=(12, 0))
