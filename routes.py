from flask import render_template, redirect, url_for, flash, request
from app import app
from database import db
from forms import RegisterForm, LoginForm, CourseForm, LessonPlanForm, AttendanceForm, EnrollmentForm
from models import User, Course, LessonPlan, LearningMaterial, Enrollment, AttendanceRecord
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os

# ==========================================
# FILE UPLOAD CONFIGURATION
# ==========================================
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'jpg', 'png'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# PUBLIC PAGES
# ==========================================

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


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

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
    form.role.data = role
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
                return redirect(url_for('student_home'))
            elif user.role == "educator":
                return redirect(url_for('educator_home'))
            elif user.role == "admin":
                return redirect(url_for('admin_home'))

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


# ==========================================
# STUDENT DASHBOARD
# ==========================================

@app.route('/student/home')
@login_required
def student_home():
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    # Get enrolled courses
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    courses = [enrollment.course for enrollment in enrollments]

    return render_template('student_home.html', courses=courses)


# ==========================================
# EDUCATOR DASHBOARD
# ==========================================

@app.route('/educator/home')
@login_required
def educator_home():
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))
    return render_template('educator_home.html')


# ==========================================
# COURSE MANAGEMENT (EDUCATOR)
# ==========================================

# VIEW ALL COURSES
@app.route('/educator/courses')
@login_required
def educator_courses():
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    courses = Course.query.filter_by(educator_id=current_user.id).all()
    return render_template('educator_courses.html', courses=courses)


# ADD NEW COURSE
@app.route('/educator/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    form = CourseForm()

    if form.validate_on_submit():
        new_course = Course(
            course_name=form.course_name.data,
            course_code=form.course_code.data,
            description=form.description.data,
            educator_id=current_user.id
        )

        db.session.add(new_course)
        db.session.commit()

        flash(f"Course '{new_course.course_name}' created successfully!", "success")
        return redirect(url_for('educator_courses'))

    return render_template('add_course.html', form=form)


# EDIT COURSE
@app.route('/educator/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    # Check if educator owns this course
    if course.educator_id != current_user.id:
        flash("You don't have permission to edit this course.", "error")
        return redirect(url_for('educator_courses'))

    form = CourseForm()

    if form.validate_on_submit():
        course.course_name = form.course_name.data
        course.course_code = form.course_code.data
        course.description = form.description.data

        db.session.commit()
        flash(f"Course '{course.course_name}' updated successfully!", "success")
        return redirect(url_for('educator_courses'))

    # Pre-fill form
    form.course_name.data = course.course_name
    form.course_code.data = course.course_code
    form.description.data = course.description

    return render_template('edit_course.html', form=form, course=course)


# DELETE COURSE
@app.route('/educator/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("You don't have permission to delete this course.", "error")
        return redirect(url_for('educator_courses'))

    db.session.delete(course)
    db.session.commit()

    flash(f"Course '{course.course_name}' deleted successfully!", "success")
    return redirect(url_for('educator_courses'))


# ==========================================
# LESSON PLAN MANAGEMENT (EDUCATOR)
# ==========================================

# VIEW ALL LESSON PLANS FOR A COURSE
@app.route('/educator/course/<int:course_id>/plans')
@login_required
def course_lesson_plans(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    lesson_plans = LessonPlan.query.filter_by(course_id=course_id).all()

    return render_template('lesson_plans.html', course=course, lesson_plans=lesson_plans)


# CREATE LESSON PLAN
@app.route('/educator/course/<int:course_id>/plan/add', methods=['GET', 'POST'])
@login_required
def add_lesson_plan(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    form = LessonPlanForm()

    if form.validate_on_submit():
        # Create lesson plan
        new_plan = LessonPlan(
            title=form.title.data,
            topic=form.topic.data,
            objectives=form.objectives.data,
            description=form.description.data,
            course_id=course_id,
            educator_id=current_user.id
        )

        db.session.add(new_plan)
        db.session.commit()

        # Handle file uploads
        files = request.files.getlist('materials')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)

                # Save to database
                material = LearningMaterial(
                    lesson_plan_id=new_plan.id,
                    filename=filename,
                    filepath=filepath
                )
                db.session.add(material)

        db.session.commit()

        flash(f"Lesson plan '{new_plan.title}' created successfully!", "success")
        return redirect(url_for('course_lesson_plans', course_id=course_id))

    return render_template('add_lesson_plan.html', form=form, course=course)


# VIEW LESSON PLAN DETAILS
@app.route('/educator/plan/<int:plan_id>')
@login_required
def view_lesson_plan(plan_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    plan = LessonPlan.query.get_or_404(plan_id)

    if plan.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    return render_template('view_lesson_plan.html', plan=plan)


# EDIT LESSON PLAN
@app.route('/educator/plan/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson_plan(plan_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    plan = LessonPlan.query.get_or_404(plan_id)

    if plan.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    form = LessonPlanForm()

    if form.validate_on_submit():
        plan.title = form.title.data
        plan.topic = form.topic.data
        plan.objectives = form.objectives.data
        plan.description = form.description.data
        plan.updated_at = datetime.utcnow()

        # Handle new file uploads
        files = request.files.getlist('materials')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)

                material = LearningMaterial(
                    lesson_plan_id=plan.id,
                    filename=filename,
                    filepath=filepath
                )
                db.session.add(material)

        db.session.commit()
        flash(f"Lesson plan '{plan.title}' updated successfully!", "success")
        return redirect(url_for('view_lesson_plan', plan_id=plan.id))

    # Pre-fill form
    form.title.data = plan.title
    form.topic.data = plan.topic
    form.objectives.data = plan.objectives
    form.description.data = plan.description

    return render_template('edit_lesson_plan.html', form=form, plan=plan)


# DELETE LESSON PLAN
@app.route('/educator/plan/<int:plan_id>/delete', methods=['POST'])
@login_required
def delete_lesson_plan(plan_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    plan = LessonPlan.query.get_or_404(plan_id)
    course_id = plan.course_id

    if plan.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    db.session.delete(plan)
    db.session.commit()

    flash(f"Lesson plan '{plan.title}' deleted successfully!", "success")
    return redirect(url_for('course_lesson_plans', course_id=course_id))


# DELETE LEARNING MATERIAL
@app.route('/educator/material/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    material = LearningMaterial.query.get_or_404(material_id)
    plan = material.lesson_plan

    if plan.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    # Delete file from filesystem
    if os.path.exists(material.filepath):
        os.remove(material.filepath)

    db.session.delete(material)
    db.session.commit()

    flash("Material removed successfully!", "success")
    return redirect(url_for('view_lesson_plan', plan_id=plan.id))


# ==========================================
# ATTENDANCE MANAGEMENT (EDUCATOR)
# ==========================================

# VIEW ATTENDANCE PAGE FOR A COURSE
@app.route('/educator/course/<int:course_id>/attendance', methods=['GET', 'POST'])
@login_required
def course_attendance(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    form = AttendanceForm()

    # Get enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = [enrollment.student for enrollment in enrollments]

    # Get selected date or default to today
    selected_date = date.today()
    if form.validate_on_submit():
        selected_date = form.date.data

    # Get existing attendance for selected date
    attendance_records = {}
    records = AttendanceRecord.query.filter_by(course_id=course_id, date=selected_date).all()
    for record in records:
        attendance_records[record.student_id] = record.status

    form.date.data = selected_date

    return render_template('course_attendance.html',
                           course=course,
                           students=students,
                           form=form,
                           selected_date=selected_date,
                           attendance_records=attendance_records)


# RECORD/UPDATE ATTENDANCE
@app.route('/educator/attendance/record', methods=['POST'])
@login_required
def record_attendance():
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course_id = request.form.get('course_id')
    attendance_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    # Get all students in the course
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    for enrollment in enrollments:
        student_id = enrollment.student_id
        status = request.form.get(f'student_{student_id}')

        if status:
            # Check if record exists
            existing_record = AttendanceRecord.query.filter_by(
                course_id=course_id,
                student_id=student_id,
                date=attendance_date
            ).first()

            if existing_record:
                # Update existing record
                existing_record.status = status
            else:
                # Create new record
                new_record = AttendanceRecord(
                    course_id=course_id,
                    student_id=student_id,
                    date=attendance_date,
                    status=status,
                    recorded_by=current_user.id
                )
                db.session.add(new_record)

    db.session.commit()
    flash("Attendance recorded successfully!", "success")
    return redirect(url_for('course_attendance', course_id=course_id))


# ==========================================
# ENROLLMENT MANAGEMENT (EDUCATOR)
# ==========================================

# MANAGE ENROLLMENTS FOR A COURSE
@app.route('/educator/course/<int:course_id>/enrollments', methods=['GET', 'POST'])
@login_required
def manage_enrollments(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    form = EnrollmentForm()

    # Get all students not yet enrolled
    enrolled_ids = [e.student_id for e in Enrollment.query.filter_by(course_id=course_id).all()]
    available_students = User.query.filter(User.role == 'student', ~User.id.in_(enrolled_ids)).all()

    form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name} ({s.username})") for s in available_students]

    if form.validate_on_submit():
        new_enrollment = Enrollment(
            student_id=form.student_id.data,
            course_id=course_id
        )
        db.session.add(new_enrollment)
        db.session.commit()

        flash("Student enrolled successfully!", "success")
        return redirect(url_for('manage_enrollments', course_id=course_id))

    # Get current enrollments
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    return render_template('manage_enrollments.html', course=course, enrollments=enrollments, form=form)


# REMOVE ENROLLMENT
@app.route('/educator/enrollment/<int:enrollment_id>/remove', methods=['POST'])
@login_required
def remove_enrollment(enrollment_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    enrollment = Enrollment.query.get_or_404(enrollment_id)
    course = enrollment.course

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    db.session.delete(enrollment)
    db.session.commit()

    flash("Student removed from course.", "success")
    return redirect(url_for('manage_enrollments', course_id=course.id))


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route('/admin/home')
@login_required
def admin_home():
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    # Get statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_educators = User.query.filter_by(role='educator').count()
    total_courses = Course.query.count()

    return render_template('admin_home.html',
                           total_users=total_users,
                           total_students=total_students,
                           total_educators=total_educators,
                           total_courses=total_courses)


# VIEW ALL USERS
@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('admin_users.html', users=users)


# VIEW ALL COURSES
@app.route('/admin/courses')
@login_required
def admin_courses():
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    courses = Course.query.all()
    return render_template('admin_courses.html', courses=courses)