# Shift-Manager-Advanced-With-Frontend
An advanced version for Shift Management System for Roster Building

File to large

Mail the owner at ankitdas2003@gmail.com to get the zip file and more info

To Run
1. Open a Terminal, Go to Frontend Folder (cd frontend), Write- npm start
2. Open another Terminal in main file and Write- python run.py


# Shift Manager

Shift Manager is a web application designed to help manage employee shifts efficiently. It provides backend APIs for managing shifts, employees, and generating monthly schedules based on employee preferences. The frontend is a React application that interacts with the backend to provide a user-friendly interface.

## Features

- Manage shifts: add, update, delete, and view shifts.
- Manage employees: upload employee data via Excel and view employee details.
- Generate monthly shift schedules automatically considering employee preferences and holidays.
- Backend built with Flask and SQLite.
- Frontend built with React.

## Backend

### Tech Stack and Dependencies

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- pandas
- openpyxl
- SQLite (for database)

### Setup and Run

1. Create a virtual environment and activate it (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:

   ```bash
   python run.py
   ```

   The backend server will start on `http://127.0.0.1:5000`.

### API Endpoints Overview

- `POST /api/shifts` - Add a new shift.
- `GET /api/shifts` - Get all shifts.
- `PUT /api/shifts/<id>` - Update a shift by ID.
- `DELETE /api/shifts/<id>` - Delete a shift by ID.
- `POST /api/upload_excel` - Upload an Excel file to bulk add employees. The Excel file must have columns: `Employee Name`, `Seniority`, `Employee ID`.
- `GET /api/employees` - Get all employees.
- `POST /api/generate_schedule` - Generate a monthly schedule. Requires JSON body with `year`, `month`, and `gazettedHolidays` (number of holidays).

## Frontend

### Tech Stack

- React (bootstrapped with Create React App)
- JavaScript, HTML, CSS

### Setup and Run

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`.

## Usage

- Use the frontend interface to manage employees and shifts.
- Upload employee data via Excel file.
- Generate monthly schedules based on employee preferences and holidays.
- The backend APIs can also be accessed directly for integration or testing.

## License

This project is open source and available under the MIT License.

