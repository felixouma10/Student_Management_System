from datetime import datetime

STATUSES = ("Present", "Absent", "Late")


class Attendance:
    all_records = []

    def __init__(self, student, classroom, date, status):
        self.date = date
        self.status = status
        if Attendance.find_record(student, classroom, self.date):
            raise ValueError("An attendance record already exists for that day.")
        self.student = student
        self.classroom = classroom
        Attendance.all_records.append(self)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        try:
            datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date '{value}'. Use YYYY-MM-DD.") from None
        self._date = str(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        normalised = str(value).strip().capitalize()
        if normalised not in STATUSES:
            raise ValueError(f"Invalid status '{value}'. Use {', '.join(STATUSES)}.")
        self._status = normalised

    def mark_present(self):
        self.status = "Present"

    def mark_absent(self):
        self.status = "Absent"

    def update_status(self, status):
        self.status = status

    def get_attendance_details(self):
        return {
            "Student": self.student.get_full_name(),
            "Class": self.classroom.class_name,
            "Date": self.date,
            "Status": self.status,
        }

    def to_dict(self):
        return {
            "student": self.student.email,
            "class_id": self.classroom.class_id,
            "date": self.date,
            "status": self.status,
        }

    @classmethod
    def mark(cls, student, classroom, date, status):
        if student not in classroom.students:
            raise ValueError(
                f"{student.get_full_name()} is not enrolled in {classroom.class_id}."
            )
        record = cls.find_record(student, classroom, date)
        if record is None:
            return cls(student, classroom, date, status)
        record.update_status(status)
        return record

    @classmethod
    def find_record(cls, student, classroom, date):
        return next(
            (r for r in cls.all_records
             if r.student is student and r.classroom is classroom and r.date == str(date)),
            None,
        )

    @classmethod
    def get_student_records(cls, student):
        return [r.get_attendance_details() for r in cls.all_records if r.student is student]

    @classmethod
    def remove_for_student(cls, student):
        cls.all_records[:] = [r for r in cls.all_records if r.student is not student]
