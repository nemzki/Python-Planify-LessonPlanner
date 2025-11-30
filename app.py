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
                ),
                User(
                    first_name="Elaine",
                    last_name="Villanueva",
                    username="evillanueva",
                    email="evillanueva@example.com",
                    contact_number="09333333333",
                    role="educator",
                    password=generate_password_hash("villanueva123")
                ),
                User(
                    first_name="Roland",
                    last_name="Santos",
                    username="rsantos",
                    email="rsantos@example.com",
                    contact_number="09444444444",
                    role="educator",
                    password=generate_password_hash("rsantos123")
                ),
                User(
                    first_name="Patricia",
                    last_name="Cruz",
                    username="pcruz",
                    email="pcruz@example.com",
                    contact_number="09555555555",
                    role="educator",
                    password=generate_password_hash("pcruz123")
                ),
                User(
                    first_name="Alfred",
                    last_name="Torres",
                    username="atorres",
                    email="atorres@example.com",
                    contact_number="09666666666",
                    role="student",
                    password=generate_password_hash("atorres123")
                ),
                User(
                    first_name="Bianca",
                    last_name="Mendoza",
                    username="bmendoza",
                    email="bmendoza@example.com",
                    contact_number="0977777777",
                    role="student",
                    password=generate_password_hash("bmendoza123")
                ),
                User(
                    first_name="Cedric",
                    last_name="Gonzales",
                    username="cgonzales",
                    email="cgonzales@example.com",
                    contact_number="09888888888",
                    role="student",
                    password=generate_password_hash("cgonzales123")
                ),
                User(
                    first_name="Danica",
                    last_name="Flores",
                    username="dflores",
                    email="dflores@example.com",
                    contact_number="09999999999",
                    role="student",
                    password=generate_password_hash("dflores123")
                ),
                User(
                    first_name="Ethan",
                    last_name="Navarro",
                    username="enavarro",
                    email="enavarro@example.com",
                    contact_number="09122222222",
                    role="student",
                    password=generate_password_hash("enavarro123")
                ),
                User(
                    first_name="Fiona",
                    last_name="Salazar",
                    username="fsalazar",
                    email="fsalazar@example.com",
                    contact_number="09133333333",
                    role="student",
                    password=generate_password_hash("fsalazar123")
                ),
                User(
                    first_name="Gabriel",
                    last_name="David",
                    username="gdavid",
                    email="gdavid@example.com",
                    contact_number="09144444444",
                    role="student",
                    password=generate_password_hash("gdavid123")
                ),
                User(
                    first_name="Hannah",
                    last_name="Ocampo",
                    username="hocampo",
                    email="hocampo@example.com",
                    contact_number="09155555555",
                    role="student",
                    password=generate_password_hash("hocampo123")
                ),
                User(
                    first_name="Ian",
                    last_name="Perez",
                    username="iperez",
                    email="iperez@example.com",
                    contact_number="09166666666",
                    role="student",
                    password=generate_password_hash("iperez123")
                ),
                User(
                    first_name="Jasmine",
                    last_name="Ramos",
                    username="jramos",
                    email="jramos@example.com",
                    contact_number="09177777777",
                    role="student",
                    password=generate_password_hash("jramos123")
                ),
                User(
                    first_name="Kyle",
                    last_name="Bautista",
                    username="kbautista",
                    email="kbautista@example.com",
                    contact_number="09188888888",
                    role="student",
                    password=generate_password_hash("kbautista123")
                ),
                User(
                    first_name="Lara",
                    last_name="Domingo",
                    username="ldomingo",
                    email="ldomingo@example.com",
                    contact_number="09199999999",
                    role="student",
                    password=generate_password_hash("ldomingo123")
                ),
                User(
                    first_name="Marcus",
                    last_name="Jimenez",
                    username="mjimenez",
                    email="mjimenez@example.com",
                    contact_number="0911222222",
                    role="student",
                    password=generate_password_hash("mjimenez123")
                ),
                User(
                    first_name="Nicole",
                    last_name="Padilla",
                    username="npadilla",
                    email="npadilla@example.com",
                    contact_number="09113333333",
                    role="student",
                    password=generate_password_hash("npadilla123")
                ),
                User(
                    first_name="Oscar",
                    last_name="Valdez",
                    username="ovaldez",
                    email="ovaldez@example.com",
                    contact_number="09114444444",
                    role="student",
                    password=generate_password_hash("ovaldez123")
                ),
                User(
                    first_name="Paula",
                    last_name="Marasigan",
                    username="pmarasigan",
                    email="pmarasigan@example.com",
                    contact_number="09115555555",
                    role="student",
                    password=generate_password_hash("pmarasigan123")
                ),
                User(
                    first_name="Quentin",
                    last_name="Abadilla",
                    username="qabadilla",
                    email="qabadilla@example.com",
                    contact_number="09116666666",
                    role="student",
                    password=generate_password_hash("qabadilla123")
                ),
                User(
                    first_name="Rhea",
                    last_name="Lagman",
                    username="rlagman",
                    email="rlagman@example.com",
                    contact_number="09117777777",
                    role="student",
                    password=generate_password_hash("rlagman123")
                ),
                User(
                    first_name="Samuel",
                    last_name="Fernandez",
                    username="sfernandez",
                    email="sfernandez@example.com",
                    contact_number="09118888888",
                    role="student",
                    password=generate_password_hash("sfernandez123")
                ),
                User(
                    first_name="Trixie",
                    last_name="Gutierrez",
                    username="tgutierrez",
                    email="tgutierrez@example.com",
                    contact_number="09119999999",
                    role="student",
                    password=generate_password_hash("tgutierrez123")
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