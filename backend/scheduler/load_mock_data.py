import os
import sys
import pandas as pd

# Setup Flask app context for database access
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend import create_app, db
app = create_app()
from backend.models import ShiftPreferenceHistory
from backend.scheduler.historical_data_mock import generate_mock_historical_data

def load_mock_data_to_db():
    with app.app_context():
        # Generate mock data
        df = generate_mock_historical_data()

        # Clear existing data
        ShiftPreferenceHistory.query.delete()
        db.session.commit()

        # Insert mock data into database
        for _, row in df.iterrows():
            record = ShiftPreferenceHistory(
                emp_id=row['emp_id'],
                date=row['date'],
                shift=row['shift'],
                preferred=bool(row['preferred'])
            )
            db.session.add(record)
        db.session.commit()
        print(f"Inserted {len(df)} records into ShiftPreferenceHistory table.")

if __name__ == "__main__":
    load_mock_data_to_db()
