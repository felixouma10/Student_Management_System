# Attendance Management System

A command-line application for managing students, teachers, classes and attendance. It is object-oriented, stores its data in JSON, and has a hashed-password login with role-based access (admin, teacher, student).

**Problem it solves:** schools track attendance on paper or spreadsheets. This tool lets each role do only what it should: admins manage people and classes, teachers record and review attendance for their own classes, and students enrol and check in.

## Features

- Registration, login and logout with salted PBKDF2-SHA256 password hashing
- Role-based access: **admin**, **teacher**, **student**
- Classes with one teacher and many students; attendance per student, class and date (Present / Absent / Late)
- `argparse` subcommands **and** an interactive menu (`python3 main.py menu`)
- JSON persistence with handling for missing or corrupt files
- Input validation (emails, dates, statuses, password length, duplicates)
- Tables rendered with [`rich`](https://pypi.org/project/rich/)
- Decorators for logging, authentication, role checks and argument validation
- Unit tests with `pytest`

## Project structure

```
attendance_system/
├── main.py              # CLI entry point (argparse)
├── models/              # Class definitions
│   ├── user.py          # User base class (validation, password hashing)
│   ├── student.py       # Student(User)
│   ├── teacher.py       # Teacher(User)
│   ├── administrator.py # Administrator(User)
│   ├── classroom.py     # Classroom (Teacher 1-* Students)
│   └── attendance.py    # Attendance (Student + Classroom + date + status)
├── data/
│   └── records.json     # Persistent storage
├── utils/               # Helpers
│   ├── storage.py       # JSON load/save
│   ├── auth.py          # Register, login, logout, session
│   ├── decorators.py    # log_action, login_required, role_required, require_args
│   ├── security.py      # Password hashing
│   ├── commands.py      # CLI command handlers
│   └── menu.py          # Interactive menu
├── tests/               # pytest unit tests
├── requirements.txt     # Dependencies for pip/venv
├── Pipfile              # Pipenv configuration (Python 3.12)
├── Pipfile.lock         # Locked Pipenv dependencies
└── README.md
```

## Object model

```
User ── Student, Teacher, Administrator   (inheritance)
Teacher 1 ──* Classroom 1 ──* Student     (one-to-many)
Classroom 1 ──* Attendance *── 1 Student
```

- **Encapsulation:** names, email, date and status are `@property` fields with validators; the password hash is private and only reachable through `set_password` / `check_password`.
- **Class attributes:** `User.all_users`, `Classroom.all_classes` and `Attendance.all_records` are the in-memory registries; `User.next_id()` generates ids (`S001`, `T001`, `A001`).
- **`__str__` / `__repr__`** on users and classes for clean output.

## Setup

Use Python 3.12, as specified by the Pipenv configuration and lockfile. Run the commands below from the `attendance_system` directory (the directory containing `main.py`).

```bash
git clone <repo-url>
cd attendance_system
```

### Using `venv` and pip

Create a virtual environment, activate it, and install the project dependencies from `requirements.txt`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Then use `python` in place of `python3.12` for the remaining commands.

### Using Pipenv

Install Pipenv if needed, then use the checked-in lockfile to create the environment and install the locked dependencies:

```bash
python3.12 -m pip install --user pipenv
pipenv sync
```

## Running

With the virtual environment activated, run commands using `python main.py`. If using Pipenv without activating its environment, prefix commands with `pipenv run`, for example `pipenv run python main.py --help`.

Show all commands with `python main.py --help`; show options for a particular command with `python main.py <command> --help`.

The **first account registered becomes the administrator**. After that, `register` creates students or teachers, and only an admin can create other admins (`add-user`).

```bash
python main.py register Grace Lee admin@school.com --password secret1
python main.py login admin@school.com --password secret1
python main.py add-user Alice Smith alice@school.com teacher --password secret1
python main.py add-user John Doe john@school.com student --password secret1
python main.py add-class C101 Math alice@school.com
python main.py enroll C101 --student john@school.com

python main.py login john@school.com --password secret1
python main.py mark C101 present                 # date defaults to today

python main.py login alice@school.com --password secret1
python main.py mark C101 late --student john@school.com --date 2026-10-19
python main.py report --class-id C101
```

Omit `--password` to be prompted without echo. Login is stored in `data/session.json` until you run `logout`. The application creates its `data/` directory and files when needed.

### Commands

| Command | Who | Description |
|---------|-----|-------------|
| `register first last email [--password] [--role]` | anyone | Create an account |
| `login email [--password]` / `logout` / `whoami` | any | Session management |
| `add-user first last email role [--password]` | admin | Create a user of any role |
| `list-users` | admin | List users |
| `update-user email [--first-name] [--last-name] [--new-email]` | admin | Edit a user |
| `remove-user email` | admin | Remove a student or teacher (and their records) |
| `add-class id name teacher_email` | admin | Create a class |
| `list-classes` | any | List classes (teachers see their own) |
| `class-students id` | teacher, admin | List a class's students |
| `enroll id [--student email]` | student, admin | Enrol in a class (admins use `--student`) |
| `mark id status [--date] [--student]` | all | Students mark themselves; teachers (own classes) and admins mark a student |
| `view-attendance [--class-id] [--date] [--student]` | any | Records you may see |
| `report [--class-id] [--date] [--student]` | teacher, admin | Records plus per-student totals |
| `menu` | any | Interactive menu with options for your role |

## Data and persistence

All data is saved to `data/records.json` after every successful command, with users, classrooms and attendance linked by email and class id. A missing file starts empty; an unreadable or inconsistent file is renamed to `records.corrupt` and the app starts empty. Passwords are stored only as salted hashes. Logs go to `data/app.log` when run via `python main.py`. To start with a clean school dataset, back up and remove `data/records.json` and `data/session.json` while the application is not running.

## Tests

Run the full test suite from the `attendance_system` directory with the project environment activated:

```bash
python -m pytest
```

Alternatively, run the suite with Pipenv without activating its environment:

```bash
pipenv run python -m pytest
```

Pytest can also run a particular test file, select tests by name, or show each test as it runs:

```bash
python -m pytest tests/test_auth.py
python -m pytest -k login
python -m pytest -v
```

In VS Code, select the project environment as the Python interpreter, configure pytest as the test framework, then use the Testing panel to discover and run individual tests. The suite covers models, authentication, storage (including corrupt files), and CLI flows with role checks.

## Known issues

- One session at a time: the login is a single file, shared by every terminal on the machine.
- The data file is not locked, so two simultaneous commands could overwrite each other.
- There is no password reset or change, and no way to reassign a class to another teacher.
- Teachers with classes cannot be removed until their classes are handled, and there is no command to delete a class.
