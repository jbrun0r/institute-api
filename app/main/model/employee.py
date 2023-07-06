from .. import db


class Employee(db.Model):
    __tablename__="employees"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    institute_id = db.Column(db.Integer, db.ForeignKey('institutes.id'), nullable=False)
    role = db.Column(db.String(80))

    user = db.relationship("User", back_populates="employee", uselist=False, lazy=True)
    institute = db.relationship("Institute", back_populates="employees", lazy=True, uselist=False)
