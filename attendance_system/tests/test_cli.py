import pytest

import main


def run(*argv):
    return main.main(list(argv))


def login(email, password="secret1"):
    assert run("login", email, "--password", password) == 0


@pytest.fixture
def populated():
    assert run("register", "Grace", "Lee", "admin@x.com", "--password", "secret1") == 0
    login("admin@x.com")
    assert run("add-user", "Alice", "Smith", "teacher@x.com", "teacher", "--password", "secret1") == 0
    assert run("add-user", "John", "Doe", "student@x.com", "student", "--password", "secret1") == 0
    assert run("add-class", "C101", "Math", "teacher@x.com") == 0
    assert run("enroll", "C101", "--student", "student@x.com") == 0


def test_commands_require_login(capsys):
    assert run("list-users") == 1
    assert "log in" in capsys.readouterr().out.lower()


def test_wrong_password_fails():
    run("register", "Grace", "Lee", "admin@x.com", "--password", "secret1")
    assert run("login", "admin@x.com", "--password", "nope") == 1


def test_role_based_access(populated):
    login("student@x.com")
    assert run("list-users") == 1
    assert run("add-class", "C2", "Art", "teacher@x.com") == 1
    login("teacher@x.com")
    assert run("remove-user", "student@x.com") == 1


def test_full_attendance_flow_persists(populated, capsys):
    login("student@x.com")
    assert run("mark", "C101", "present", "--date", "2026-10-18") == 0
    login("teacher@x.com")
    assert run("mark", "C101", "late", "--student", "student@x.com", "--date", "2026-10-19") == 0
    capsys.readouterr()
    assert run("report", "--class-id", "C101") == 0
    out = capsys.readouterr().out
    assert "John Doe" in out and "Late" in out and "Present" in out
    login("student@x.com")
    capsys.readouterr()
    assert run("view-attendance") == 0
    assert "2026-10-19" in capsys.readouterr().out


def test_invalid_input_is_reported(populated):
    login("student@x.com")
    assert run("mark", "C101", "sleeping") == 1
    assert run("mark", "C101", "present", "--date", "yesterday") == 1
    assert run("mark", "NOPE", "present") == 1


def test_no_command_prints_help(capsys):
    assert run() == 0
    assert "usage" in capsys.readouterr().out.lower()
