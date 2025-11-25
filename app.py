from flask import Flask
from database import db
import os
from flask_login import LoginManager

app = Flask(__name__)

# APP CONFIGURATION
app.config['SECRET_KEY'] = 'planify_secret_key'

# -- ENSURE INSTANCE FOLDER EXISTS --
os.makedirs(app.instance_path, exist_ok=True)

# DATABASE CONNECTION
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'planify.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# FLASK-LOGIN SETUP
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# IMPORT ROUTES
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        print("Database ready!")

        if not User.query.filter_by(username="admin").first():
            dummy_users = [
                User(
                    first_name="Admin",
                    last_name="User",
                    username="admin",
                    email="admin@example.com",
                    contact_number="09123456789",
                    role="admin",
                    password=generate_password_hash("Admin123")
                ),
                User(
                    first_name="John",
                    last_name="Doe",
                    username="student1",
                    email="student1@example.com",
                    contact_number="09111111111",
                    role="student",
                    password=generate_password_hash("Student123")
                ),
                User(
                    first_name="Jane",
                    last_name="Smith",
                    username="educator1",
                    email="educator1@example.com",
                    contact_number="09222222222",
                    role="educator",
                    password=generate_password_hash("Educator123")
                )
            ]

            for user in dummy_users:
                db.session.add(user)
            db.session.commit()
            print("User created!")
        else:
            print("User already exist.")

        app.run(debug=True)
    app.run(debug=True)