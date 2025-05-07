from flask import Blueprint, request, jsonify
from backend.models import db, Shift , Employee

shift_bp = Blueprint('shift_bp', __name__)

# POST API
@shift_bp.route('/api/shifts', methods=['POST'])
def add_shift():
    data = request.get_json()
    try:
        new_shift = Shift(
            employee_name=data['employeeName'],
            date=data['date'],
            shift_type=data['shiftType']
        )
        db.session.add(new_shift)
        db.session.commit()
        return jsonify({"message": "Shift added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 🚀 GET API 
@shift_bp.route('/api/shifts', methods=['GET'])
def get_shifts():
    shifts = Shift.query.all()
    output = []
    for shift in shifts:
        output.append({
            'id': shift.id,
            'employeeName': shift.employee_name,
            'date': shift.date,
            'shiftType': shift.shift_type
        })
    return jsonify(output)


@shift_bp.route('/api/shifts/<int:id>', methods=['DELETE'])
def delete_shift(id):
    shift = Shift.query.get_or_404(id)

    try:
        db.session.delete(shift)
        db.session.commit()
        return jsonify({"message": "Shift deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@shift_bp.route('/api/shifts/<int:id>', methods=['PUT'])
def update_shift(id):
    shift = Shift.query.get_or_404(id)
    data = request.get_json()

    try:
        shift.employee_name = data['employeeName']
        shift.date = data['date']
        shift.shift_type = data['shiftType']

        db.session.commit()
        return jsonify({"message": "Shift updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@shift_bp.route('/api/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        print("❌ No file in request")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        print("❌ Empty filename received")
        return jsonify({"error": "Empty filename"}), 400

    try:
        import pandas as pd
        from backend.models import Employee

        print("✅ Reading Excel file now...")
        df = pd.read_excel(file)
        
        # 👉 ADD THIS:
        print("✅ Columns Found:", df.columns.tolist())

        print(f"✅ Excel read successfully! Shape: {df.shape}")

        required_columns = {'Employee Name', 'Seniority', 'Employee ID'}
        if not required_columns.issubset(df.columns):
            print("❌ Required columns missing in Excel!")
            return jsonify({"error": "Incorrect Excel format!"}), 400

        print("✅ Clearing old Employee data...")
        Employee.query.delete()
        db.session.commit()

        print("✅ Inserting new employees into database...")
        for index, row in df.iterrows():
            new_employee = Employee(
                name=row['Employee Name'],
                seniority=row['Seniority'],
                emp_id=row['Employee ID']
            )
            db.session.add(new_employee)

        db.session.commit()
        print("✅ All employees inserted successfully!")

        return jsonify({"message": "Excel processed and employees saved successfully!"})
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 400



@shift_bp.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    output = []
    for emp in employees:
        output.append({
            'id': emp.id,
            'name': emp.name,
            'seniority': emp.seniority,
            'emp_id': emp.emp_id
        })
    return jsonify(output)

