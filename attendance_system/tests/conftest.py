import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.attendance import Attendance
from models.classroom import Classroom
from models.user import User
from utils import auth, storage


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    storage.reset_registries()
    monkeypatch.setattr(storage, "DB_FILE", tmp_path / "records.json")
    yield
    storage.reset_registries()


@pytest.fixture
def school():
    from models.student import Student
    from models.teacher import Teacher

    teacher = Teacher("Alice", "Smith", "alice@example.com")
    student = Student("John", "Doe", "john@example.com")
    classroom = Classroom("C101", "Math", teacher)
    classroom.add_student(student)
    return teacher, student, classroom
