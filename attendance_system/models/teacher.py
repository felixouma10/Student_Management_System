from models.attendance import Attendance
from models.user import User


class Teacher(User):
    ROLE = "teacher"
    PREFIX = "T"

    def __init__(self, first_name, last_name, email, teacher_id=None, password_hash=""):
        self.assigned_classes = []
        super().__init__(first_name, last_name, email, teacher_id, password_hash)

    @property
    def teacher_id(self):
        return self.user_id

    def view_students(self, classroom):
        return classroom.get_student_list()

    def view_daily_attendance(self, classroom, date):
        return [
            r for r in Attendance.all_records
            if r.classroom is classroom and r.date == date
        ]

    def view_student_history(self, student):
        return Attendance.get_student_records(student)

    def mark_attendance(self, student, classroom, date, status):
        if classroom.teacher is not self:
            raise ValueError("You can only mark attendance for your own classes.")
        return Attendance.mark(student, classroom, date, status)

    def generate_attendance_report(self, classroom):
        return [
            r.get_attendance_details()
            for r in Attendance.all_records if r.classroom is classroom
        ]
