import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shift_manager.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from backend.routes import shift_routes

    app.register_blueprint(shift_routes.shift_bp)
    
    from backend.routes.schedule_routes import schedule_bp
    app.register_blueprint(schedule_bp)

    
    @app.route('/')
    def home():
        return 'Shift Manager Backend is running!'

    return app
