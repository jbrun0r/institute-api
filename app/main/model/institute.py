from .. import db
from ..model.user import Profile

class Institute(db.Model):
    __tablename__ = "institutes"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True,
                   nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    trading_name = db.Column(db.String(80), nullable=False)
    corporate_name = db.Column(db.String(80), nullable=False)

    address = db.relationship("Address", back_populates="institute", cascade="all,delete", uselist=False)
    employees = db.relationship("Employee", back_populates="institute", cascade="all,delete")
    students = db.relationship("Student", back_populates="institute", cascade="all,delete")


    @property
    def get_admin_employee(self):
        return next(filter(lambda usr: usr.user.profile.value in (Profile.INSTITUTE.value, Profile.OWNER.value), self.employees))
