import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import create_app, db

app = create_app()
app.app_context().push()

db.create_all()
print("✅ Database tables created!")
