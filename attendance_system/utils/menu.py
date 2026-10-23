import argparse
import getpass

from rich.console import Console

from utils import auth, commands, storage

console = Console()

DATE_PROMPT = "Date YYYY-MM-DD (blank = today)"
SHARED = [("Show my profile", commands.cmd_whoami, [])]

MENUS = {
    None: [
        ("Log in", commands.cmd_login, [("email", "Email"), ("password", "Password")]),
        ("Register", commands.cmd_register, [
            ("first_name", "First name"), ("last_name", "Last name"),
            ("email", "Email"), ("role", "Role (student/teacher)"),
            ("password", "Password")]),
    ],
    "student": SHARED + [
        ("List classes", commands.cmd_list_classes, []),
        ("Enroll in a class", commands.cmd_enroll, [("class_id", "Class ID")]),
        ("Mark my attendance", commands.cmd_mark, [
            ("class_id", "Class ID"), ("date", DATE_PROMPT),
            ("status", "Status (Present/Absent/Late)")]),
        ("View my attendance", commands.cmd_view_attendance, []),
    ],
    "teacher": SHARED + [
        ("List my classes", commands.cmd_list_classes, []),
        ("View class students", commands.cmd_class_students, [("class_id", "Class ID")]),
        ("Mark student attendance", commands.cmd_mark, [
            ("class_id", "Class ID"), ("student", "Student email"),
            ("date", DATE_PROMPT), ("status", "Status (Present/Absent/Late)")]),
        ("View attendance", commands.cmd_view_attendance, [
            ("class_id", "Class ID (optional)"), ("date", "Date (optional)")]),
        ("Attendance report", commands.cmd_report, [("class_id", "Class ID (optional)")]),
    ],
    "admin": SHARED + [
        ("Add user", commands.cmd_add_user, [
            ("first_name", "First name"), ("last_name", "Last name"),
            ("email", "Email"), ("role", "Role (student/teacher/admin)"),
            ("password", "Password")]),
        ("List users", commands.cmd_list_users, []),
        ("Remove user", commands.cmd_remove_user, [("email", "Email")]),
        ("Create class", commands.cmd_add_class, [
            ("class_id", "Class ID"), ("class_name", "Class name"),
            ("teacher", "Teacher email")]),
        ("List classes", commands.cmd_list_classes, []),
        ("Enroll student", commands.cmd_enroll, [
            ("class_id", "Class ID"), ("student", "Student email")]),
        ("Mark student attendance", commands.cmd_mark, [
            ("class_id", "Class ID"), ("student", "Student email"),
            ("date", DATE_PROMPT), ("status", "Status (Present/Absent/Late)")]),
        ("View attendance", commands.cmd_view_attendance, []),
        ("Attendance report", commands.cmd_report, [("class_id", "Class ID (optional)")]),
    ],
}


def _ask(name, prompt):
    return getpass.getpass(f"{prompt}: ") if name == "password" else input(f"{prompt}: ")


def run_menu(args=None):
    while True:
        user = auth.current_user()
        options = MENUS[user.role if user else None]
        console.print(f"\n[bold]Attendance System[/bold] "
                      f"({user.get_full_name() + ', ' + user.role if user else 'not logged in'})")
        for number, (label, _, _) in enumerate(options, 1):
            console.print(f"  {number}. {label}")
        if user:
            console.print("  l. Log out")
        console.print("  0. Quit")
        choice = input("Choose: ").strip().lower()
        if choice == "0":
            return
        if choice == "l" and user:
            commands.cmd_logout(None)
            continue
        if not choice.isdigit() or not 1 <= int(choice) <= len(options):
            console.print("[red]Invalid choice.[/red]")
            continue
        _, handler, prompts = options[int(choice) - 1]
        try:
            answers = {name: _ask(name, prompt) for name, prompt in prompts}
            handler(argparse.Namespace(**answers))
            storage.save()
        except (ValueError, auth.AuthError, storage.StorageError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
