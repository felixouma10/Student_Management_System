
class Classroom:
    all_classes = []

    def __init__(self, class_id, class_name, teacher):
        class_id = str(class_id).strip()
        class_name = str(class_name).strip()
        if not class_id or not class_name:
            raise ValueError("Class ID and name cannot be empty.")
        if Classroom.find(class_id):
            raise ValueError(f"Class '{class_id}' already exists.")
        if getattr(teacher, "role", None) != "teacher":
            raise ValueError("A classroom must be assigned to a teacher.")
        self.class_id = class_id
        self.class_name = class_name
        self.teacher = teacher
        self.students = []
        teacher.assigned_classes.append(self)
        Classroom.all_classes.append(self)

    @classmethod
    def find(cls, class_id):
        class_id = str(class_id).strip()
        return next((c for c in cls.all_classes if c.class_id == class_id), None)

    def add_student(self, student):
        if getattr(student, "role", None) != "student":
            raise ValueError("Only students can be enrolled in a class.")
        if student not in self.students:
            self.students.append(student)
        if self not in student.enrolled_classes:
            student.enrolled_classes.append(self)

    def remove_student(self, student):
        if student in self.students:
            self.students.remove(student)
        if self in student.enrolled_classes:
            student.enrolled_classes.remove(self)

    def get_student_list(self):
        return [s.get_full_name() for s in self.students]

    def to_dict(self):
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "teacher": self.teacher.email,
            "students": [s.email for s in self.students],
        }

    def __str__(self):
        return f"{self.class_id} - {self.class_name} ({self.teacher.get_full_name()})"

    def __repr__(self):
        return f"Classroom({self.class_id!r}, {self.class_name!r})"
