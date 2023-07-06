from .. import db


class Error(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    api_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)
