# CWTS Management System: Work Plan

A guide for learning and modifying the project step by step. The original single file (`reference/frontend_original.py`, 830 lines) was split into small modules **without changing any logic**, so the app behaves exactly as before. A headless test opened all 20+ pages without errors.

---

## 1. Choose your IDE

**Recommendation: VS Code.**

| | VS Code | PyCharm |
|---|---|---|
| Cost | Free | Free core features (JetBrains now ships one unified PyCharm; a 30-day Pro trial starts after install, then the core stays free) |
| Weight | Light, starts fast, fine on a modest laptop | Heavier, uses more memory |
| Python support | Good, via the Python extension | Excellent out of the box |
| Refactoring (rename across files) | Good | Best in class |
| Other files (HTML, JS, JSON, Markdown) | Great. You can keep the earlier web prototype in the same editor | Fine, but Python is its focus |
| Learning curve | Easy | A bit more to learn (project settings, run configurations) |

**Why VS Code for this project:** it is light, you can edit the web prototype and the Python app in one window, and the project already includes `.vscode/` settings so F5 runs the app. Choose **PyCharm** instead if your laptop has plenty of RAM and you want the strongest rename/refactor tools and an all-in-one Python experience.

### Setup (VS Code)
1. Install **Python 3.9 or newer** from python.org. On Windows, tick **Add Python to PATH**. (3.9+ is required because the code uses the `|` dict merge.)
2. Check Tkinter works: run `python -m tkinter`. A small window should open. On Linux: `sudo apt install python3-tk`.
3. Install VS Code, then the extensions **Python** and **Python Debugger** (both from Microsoft).
4. `File > Open Folder...` and choose the `cwts_project` folder.
5. `Ctrl+Shift+P > Python: Select Interpreter` and pick your Python.
6. Press **F5** (or run `python main.py` in the terminal). The login screen appears.
7. Optional: `pip install qrcode[pil]` for the QR Code button.

### Useful shortcuts
| Action | VS Code | PyCharm |
|---|---|---|
| Jump to a function's definition | F12 | Ctrl+B |
| Find where it is used | Shift+F12 | Alt+F7 |
| Search all files | Ctrl+Shift+F | Ctrl+Shift+F |
| Go to symbol in file | Ctrl+Shift+O | Ctrl+F12 |
| Breakpoint | F9 | Ctrl+F8 |
| Run / debug | F5 | Shift+F10 / Shift+F9 |

---

## 2. Project map

```
cwts_project/
  main.py            Start here. Runs the app.
  app.py             The App window: setup, go() navigation, header menu, logout.
  config.py          Constants: file paths, admin code, colours.
  store.py           The Store class (all data) + saving/loading JSON.
  helpers.py         Password hashing, find(), formatting, open_file().
  widgets.py         Reusable widget builders (card, label, button, entry, table...).
  pages_public.py    Home, login, register, admin register.
  pages_student.py   Student pages and time in/out.
  pages_staff.py     Instructor/admin pages: reports, attendance, activities, QR, evaluations.
  pages_admin.py     Admin-only: student management, analytics.
  pages_common.py    Announcements, feedback, notifications.
  structures.py      Activity 2: RecordDictionary, RecordList, ServiceQueue (not wired in yet).
  algorithms.py      Activity 3: binary_search, selection_sort (not wired in yet).
  tests/             Unit tests (python -m unittest discover tests).
  reference/         The untouched original file, for comparison.
  cwts_data.json     Created on first run. This is your database. Delete it to reset.
  uploads/           Created on first run. Report photos and QR images.
```

**How the pages are connected.** `App` inherits from one mixin per page group (`PublicPagesMixin`, `StudentPagesMixin`, and so on). Every page is a method, so `self.card()` inside `pages_student.py` still works. It is defined in `widgets.py` and combined into `App` at runtime.

**How a click works.** A button calls `self.go(page, *args)`, which does three things in order: it destroys everything in `self.body`, redraws the header (`draw_header`), then calls `page(*args)`, which draws the new screen. To add a page, write one method and call `self.go(self.my_page)` from a button.

**Who sees which menu** (set in `App.draw_header`):

| Role | Menu |
|---|---|
| student | Dashboard, Time In/Out, My Reports, Submit Report, Announcements, Feedback |
| instructor | Dashboard, Reports, Attendance, Evaluations, Activities, Announcements, Feedback |
| admin | Dashboard, Students, Activities, Reports, Attendance, Analytics, Announcements, Feedback |

---

## 3. Function reference

### `config.py` (constants, no functions)
`BASE_DIR`, `DATA_FILE`, `UPLOAD_DIR`, `ADMIN_CODE`, `MAX_ADMINS`, colours `BG BLUE NAVY RED GRAY BORDER`, and `STATUS_COLORS` (pill colours for Approved, Pending, Rejected).

### `store.py`: class `Store` (the data layer)
| Function | What it does |
|---|---|
| `__init__` | Creates the empty dicts (`users`, `admins`, `hours`, `counters`) and lists (`attendance`, `reports`, `documents`, `activities`, `inbox`, `feedback`, `announcements`, `evaluations`), plus `photo_fingerprints`. |
| `next_id(kind)` | Returns the next number for `"act"`, `"att"`, `"rep"` or `"anc"` and remembers it in `counters`. |
| `save()` | Writes everything to `cwts_data.json` through a temp file so a crash cannot corrupt it. |
| `load()` | Creates `uploads/` and reads the JSON back into the dicts and lists. |

`db = Store()` at the bottom is the one shared database object every module imports.

### `helpers.py`
| Function | What it does |
|---|---|
| `hash_password(password)` | Salted PBKDF2-SHA256 hash, returned as `salt$hash`. |
| `check_password(stored, password)` | Re-hashes and compares. |
| `find(items, **match)` | First dict in a list whose fields match, e.g. `find(db.reports, id=5)`. This is a linear O(n) search. |
| `person_name(username)` | Display name for a username. |
| `activity_title(aid)` | Title for an activity id, or `Activity #id`. |
| `fmt(value)` | `2026-10-05T14:30:00` becomes `Oct 05, 2026 02:30 PM`. |
| `hours_text(h)` | Formats hours as `1.25`, or `-` if none. |
| `open_file(path)` | Opens a file with the computer's default program. |
| `all_students()` | All users whose role is `student`. |

### `app.py`: class `App`
| Function | What it does |
|---|---|
| `__init__` | Window size, theme, header and body frames, then shows `home`. |
| `color` (property) | Navy for admin screens, blue for everyone else. |
| `go(page, *args, admin=False)` | Switches page (see "How a click works"). |
| `dashboard()` | Sends the user to the student or staff dashboard. |
| `draw_header()` | Builds the top bar, role menu, bell with unread count, user name and logout. |
| `logout()` | Clears the session and returns home. |

### `widgets.py`: class `WidgetMixin`
| Function | What it does |
|---|---|
| `title_label(text)` | Big page title. |
| `card(parent, **pack)` | White bordered box that holds content. |
| `label(parent, text, bold, muted, size, ...)` | Text label. |
| `button(parent, text, command, color, **pack)` | Coloured button. `side="left"` puts buttons side by side. |
| `entry(parent, text, value, show, state)` | Label plus text field. `show="*"` hides passwords. |
| `textbox(parent, text, value, height)` | Label plus multi-line box. |
| `combo(parent, text, values, value)` | Label plus read-only drop-down. |
| `stats(items)` | Row of number boxes on dashboards. |
| `table(parent, columns, rows, on_open, empty, height)` | Table with optional double-click action. Returns `None` if there are no rows. |
| `pill(parent, status)` | Coloured status badge. |

### `pages_public.py`: class `PublicPagesMixin`
| Function | What it does |
|---|---|
| `home()` | Landing page with Log In, Register and Admin Portal buttons. |
| `login(admin)` | Login form. Inner `submit` checks the password and starts the session. |
| `make_account(role, name, email, section, username, password)` | Builds a user dict with a hashed password. |
| `register()` | Student/instructor sign-up (6+ character password). |
| `admin_register()` | Admin sign-up. Needs `ADMIN_CODE`, 8+ characters, max 3 admins. |

### `pages_student.py`: class `StudentPagesMixin`
| Function | What it does |
|---|---|
| `active_session(username)` | The student's open attendance record (timed in, not out), or `None`. |
| `activity_choices()` | Drop-down values like `1 - Clean-up`. |
| `report_rows(reports, with_student)` | Turns reports into table rows. |
| `student_dashboard()` | Stats, the Time In / Time Out card, and recent reports. |
| `time_in(choice)` | Starts an attendance record. |
| `time_out()` | Ends it, computes hours and adds them to `db.hours`. |
| `attendance_rows(records, with_student)` | Turns attendance into table rows. |
| `student_attendance()` | The student's attendance log. |
| `student_reports()` | The student's report list. |
| `report_form()` | Submit a report. Inner `choose` picks photos and `submit` validates, rejects duplicate photos (MD5), copies files and saves. |

### `pages_staff.py`: class `StaffPagesMixin`
| Function | What it does |
|---|---|
| `staff_dashboard()` | Counts and the list of pending reports. |
| `staff_reports()` | All reports. |
| `staff_attendance()` | All attendance logs. |
| `report_detail(rid)` | One report with details, photos, comments and Approve/Reject (staff only). |
| `review(rid, status, comment)` | Sets the status, saves the comment and notifies the student. |
| `staff_activities()` | Activity table with Add, Edit and QR buttons. |
| `show_qr(aid)` | Makes and shows a QR image (needs `qrcode`). |
| `activity_form(aid)` | Add or edit an activity. Inner `submit` validates dates and numbers. |
| `evaluations()` | Rate a student and see the history. |

### `pages_admin.py`: class `AdminPagesMixin`
| Function | What it does |
|---|---|
| `admin_students()` | Student table with Add and Edit buttons. |
| `student_form(username)` | Add or edit a student. |
| `admin_analytics()` | Total students, total hours, average hours. |

### `pages_common.py`: class `CommonPagesMixin`
| Function | What it does |
|---|---|
| `announcements()` | Post (staff only) and read announcements. |
| `feedback()` | Send feedback or a suggestion. Students see only their own. |
| `notifications()` | Lists notifications and marks them read. |

### `structures.py` and `algorithms.py` (your Activity 2 and 3 code, not wired in yet)
`RecordDictionary` (`add, get, update, remove, view_all, is_empty, size`), `RecordList` (`add, remove, get, view_all, is_empty, size`), `ServiceQueue` (`enqueue, dequeue, peek, is_empty, size, to_list`), `binary_search(arr, key, get_key)` and `selection_sort(arr, get_key, reverse)`.

---

## 4. Data model (what is stored in `cwts_data.json`)

| Collection | One record looks like |
|---|---|
| `users` / `admins` (dict, key = username) | `{username, name, email, section, role, password}` |
| `activities` (list) | `{id, title, goal, location, start, end, area_limit, max_participants, created_by}` |
| `attendance` (list) | `{id, student, activity_id, time_in, time_out, hours}` |
| `reports` (list) | `{id, student, activity_id, title, date, area, description, status, created, comments[]}` |
| `documents` (list) | `{report_id, kind, original, stored}` (photo files) |
| `hours` (dict) | `{username: total_hours}` |
| `inbox` (list) | `{to, message, read, at}` |
| `evaluations`, `feedback`, `announcements` (lists) | see `evaluations()`, `feedback()`, `announcements()` |

---

## 5. Work plan

Work in order. Each phase ends with a **Done when** check. Commit (or copy the folder) after each phase so you can go back.

### Phase 0: Setup (about 30 minutes)
- [ ] Install Python, VS Code and the extensions (section 1).
- [ ] Run the app (F5), register an admin using the code in `config.py`, then register a student and an instructor.
- [ ] Run `python -m unittest discover tests`.

**Done when:** you can log in as all three roles and the 6 tests pass.

### Phase 1: Read and trace (learning)
Do not change logic yet. Use breakpoints (F9) and `print()`.
1. Read `main.py`, then `app.py`: follow `__init__`, `go`, `draw_header`.
2. Trace **login**: breakpoint in `login > submit`, log in, step through with F10 and F11.
3. Trace **time in / time out**: `time_in`, `active_session`, `time_out`. Watch `db.hours` change.
4. Trace **a report's life**: `report_form > submit`, then `report_detail`, `review`, `notifications`.
5. Open `cwts_data.json` after each action and see what changed.
6. Warm-up edits: change a colour in `config.py`, a button label in `home()`, and the window size in `App.__init__`.

**Done when:** you can explain, in your own words, what `go()` does and how `db.save()` is used.

### Phase 2: Quick fixes (small, safe changes)
| # | Task | Where |
|---|---|---|
| 2.1 | "Recent Activity Reports" shows the oldest 5. Show the newest 5, newest first. | `student_dashboard` (`mine[:5]`) |
| 2.2 | Make `open_file` work with spaces and backslashes: use `pathlib.Path(path).as_uri()`. | `helpers.open_file` |
| 2.3 | Validate activities: end after start, area limit above 0, max participants at least 1. | `activity_form > submit` |
| 2.4 | Show newest first in the report and attendance tables, as the evaluation page already does. | `student_reports`, `staff_reports`, `staff_attendance` |
| 2.5 | Fix the docstring that says `cwts_app.py`. | `main.py` (done) |

**Done when:** each fix is tested by hand in the running app.

### Phase 3: Fix the serious issues
| # | Problem | Suggested fix | Where |
|---|---|---|---|
| 3.1 | Anyone can register as an instructor and approve reports. | New instructors start as `approved: False`. `login` blocks them. Add a "Pending instructors" list with an Approve button for admins. | `register`, `login`, `admin_students`, new method `approve_instructor` |
| 3.2 | Hours are wall-clock time with no limits. | In `time_in`, check the activity's start/end window and `max_participants`. In `time_out`, cap hours at the activity end time. | `time_in`, `time_out` |
| 3.3 | A rejected report permanently blocks its photos. | Save each fingerprint in `db.documents`. On Reject, remove them from `photo_fingerprints`. | `report_form > submit`, `review` |
| 3.4 | `db.hours` can drift from attendance. | Add `total_hours(username)` in `helpers.py` that sums `db.attendance`. Use it everywhere and drop `db.hours`. | `helpers`, `student_dashboard`, `admin_students`, `admin_analytics`, `time_out` |
| 3.5 | Weak spots in security. | Use `hmac.compare_digest` in `check_password`. Read `ADMIN_CODE` from an environment variable. | `helpers`, `config` |
| 3.6 | `activity_id` is a string in some records and an int in others. | Store ints. Convert old data in `Store.load`. | `time_in`, `report_form`, `Store.load` |
| 3.7 | A damaged JSON file crashes startup. | Catch the error, back up the bad file and start empty. | `Store.load` |

**Done when:** every row works and you tried to break it (spam time in, reject then resubmit, register as instructor and log in).

### Phase 4: Plug in Activities 2 and 3 (your data structures)
| # | Task | Details |
|---|---|---|
| 4.1 | **Dictionary for activities and reports** | In `Store`, make `activities` and `reports` `RecordDictionary` objects keyed by id. Update `save()` (write `list(d.values())`) and `load()` (add each record). `activity_title` then becomes `db.activities.get(aid)`, O(1) instead of the O(n) `find()`. |
| 4.2 | **Queue for pending reports** | Build a `ServiceQueue` of pending report ids when the app starts (do not save it, rebuild it from `reports`). `submit` calls `enqueue`. `review` calls `dequeue`. On `staff_dashboard`, add a **Review next** button that opens `queue.peek()`. |
| 4.3 | **Selection sort for tables** | Add a "Sort by" drop-down and an ascending/descending choice to `admin_students` (name, section, hours) and `staff_reports` (date, status). Call `selection_sort(rows, get_key, reverse)`. |
| 4.4 | **Binary search for Find student** | In `admin_students`, add a name box and a Find button. Sort the names with `selection_sort`, then call `binary_search`, then select the matching row in the table. Show a message when nothing is found. |
| 4.5 | **Document Big O** | Add a short table in this file: which feature uses which structure, and its Big O. |
| 4.6 | **Tests** | Add tests for the queue order of pending reports and for the sorted/search results on student data. |

**Done when:** the app has no remaining uses of `find()` on `db.activities` or `db.reports`, the dashboard shows the review queue, and tests pass.

### Phase 5: New features (pick what you like)
- Time in by typing the activity code `CWTS-ACTIVITY-<id>` (the QR already encodes it).
- A page where students see their evaluations (`my_evaluations`).
- CSV export of attendance (use Python's `csv` module) on `staff_attendance`.
- Delete or archive an activity; let a student fix and resubmit a rejected report.
- A search box inside `table()` that filters rows as you type.
- Change-password page; per-section filtering for instructors.

### Phase 6: Test and polish
- Unit tests for `helpers` (passwords, `fmt`) and for `Store` using a temporary data file.
- Manual checklist: register, login (wrong password), time in/out, submit report with a duplicate photo, approve, reject, notification count, admin student edit, analytics.
- Add docstrings to every function you changed. Keep your comments in whichever language you prefer.
- Final clean-up: run `python -m pyflakes *.py` and commit.

---

## 6. Working habits
1. **One change at a time**, then run the app.
2. **Use version control** (`git init`, one commit per task) or copy the folder before each phase.
3. **Delete `cwts_data.json`** whenever you want a clean database.
4. When something breaks, read the **last line** of the error first, then the file and line number above it.
5. Ask "which function owns this screen?" and jump to it with F12 or Ctrl+Shift+O.
