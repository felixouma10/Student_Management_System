from models.attendance import Attendance
from models.user import User


class Student(User):
    ROLE = "student"
    PREFIX = "S"

    def __init__(self, first_name, last_name, email, student_id=None, password_hash=""):
        self.enrolled_classes = []
        super().__init__(first_name, last_name, email, student_id, password_hash)

    @property
    def student_id(self):
        return self.user_id

    def register_for_class(self, classroom):
        classroom.add_student(self)

    def mark_attendance(self, classroom, date, status):
        return Attendance.mark(self, classroom, date, status)

    def view_attendance_history(self):
        return Attendance.get_student_records(self)
