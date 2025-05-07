from flask import Blueprint, request, jsonify
from backend.models import db, Employee
from backend.scheduler.schedule import Schedule
from backend.scheduler.employee import Employee as SchedulerEmployee  # 🆕 ADD THIS!
from datetime import datetime
import calendar
import pandas as pd

schedule_bp = Blueprint('schedule_bp', __name__)

@schedule_bp.route('/api/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        data = request.get_json()
        year = int(data.get('year'))
        month = int(data.get('month'))
        gazetted_holidays = int(data.get('gazettedHolidays'))

        if not (1 <= month <= 12):
            return jsonify({"error": "Invalid month"}), 400

        employees = Employee.query.all()
        if not employees:
            return jsonify({"error": "No employees found in database"}), 400

        schedule = Schedule()

        for emp in employees:
            schedule.employees.append(SchedulerEmployee(emp.name, emp.seniority, emp.emp_id))  # 🆕

        schedule.collect_shift_preferences(year, month, [])
        schedule.generate_schedule(year, month, gazetted_holidays)

        final_schedule = []
        days_in_month = calendar.monthrange(year, month)[1]

        for emp in schedule.employees:
            emp_schedule = {"employeeName": emp.name}
            for day in range(1, days_in_month + 1):
                shift = schedule.schedules[(year, month)].at[emp.name, day]
                emp_schedule[str(day)] = shift if pd.notnull(shift) else 'Off'
            final_schedule.append(emp_schedule)

        return jsonify(final_schedule), 200

    except Exception as e:
        import traceback
        print("❌ ERROR in generate_schedule:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
