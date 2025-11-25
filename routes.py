from flask import render_template, redirect, url_for, flash
from app import app, db
from forms import RegisterForm
from models import User
from werkzeug.security import generate_password_hash

# LANDING PAGE
@app.route('/')
def home():
    return render_template('home.html')

# CHOOSE ROLE PAGE
@app.route('/choose-role')
def choose_role():
    return render_template('choose_role.html')

# REGISTER REDIRECT
@app.route('/register')
def register():
    return redirect(url_for('choose_role'))

# REGISTER FORM (WITH ROLE)
@app.route('/register/<role>', methods=["GET", "POST"])
def register_form(role):
    form = RegisterForm()
    form.role.data = role  # Pre-fill role

    if form.validate_on_submit():

        # CHECK USERNAME
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.", "error")
            return redirect(url_for('register_form', role=role))

        # CHECK EMAIL
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "error")
            return redirect(url_for('register_form', role=role))

        # CREATE USER
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            contact_number=form.contact_number.data,
            role=role,
            password=generate_password_hash(form.password.data)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template("register.html", form=form, role=role)

# LOGIN PAGE
@app.route('/login')
def login():
    return render_template("login.html")
