from .. import db

import enum


class Gender(enum.Enum):
    CIS_MALE = "CIS_MALE"
    CIS_FEMALE = "CIS_FEMALE"
    TRANS_MALE = "TRANS_MALE"
    TRANS_FEMALE = "TRANS_FEMALE"
    NON_BINARY = "NON_BINARY"
    UNSPOKEN = "UNSPOKEN"

    def __str__(self) -> str:
        return self.value


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    birthday_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    disabled_person = db.Column(db.Boolean, nullable=False, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    institute_id = db.Column(db.Integer, db.ForeignKey("institutes.id"), nullable=False)

    user = db.relationship("User", back_populates="student", cascade="all,delete", uselist=False)
    address = db.relationship("Address", back_populates="student", cascade="all,delete,delete-orphan", uselist=False)
    document = db.relationship("Document", back_populates="student", cascade="all,delete,delete-orphan", uselist=False)
    institute = db.relationship("Institute", back_populates="students")