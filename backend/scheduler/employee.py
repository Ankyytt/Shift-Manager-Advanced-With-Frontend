class Employee:
    def __init__(self, name, seniority, emp_id):
        self.name = name
        self.seniority = seniority
        self.id = emp_id
        self.schedule = []
        self.training_days = []

    def add_shift(self, date, shift):
        self.schedule.append((date, shift))

    def get_shifts(self):
        return self.schedule

    def add_training_day(self, date):
        self.training_days.append(date)
