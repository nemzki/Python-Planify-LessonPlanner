from flask import Flask
from database import db
import os

app = Flask(__name__)

# APP CONFIGURATION
app.config['SECRET_KEY'] = 'planify_secret_key'

# DATABASE CONNECTION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/planify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# IMPORT ROUTES
from routes import *

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists("instance/planify.db"):
            os.makedirs(app.instance_path, exist_ok=True)
            db.create_all()
            print("Database created!")
        else:
            print("Database already exists.")
    app.run(debug=True)