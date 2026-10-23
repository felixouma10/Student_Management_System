import datetime
import getpass
from collections import Counter

from rich.console import Console
from rich.table import Table

from models.attendance import Attendance
from models.classroom import Classroom
from models.user import User
from utils import auth
from utils.decorators import log_action, login_required, require_args, role_required

console = Console()


def _opt(args, name):
    value = getattr(args, name, None)
    if isinstance(value, str):
        value = value.strip()
    return value or None


def _password(args):
    return _opt(args, "password") or getpass.getpass("Password: ")


def _get_user(email, role=None):
    user = User.find_user(email)
    if user is None or (role and user.role != role):
        raise ValueError(f"No {role or 'user'} found with email '{email}'.")
    return user


def _get_class(class_id, user=None):
    classroom = Classroom.find(class_id)
    if classroom is None:
        raise ValueError(f"No class found with ID '{class_id}'.")
    if user is not None and user.role == "teacher" and classroom.teacher is not user:
        raise ValueError("You do not teach that class.")
    return classroom


def _print_table(title, columns, rows):
    if not rows:
        console.print(f"[yellow]No {title.lower()} found.[/yellow]")
        return
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)


def _visible_records(user, args):
    records = Attendance.all_records
    if user.role == "student":
        records = [r for r in records if r.student is user]
    elif user.role == "teacher":
        records = [r for r in records if r.classroom.teacher is user]
    if _opt(args, "class_id"):
        classroom = _get_class(args.class_id, user)
        records = [r for r in records if r.classroom is classroom]
    if _opt(args, "student") and user.role != "student":
        target = _get_user(args.student, "student")
        records = [r for r in records if r.student is target]
    if _opt(args, "date"):
        records = [r for r in records if r.date == args.date.strip()]
    return records


def _record_rows(records):
    return [r.get_attendance_details().values() for r in records]


RECORD_COLUMNS = ["Student", "Class", "Date", "Status"]


@log_action
@require_args("first_name", "last_name", "email")
def cmd_register(args):
    user = auth.register(
        args.first_name, args.last_name, args.email, _password(args),
        _opt(args, "role") or "student",
    )
    console.print(f"[green]Registered:[/green] {user}")


@log_action
@require_args("email")
def cmd_login(args):
    user = auth.login(args.email, _password(args))
    console.print(f"[green]Welcome, {user.get_full_name()} ({user.role}).[/green]")


@log_action
def cmd_logout(args):
    auth.logout()
    console.print("Logged out.")


@log_action
@login_required
def cmd_whoami(args, user):
    _print_table("Profile", ["Field", "Value"], user.view_profile().items())


@log_action
@login_required
@role_required("admin")
@require_args("first_name", "last_name", "email", "role")
def cmd_add_user(args, user):
    new = User.register_user(
        args.first_name, args.last_name, args.email, _password(args), args.role
    )
    console.print(f"[green]Added:[/green] {new}")


@log_action
@login_required
@role_required("admin")
def cmd_list_users(args, user):
    rows = [(u.user_id, u.get_full_name(), u.email, u.role) for u in User.all_users]
    _print_table("Users", ["ID", "Name", "Email", "Role"], rows)


@log_action
@login_required
@role_required("admin")
@require_args("email")
def cmd_update_user(args, user):
    changes = {
        key: _opt(args, key) for key in ("first_name", "last_name", "new_email")
        if _opt(args, key)
    }
    if not changes:
        raise ValueError("Give at least one of --first-name, --last-name, --new-email.")
    if "new_email" in changes:
        changes["email"] = changes.pop("new_email")
    target = _get_user(args.email)
    user.update_user(target, **changes)
    console.print(f"[green]Updated:[/green] {target}")


@log_action
@login_required
@role_required("admin")
@require_args("email")
def cmd_remove_user(args, user):
    target = _get_user(args.email)
    if target is user:
        raise ValueError("You cannot remove your own account.")
    user.remove_user(target)
    console.print(f"[green]Removed:[/green] {target}")


@log_action
@login_required
@role_required("admin")
@require_args("class_id", "class_name", "teacher")
def cmd_add_class(args, user):
    classroom = user.create_class(
        args.class_id, args.class_name, _get_user(args.teacher, "teacher")
    )
    console.print(f"[green]Created class:[/green] {classroom}")


@log_action
@login_required
def cmd_list_classes(args, user):
    classes = Classroom.all_classes
    if user.role == "teacher":
        classes = user.assigned_classes
    rows = [
        (c.class_id, c.class_name, c.teacher.get_full_name(), len(c.students))
        for c in classes
    ]
    _print_table("Classes", ["ID", "Name", "Teacher", "Students"], rows)


@log_action
@login_required
@role_required("teacher", "admin")
@require_args("class_id")
def cmd_class_students(args, user):
    classroom = _get_class(args.class_id, user)
    names = user.view_students(classroom) if user.role == "teacher" \
        else classroom.get_student_list()
    _print_table("Students", ["Name"], [(n,) for n in names])


@log_action
@login_required
@role_required("student", "admin")
@require_args("class_id")
def cmd_enroll(args, user):
    if user.role == "student":
        target = user
    else:
        if not _opt(args, "student"):
            raise ValueError("'student' is required.")
        target = _get_user(args.student, "student")
    classroom = _get_class(args.class_id)
    target.register_for_class(classroom)
    console.print(f"[green]{target.get_full_name()} enrolled in {classroom}.[/green]")


@log_action
@login_required
@require_args("class_id", "status")
def cmd_mark(args, user):
    classroom = _get_class(args.class_id, user)
    day = _opt(args, "date") or datetime.date.today().isoformat()
    if user.role == "student":
        record = user.mark_attendance(classroom, day, args.status)
    else:
        if not _opt(args, "student"):
            raise ValueError("'student' is required.")
        target = _get_user(args.student, "student")
        if user.role == "teacher":
            record = user.mark_attendance(target, classroom, day, args.status)
        else:
            record = Attendance.mark(target, classroom, day, args.status)
    console.print(f"[green]Recorded:[/green] {dict(record.get_attendance_details())}")


@log_action
@login_required
def cmd_view_attendance(args, user):
    _print_table("Attendance records", RECORD_COLUMNS,
                 _record_rows(_visible_records(user, args)))


@log_action
@login_required
@role_required("teacher", "admin")
def cmd_report(args, user):
    records = _visible_records(user, args)
    _print_table("Attendance report", RECORD_COLUMNS, _record_rows(records))
    totals = {}
    for record in records:
        totals.setdefault(record.student.get_full_name(), Counter())[record.status] += 1
    rows = [(name, c["Present"], c["Late"], c["Absent"]) for name, c in totals.items()]
    if rows:
        _print_table("Summary", ["Student", "Present", "Late", "Absent"], rows)
