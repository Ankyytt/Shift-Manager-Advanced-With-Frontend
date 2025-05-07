import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

class MLPreferenceModel:
    def __init__(self, model_path='ml_preference_model.pkl'):
        # Initialize the model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.trained = False
        self.model_path = model_path
        self.seniority_encoder = LabelEncoder()

    def train(self, historical_data):
        """
        Train the ML model on historical shift preference data.
        historical_data: pd.DataFrame with columns ['emp_id', 'date', 'shift', 'preferred', 'seniority']
        'preferred' is binary: 1 if employee preferred the shift, 0 otherwise.
        """
        # Encode shifts as numeric labels
        historical_data['shift_encoded'] = self.label_encoder.fit_transform(historical_data['shift'])

        # Encode seniority as numeric labels
        historical_data['seniority_encoded'] = self.seniority_encoder.fit_transform(historical_data['seniority'])

        # Extract day of week and day of month
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        historical_data['day'] = historical_data['date'].dt.day
        historical_data['day_of_week'] = historical_data['date'].dt.weekday

        # Features: emp_id (as categorical), day, day_of_week, shift_encoded, seniority_encoded
        historical_data['emp_id_encoded'] = historical_data['emp_id'].astype('category').cat.codes
        X = pd.DataFrame({
            'emp_id': historical_data['emp_id_encoded'],
            'day': historical_data['day'],
            'day_of_week': historical_data['day_of_week'],
            'shift': historical_data['shift_encoded'],
            'seniority': historical_data['seniority_encoded']
        })
        y = historical_data['preferred']

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        self.trained = True

        # Evaluate model
        y_pred = self.model.predict(X_test)
        print("Model Accuracy:", accuracy_score(y_test, y_pred))
        print("Classification Report:\n", classification_report(y_test, y_pred))

        # Save the trained model
        joblib.dump((self.model, self.label_encoder, self.seniority_encoder), self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        if os.path.exists(self.model_path):
            loaded = joblib.load(self.model_path)
            if isinstance(loaded, tuple):
                if len(loaded) == 3:
                    self.model, self.label_encoder, self.seniority_encoder = loaded
                elif len(loaded) == 2:
                    self.model, self.label_encoder = loaded
                    self.seniority_encoder = LabelEncoder()
                else:
                    raise ValueError("Loaded model file has unexpected number of objects")
            else:
                raise ValueError("Loaded model file is not a tuple")
            self.trained = True
            print(f"Model loaded from {self.model_path}")
        else:
            print("No saved model found. Please train the model first.")

    def predict_preferences(self, employees, year, month, days_in_month, shifts):
        """
        Predict preference scores for each employee, day, and shift.
        Returns a dict with keys (emp_id, date_str, shift) and values as penalty scores (float).
        Lower score means more preferred.
        If model is not trained, returns default penalties.
        """
        preference_scores = {}
        for e in employees:
            for d in range(1, days_in_month + 1):
                date_str = f"{year:04d}-{month:02d}-{d:02d}"
                for s in shifts:
                    if self.trained:
                        # Prepare feature vector
                        emp_code = e.id  # Assuming emp_id is numeric or can be used directly
                        day = d
                        day_of_week = pd.Timestamp(date_str).weekday()
                        try:
                            shift_encoded = self.label_encoder.transform([s])[0]
                        except ValueError:
                            shift_encoded = 0  # default if unseen shift

                        try:
                            seniority_encoded = self.seniority_encoder.transform([e.seniority])[0]
                        except Exception:
                            seniority_encoded = 0
                        X_pred = pd.DataFrame([[emp_code, day, day_of_week, shift_encoded, seniority_encoded]], 
                                              columns=['emp_id', 'day', 'day_of_week', 'shift', 'seniority'])
                        prob = self.model.predict_proba(X_pred)[0][1]  # probability of preferred=1
                        penalty = 1 - prob  # lower penalty for higher preference probability
                    else:
                        # Default penalty if not trained: simple heuristic
                        try:
                            seniority_val = int(e.seniority)
                        except Exception:
                            seniority_val = 0
                        penalty = 0.5 if s == 'M' and seniority_val > 5 else 1.0
                    preference_scores[(e.id, date_str, s)] = penalty
        return preference_scores
