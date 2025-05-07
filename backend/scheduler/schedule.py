import pandas as pd
import calendar
from datetime import datetime
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value
from backend.scheduler.employee import Employee
from backend.scheduler.shift_preference import ShiftPreference

from backend.scheduler.ml_model import MLPreferenceModel

class Schedule:
    def __init__(self):
        self.employees = []
        self.schedules = {}
        self.shift_preferences = []
        self.ml_model = MLPreferenceModel()
        self.ml_model.load_model()

    def load_employees_from_json(self, file_path):
        import json
        with open(file_path, 'r') as file:
            employee_data = json.load(file)
            self.employees = [Employee(emp['name'], emp['seniority'], emp['id']) for emp in employee_data]

    def collect_shift_preferences(self, year, month, preferences):
        self.shift_preferences = preferences

    def generate_schedule(self, year, month, gazetted_holidays):
        shifts = ['M', 'E', 'N', 'Off', 'TR']
        days_in_month = calendar.monthrange(year, month)[1]

        weekends = sum(1 for d in range(1, days_in_month + 1) if calendar.weekday(year, month, d) >= 5)
        total_holidays = weekends + gazetted_holidays

        self.schedules[(year, month)] = pd.DataFrame(index=[e.name for e in self.employees],
                                                     columns=range(1, days_in_month + 1))

        prob = LpProblem("ShiftScheduling", LpMinimize)

        shifts_vars = LpVariable.dicts("Shift",
            ((e.name, d, s) for e in self.employees for d in range(1, days_in_month + 1) for s in shifts),
            cat='Binary')

        # Get ML-based preference penalties
        preference_scores = self.ml_model.predict_preferences(self.employees, year, month, days_in_month, shifts)

        # Objective function: minimize total penalty based on ML predictions
        prob += lpSum(
            preference_scores.get((e.id, f"{year:04d}-{month:02d}-{d:02d}", s), 1) * shifts_vars[e.name, d, s]
            for e in self.employees for d in range(1, days_in_month + 1) for s in shifts
        )

        for d in range(1, days_in_month + 1):
            prob += lpSum(shifts_vars[e.name, d, 'M'] for e in self.employees) >= 1
            prob += lpSum(shifts_vars[e.name, d, 'E'] for e in self.employees) >= 1
            prob += lpSum(shifts_vars[e.name, d, 'N'] for e in self.employees) == 2

            for e in self.employees:
                prob += lpSum(shifts_vars[e.name, d, s] for s in shifts) == 1

                if d > 1:
                    for s in ['M', 'E']:
                        prob += lpSum([shifts_vars[e.name, d, s], shifts_vars[e.name, d-1, 'N']]) <= 1
                    prob += lpSum([shifts_vars[e.name, d, 'M'], shifts_vars[e.name, d-1, 'E']]) <= 1
                    prob += lpSum([shifts_vars[e.name, d, 'TR'], shifts_vars[e.name, d-1, 'E']]) <= 1

                if d > 2:
                    for s in ['M', 'E', 'N', 'TR']:
                        prob += lpSum([shifts_vars[e.name, d, s], shifts_vars[e.name, d-1, 'N'], shifts_vars[e.name, d-2, 'N']]) <= 2
                        prob += lpSum([shifts_vars[e.name, d, s], shifts_vars[e.name, d-1, 'TR'], shifts_vars[e.name, d-2, 'N']]) <= 2

                if d > 3:
                    for s in ['M', 'E', 'N', 'TR']:
                        prob += lpSum([shifts_vars[e.name, d, s], shifts_vars[e.name, d-2, 'N'], shifts_vars[e.name, d-3, 'N']]) <= 2
                        prob += lpSum([shifts_vars[e.name, d, s], shifts_vars[e.name, d-2, 'TR'], shifts_vars[e.name, d-3, 'N']]) <= 2

                if d > 6:
                    prob += lpSum([shifts_vars[e.name, d - i, 'Off'] for i in range(7)]) >= 1

        avg_night_shifts = 2 * days_in_month / len(self.employees)
        avg_total_shifts = days_in_month - total_holidays

        for e in self.employees:
            prob += lpSum(shifts_vars[e.name, d, 'N'] for d in range(1, days_in_month + 1)) >= avg_night_shifts - 1
            prob += lpSum(shifts_vars[e.name, d, 'N'] for d in range(1, days_in_month + 1)) <= avg_night_shifts + 1

            prob += lpSum(shifts_vars[e.name, d, s] for d in range(1, days_in_month + 1) for s in shifts if s != 'Off') >= avg_total_shifts - 1
            prob += lpSum(shifts_vars[e.name, d, s] for d in range(1, days_in_month + 1) for s in shifts if s != 'Off') <= avg_total_shifts + 1

            prob += lpSum(shifts_vars[e.name, d, 'Off'] for d in range(1, days_in_month + 1)) >= total_holidays - 1
            prob += lpSum(shifts_vars[e.name, d, 'Off'] for d in range(1, days_in_month + 1)) <= total_holidays + 1

        prob.solve()

        if LpStatus[prob.status] == 'Infeasible':
            raise Exception("Unable to find feasible schedule")

        for d in range(1, days_in_month + 1):
            for e in self.employees:
                for s in shifts:
                    if value(shifts_vars[e.name, d, s]) == 1:
                        self.schedules[(year, month)].at[e.name, d] = s
                        e.add_shift(datetime(year, month, d), s)

    def get_preference_penalty(self, emp_id, date, shift):
        for preference in self.shift_preferences:
            if preference.emp_id == emp_id:
                if date.strftime('%Y-%m-%d') in preference.preferences:
                    if preference.preferences[date.strftime('%Y-%m-%d')] == shift:
                        return 0
                    else:
                        return 1
        return 1
