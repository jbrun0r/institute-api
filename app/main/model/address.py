from .. import db


class Address(db.Model):
    __tablename__ = "address"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(80))
    state = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    neighborhood = db.Column(db.String(80))
    street = db.Column(db.String(80))
    number = db.Column(db.String(255))
    complement = db.Column(db.String(255))

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    institute_id = db.Column(db.Integer, db.ForeignKey("institutes.id"))

    student = db.relationship("Student", back_populates="address")
    institute = db.relationship("Institute", back_populates="address")
