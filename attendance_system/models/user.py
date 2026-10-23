import re

from utils.security import hash_password, verify_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 6


def _clean_name(value, label):
    value = str(value).strip()
    if not value:
        raise ValueError(f"{label} cannot be empty.")
    return value


class User:
    ROLE = "user"
    PREFIX = "U"
    all_users = []

    def __init__(self, first_name, last_name, email, user_id=None, password_hash=""):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._password_hash = password_hash
        self.user_id = user_id or type(self).next_id()
        User.all_users.append(self)

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = _clean_name(value, "First name")

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = _clean_name(value, "Last name")

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        value = str(value).strip().lower()
        if not EMAIL_RE.match(value):
            raise ValueError(f"Invalid email address: '{value}'.")
        other = User.find_user(value)
        if other is not None and other is not self:
            raise ValueError(f"A user with email '{value}' already exists.")
        self._email = value

    @property
    def role(self):
        return self.ROLE

    @classmethod
    def next_id(cls):
        start = len(cls.PREFIX)
        numbers = [
            int(u.user_id[start:])
            for u in User.all_users
            if u.ROLE == cls.ROLE and u.user_id[start:].isdigit()
        ]
        return f"{cls.PREFIX}{max(numbers, default=0) + 1:03d}"

    @staticmethod
    def validate_password(password):
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
            )

    def set_password(self, password):
        self.validate_password(password)
        self._password_hash = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self._password_hash)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def view_profile(self):
        return {"Name": self.get_full_name(), "Email": self.email, "Role": self.role}

    def to_dict(self):
        return {
            "role": self.ROLE,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password_hash": self._password_hash,
        }

    @staticmethod
    def role_classes():
        from models.administrator import Administrator
        from models.student import Student
        from models.teacher import Teacher

        return {"student": Student, "teacher": Teacher, "admin": Administrator}

    @staticmethod
    def from_dict(data):
        klass = User.role_classes()[data["role"]]
        return klass(
            data["first_name"],
            data["last_name"],
            data["email"],
            data["user_id"],
            data["password_hash"],
        )

    @classmethod
    def register_user(cls, first_name, last_name, email, password, role):
        klass = cls.role_classes().get(role)
        if klass is None:
            raise ValueError(f"Unknown role '{role}'. Use student, teacher or admin.")
        cls.validate_password(password)
        user = klass(first_name, last_name, email)
        user.set_password(password)
        return user

    @classmethod
    def find_user(cls, email):
        email = str(email).strip().lower()
        return next((u for u in User.all_users if u._email == email), None)

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}> [{self.role}]"

    def __repr__(self):
        return f"{type(self).__name__}({self.user_id!r}, {self.email!r})"
