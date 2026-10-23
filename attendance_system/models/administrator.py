from models.attendance import Attendance
from models.classroom import Classroom
from models.user import User

EDITABLE_FIELDS = {"first_name", "last_name", "email"}


class Administrator(User):
    ROLE = "admin"
    PREFIX = "A"

    @property
    def admin_id(self):
        return self.user_id

    def add_user(self, user):
        if user not in User.all_users:
            User.all_users.append(user)

    def update_user(self, user, **fields):
        unknown = set(fields) - EDITABLE_FIELDS
        if unknown:
            raise ValueError(f"Cannot update: {', '.join(sorted(unknown))}.")
        for key, value in fields.items():
            setattr(user, key, value)

    def remove_user(self, user):
        if user.role == "admin":
            raise ValueError("Administrator accounts cannot be removed.")
        if user.role == "teacher" and user.assigned_classes:
            raise ValueError("Reassign or remove this teacher's classes first.")
        if user.role == "student":
            for classroom in user.enrolled_classes:
                classroom.remove_student(user)
            Attendance.remove_for_student(user)
        User.all_users.remove(user)

    def create_class(self, class_id, class_name, teacher):
        return Classroom(class_id, class_name, teacher)

    def view_all_attendance(self):
        return list(Attendance.all_records)

    def generate_report(self):
        return [r.get_attendance_details() for r in Attendance.all_records]
