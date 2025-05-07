import pandas as pd
import random
from datetime import datetime, timedelta

def generate_mock_historical_data(num_employees=10, start_date='2023-01-01', end_date='2023-03-31'):
    """
    Generate mock historical shift preference data for training the ML model.
    Returns a pandas DataFrame with columns: ['emp_id', 'date', 'shift', 'preferred']
    """
    shifts = ['M', 'E', 'N', 'Off', 'TR']
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    delta = (end - start).days + 1

    data = []
    for emp_id in range(1, num_employees + 1):
        for i in range(delta):
            date = start + timedelta(days=i)
            for shift in shifts:
                # Randomly assign preference: 1 with 30% chance, else 0
                preferred = 1 if random.random() < 0.3 else 0
                data.append({
                    'emp_id': emp_id,
                    'date': date.strftime('%Y-%m-%d'),
                    'shift': shift,
                    'preferred': preferred
                })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_mock_historical_data()
    print(df.head())
