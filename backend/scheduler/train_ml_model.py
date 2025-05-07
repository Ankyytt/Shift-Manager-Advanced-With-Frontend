import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend import create_app, db
from backend.models import ShiftPreferenceHistory
from backend.scheduler.ml_model import MLPreferenceModel

def train_ml_model():
    app = create_app()
    with app.app_context():
        connection = db.engine.connect()
        # Load historical data from database
        query = db.session.query(
            ShiftPreferenceHistory.emp_id,
            ShiftPreferenceHistory.date,
            ShiftPreferenceHistory.shift,
            ShiftPreferenceHistory.preferred,
            # Assuming seniority is available in Employee model or elsewhere; 
            # for now, set seniority to a default or fetch if possible
        )

        # Convert query result to DataFrame
        sql = query.statement.compile(compile_kwargs={"literal_binds": True})
        df = pd.read_sql(str(sql), connection)
        connection.close()

        # If seniority is not in ShiftPreferenceHistory, we need to join with Employee table
        # For now, add a default seniority column if missing
        if 'seniority' not in df.columns:
            df['seniority'] = 1  # default seniority, adjust as needed

        # Initialize and train the model
        ml_model = MLPreferenceModel()
        ml_model.train(df)

if __name__ == "__main__":
    train_ml_model()
