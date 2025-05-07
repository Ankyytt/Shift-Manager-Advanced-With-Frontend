from backend import db

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    shift_type = db.Column(db.String(10), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    seniority = db.Column(db.String(100), nullable=False)
    emp_id = db.Column(db.String(100), nullable=False)

class ShiftPreferenceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    shift = db.Column(db.String(10), nullable=False)
    preferred = db.Column(db.Boolean, nullable=False)
