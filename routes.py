from flask import render_template, redirect, url_for, flash, request
from app import app
from database import db
from forms import RegisterForm, LoginForm
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

# LANDING PAGE
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about-us')
def about_us():
    return render_template('about_us.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

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

    form.role.render_kw = {'readonly': True, 'disabled': True}

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username_or_email = form.username_or_email.data
        password = form.password.data

        # Try to find user by username OR email
        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")

            # REDIRECT BASED ON ROLE
            if user.role == "student":
                return redirect(url_for('student_dashboard'))
            elif user.role == "educator":
                return redirect(url_for('educator_dashboard'))
            elif user.role == "admin":
                return redirect(url_for('admin_dashboard'))

            return redirect(url_for('home'))

        else:
            flash("Invalid username/email or password.", "error")
            return redirect(url_for('login'))

    return render_template("login.html", form=form)

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

#-------  DASHBOARDS ---------

# -- STUDENT DASHBOARD --
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))
    return render_template('student_dashboard.html')

# -- EDUCATOR DASHBOARD --
@app.route('/educator/dashboard')
@login_required
def educator_dashboard():
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))
    return render_template('educator_dashboard.html')

# -- ADMIN DASHBOARD --
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')
