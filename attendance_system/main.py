import argparse
import logging
import sys

from rich.console import Console

from utils import auth, commands, storage
from utils.menu import run_menu

console = Console()


def build_parser():
    parser = argparse.ArgumentParser(
        prog="main.py", description="Attendance Management System CLI"
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    def add(name, func, help_text, *arguments, **options):
        p = sub.add_parser(name, help=help_text, description=help_text)
        for arg in arguments:
            p.add_argument(arg)
        for flag, flag_help in options.items():
            p.add_argument(f"--{flag.replace('_', '-')}", dest=flag, help=flag_help)
        p.set_defaults(func=func)
        return p

    pw = "password (prompted if omitted)"
    add("register", commands.cmd_register, "Create an account (first user becomes admin)",
        "first_name", "last_name", "email", password=pw,
        role="student or teacher (default: student)")
    add("login", commands.cmd_login, "Log in", "email", password=pw)
    add("logout", commands.cmd_logout, "Log out")
    add("whoami", commands.cmd_whoami, "Show the logged-in user")
    add("add-user", commands.cmd_add_user, "Admin: add a user",
        "first_name", "last_name", "email", "role", password=pw)
    add("list-users", commands.cmd_list_users, "Admin: list users")
    add("update-user", commands.cmd_update_user, "Admin: update a user", "email",
        first_name="new first name", last_name="new last name", new_email="new email")
    add("remove-user", commands.cmd_remove_user, "Admin: remove a student or teacher", "email")
    add("add-class", commands.cmd_add_class, "Admin: create a class",
        "class_id", "class_name", "teacher")
    add("list-classes", commands.cmd_list_classes, "List classes")
    add("class-students", commands.cmd_class_students,
        "Teacher/Admin: list students in a class", "class_id")
    add("enroll", commands.cmd_enroll, "Enroll in a class (admin: use --student)",
        "class_id", student="student email (admin only)")
    add("mark", commands.cmd_mark, "Mark attendance (Present/Absent/Late)",
        "class_id", "status", date="YYYY-MM-DD (default: today)",
        student="student email (teacher/admin)")
    add("view-attendance", commands.cmd_view_attendance, "View attendance records",
        class_id="filter by class", date="filter by YYYY-MM-DD",
        student="filter by student email")
    add("report", commands.cmd_report, "Teacher/Admin: attendance report",
        class_id="filter by class", date="filter by YYYY-MM-DD",
        student="filter by student email")
    add("menu", run_menu, "Start the interactive menu")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        storage.load()
        args.func(args)
        storage.save()
        return 0
    except (ValueError, auth.AuthError, storage.StorageError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    logging.basicConfig(
        filename=storage.DB_FILE.parent / "app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    sys.exit(main())
