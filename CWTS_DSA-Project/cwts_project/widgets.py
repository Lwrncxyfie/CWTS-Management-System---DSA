"""Reusable Tkinter widget builders (card, label, button, entry, table...). Shared by every page."""
import tkinter as tk
from tkinter import ttk
from config import BG, GRAY, BORDER, STATUS_COLORS



class WidgetMixin:
    """Small building blocks used by all pages."""

    def title_label(self, text):
        tk.Label(self.body, text=text, bg=BG, font=("Segoe UI", 18, "bold"), fg="#222").pack(anchor="w", pady=(0, 10))

    def card(self, parent=None, **pack):
        frame = tk.Frame(parent or self.body, bg="white", highlightbackground=BORDER, highlightthickness=1, padx=15, pady=12)
        frame.pack(**({"fill": "x", "pady": 6} | pack))
        return frame

    def label(self, parent, text, bold=False, muted=False, size=10, bg="white", **pack):
        lab = tk.Label(parent, text=text, bg=bg, font=("Segoe UI", size, "bold" if bold else "normal"),
                       fg=GRAY if muted else "#333", justify="left", anchor="w", wraplength=950)
        lab.pack(**({"anchor": "w"} | pack))
        return lab

    def button(self, parent, text, command, color=None, **pack):
        b = tk.Button(parent, text=text, command=command, bg=color or self.color, fg="white", bd=0, padx=14, pady=5,
                      activebackground=color or self.color, activeforeground="white", cursor="hand2", font=("Segoe UI", 10))
        opts = {"side": "top", "anchor": "w"} | pack          # default: nakapatong; side="left" = magkatabi
        if opts["side"] == "left":
            opts.setdefault("padx", (0, 8))
        b.pack(**opts)
        return b

    def entry(self, parent, text, value="", show="", state="normal"):
        self.label(parent, text, bold=True, size=9, pady=(8, 0))
        e = tk.Entry(parent, show=show, relief="solid", bd=1, font=("Segoe UI", 10))
        e.insert(0, value)
        e.configure(state=state)
        e.pack(fill="x", ipady=3)
        return e

    def textbox(self, parent, text, value="", height=4):
        self.label(parent, text, bold=True, size=9, pady=(8, 0))
        t = tk.Text(parent, height=height, relief="solid", bd=1, font=("Segoe UI", 10))
        t.insert("1.0", value)
        t.pack(fill="x")
        return t

    def combo(self, parent, text, values, value=""):
        self.label(parent, text, bold=True, size=9, pady=(8, 0))
        c = ttk.Combobox(parent, values=values, state="readonly", font=("Segoe UI", 10))
        c.set(value)
        c.pack(fill="x", ipady=2)
        return c

    def stats(self, items):
        """Mga kahon ng numero sa dashboard. items = [(numero, paliwanag), ...]"""
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 8))
        for value, caption in items:
            box = tk.Frame(row, bg="white", highlightbackground=BORDER, highlightthickness=1, padx=10, pady=12)
            box.pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(box, text=str(value), bg="white", fg=self.color, font=("Segoe UI", 20, "bold")).pack()
            tk.Label(box, text=caption, bg="white", fg=GRAY).pack()

    def table(self, parent, columns, rows, on_open=None, empty="No data.", height=8):
        """columns = [(pangalan, lapad)], rows = [(iid, (values...))]. Double-click = on_open(iid)."""
        if not rows:
            self.label(parent, empty, muted=True)
            return None
        ids = [f"c{i}" for i in range(len(columns))]
        tree = ttk.Treeview(parent, columns=ids, show="headings", height=height)
        for cid, (name, width) in zip(ids, columns):
            tree.heading(cid, text=name)
            tree.column(cid, width=width, anchor="w")
        for iid, values in rows:
            tree.insert("", "end", iid=str(iid), values=values)
        if on_open:
            tree.bind("<Double-1>", lambda e: tree.selection() and on_open(tree.selection()[0]))
        tree.pack(fill="both", expand=True)
        return tree

    def pill(self, parent, status):
        bg, fg = STATUS_COLORS.get(status, ("#dbeafe", "#1e40af"))
        return tk.Label(parent, text=f" {status} ", bg=bg, fg=fg, font=("Segoe UI", 9, "bold"))
