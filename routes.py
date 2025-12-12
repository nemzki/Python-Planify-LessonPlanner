from flask import render_template, redirect, url_for, flash, request
from app import app
from database import db
from forms import RegisterForm, LoginForm, CourseForm, LessonPlanForm, AttendanceForm, ContactForm, EnrollByEmailForm, JoinCourseForm
from models import User, Course, LessonPlan, LearningMaterial, Enrollment, AttendanceRecord, ContactMessage
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

# Ensure the upload folder exists
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

            # REDIRECT BASED ON ROLE - FIXED ORDER
            if user.role == "admin":
                return redirect(url_for('admin_home'))
            elif user.role == "educator":
                return redirect(url_for('educator_home'))
            elif user.role == "student":
                return redirect(url_for('student_home'))
            else:
                # Fallback for unknown roles
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


# ==========================================
# COURSE CREATION - UPDATE TO GENERATE CODE
# ==========================================

# ADD NEW COURSE - UPDATED
@app.route('/educator/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    form = CourseForm()

    if form.validate_on_submit():
        # Generate unique enrollment code
        enrollment_code = Course.generate_enrollment_code()

        new_course = Course(
            course_name=form.course_name.data,
            course_code=form.course_code.data,
            block_section=form.block_section.data,
            description=form.description.data,
            educator_id=current_user.id,
            enrollment_code=enrollment_code  # NEW: Add enrollment code
        )

        db.session.add(new_course)
        db.session.commit()

        flash(f"Course '{new_course.course_name}' created! Enrollment code: {enrollment_code}", "success")
        return redirect(url_for('educator_courses'))

    return render_template('add_course.html', form=form)


# ==========================================
# ENROLLMENT MANAGEMENT - UPDATED
# ==========================================

# MANAGE ENROLLMENTS BY EMAIL (EDUCATOR)
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

    form = EnrollByEmailForm()

    if form.validate_on_submit():
        student_email = form.student_email.data

        # Find student by email
        student = User.query.filter_by(email=student_email, role='student').first()

        if not student:
            flash("No student found with that email address.", "error")
            return redirect(url_for('manage_enrollments', course_id=course_id))

        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=course_id
        ).first()

        if existing_enrollment:
            flash(f"{student.first_name} {student.last_name} is already enrolled in this course.", "error")
            return redirect(url_for('manage_enrollments', course_id=course_id))

        # Enroll student
        new_enrollment = Enrollment(
            student_id=student.id,
            course_id=course_id
        )
        db.session.add(new_enrollment)
        db.session.commit()

        flash(f"{student.first_name} {student.last_name} enrolled successfully!", "success")
        return redirect(url_for('manage_enrollments', course_id=course_id))

    # Get current enrollments
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    return render_template('manage_enrollments.html', course=course, enrollments=enrollments, form=form)


# ==========================================
# STUDENT - JOIN COURSE BY CODE
# ==========================================

# JOIN COURSE BY CODE (STUDENT)
@app.route('/student/join-course', methods=['GET', 'POST'])
@login_required
def student_join_course():
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    form = JoinCourseForm()

    if form.validate_on_submit():
        enrollment_code = form.enrollment_code.data.upper().strip()

        # Find course by enrollment code
        course = Course.query.filter_by(enrollment_code=enrollment_code).first()

        if not course:
            flash("Invalid course code. Please check and try again.", "error")
            return redirect(url_for('student_join_course'))

        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course.id
        ).first()

        if existing_enrollment:
            flash(f"You are already enrolled in {course.course_name}.", "error")
            return redirect(url_for('student_home'))

        # Enroll student
        new_enrollment = Enrollment(
            student_id=current_user.id,
            course_id=course.id
        )
        db.session.add(new_enrollment)
        db.session.commit()

        flash(f"Successfully enrolled in {course.course_name}!", "success")
        return redirect(url_for('student_home'))

    return render_template('student_join_course.html', form=form)

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
        course.block_section = form.block_section.data
        course.description = form.description.data

        db.session.commit()
        flash(f"Course '{course.course_name}' updated successfully!", "success")
        return redirect(url_for('educator_courses'))

    # Pre-fill form
    form.course_name.data = course.course_name
    form.course_code.data = course.course_code
    form.block_section.data = course.block_section
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

    # Get selected date from URL parameter or form or default to today
    selected_date = date.today()

    # Check if date is passed in URL (when clicking edit from detail page)
    url_date = request.args.get('date')
    if url_date:
        try:
            selected_date = datetime.strptime(url_date, '%Y-%m-%d').date()
        except ValueError:
            pass
    elif form.validate_on_submit():
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


# ==========================================
# ATTENDANCE HISTORY (EDUCATOR)
# ==========================================

# VIEW ATTENDANCE HISTORY FOR A COURSE
@app.route('/educator/course/<int:course_id>/attendance/history')
@login_required
def attendance_history(course_id):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    # Get all attendance records for this course, ordered by date (newest first)
    # Group by date to show all records created on each date
    from sqlalchemy import func, distinct

    # Get all unique dates that have attendance records
    attendance_dates = db.session.query(
        AttendanceRecord.date
    ).filter_by(
        course_id=course_id
    ).distinct().order_by(
        AttendanceRecord.date.desc()
    ).all()

    # For each date, get all the records
    attendance_by_date = {}
    for (date_obj,) in attendance_dates:
        records = AttendanceRecord.query.filter_by(
            course_id=course_id,
            date=date_obj
        ).order_by(AttendanceRecord.recorded_at.desc()).all()

        # Get the time when this attendance was recorded (from first record)
        recorded_time = records[0].recorded_at if records else None

        # Count statistics for this date
        stats = {
            'total': len(records),
            'present': len([r for r in records if r.status == 'present']),
            'absent': len([r for r in records if r.status == 'absent']),
            'excused': len([r for r in records if r.status == 'excused']),
            'late': len([r for r in records if r.status == 'late'])
        }

        attendance_by_date[date_obj] = {
            'records': records,
            'recorded_time': recorded_time,
            'stats': stats
        }

    return render_template('attendance_history.html',
                           course=course,
                           attendance_by_date=attendance_by_date)


# VIEW DETAILED ATTENDANCE FOR A SPECIFIC DATE
@app.route('/educator/course/<int:course_id>/attendance/view/<date_str>')
@login_required
def view_attendance_date(course_id, date_str):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    # Convert date string to date object
    from datetime import datetime
    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Get all attendance records for this date
    records = AttendanceRecord.query.filter_by(
        course_id=course_id,
        date=attendance_date
    ).order_by(AttendanceRecord.recorded_at.desc()).all()

    # Get enrollment info to show all students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    # Create a dictionary for easy lookup
    attendance_dict = {record.student_id: record for record in records}

    return render_template('view_attendance_detail.html',
                           course=course,
                           attendance_date=attendance_date,
                           records=records,
                           enrollments=enrollments,
                           attendance_dict=attendance_dict)


# DOWNLOAD ATTENDANCE AS PDF
@app.route('/educator/course/<int:course_id>/attendance/download/<date_str>')
@login_required
def download_attendance_pdf(course_id, date_str):
    if current_user.role != 'educator':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if course.educator_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('educator_courses'))

    # Convert date string to date object
    from datetime import datetime
    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Get all attendance records for this date
    records = AttendanceRecord.query.filter_by(
        course_id=course_id,
        date=attendance_date
    ).order_by(AttendanceRecord.student_id).all()

    # Get all enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    # Create PDF
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

    elements = []
    styles = getSampleStyleSheet()

    # Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Subtitle Style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6,
        alignment=TA_CENTER
    )

    # Add Title
    title = Paragraph(f"<b>Attendance Report</b>", title_style)
    elements.append(title)

    # Add Course Info
    course_info = Paragraph(f"{course.course_name} ({course.course_code})", subtitle_style)
    elements.append(course_info)

    block_info = Paragraph(f"Block: {course.block_section}", subtitle_style)
    elements.append(block_info)

    date_info = Paragraph(f"Date: {attendance_date.strftime('%A, %B %d, %Y')}", subtitle_style)
    elements.append(date_info)

    if records:
        recorded_info = Paragraph(
            f"Recorded on: {records[0].recorded_at.strftime('%B %d, %Y at %I:%M %p')}",
            subtitle_style
        )
        elements.append(recorded_info)

    elements.append(Spacer(1, 0.3 * inch))

    # Create attendance dictionary
    attendance_dict = {record.student_id: record for record in records}

    # Calculate statistics
    total_students = len(enrollments)
    present_count = len([r for r in records if r.status == 'present'])
    absent_count = len([r for r in records if r.status == 'absent'])
    late_count = len([r for r in records if r.status == 'late'])
    excused_count = len([r for r in records if r.status == 'excused'])

    # Add Statistics Table
    stats_data = [
        ['Total Students', 'Present', 'Absent', 'Late', 'Excused'],
        [str(total_students), str(present_count), str(absent_count), str(late_count), str(excused_count)]
    ]

    stats_table = Table(stats_data, colWidths=[1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    elements.append(stats_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Add Student Attendance Table
    data = [['#', 'Student Name', 'Username', 'Status']]

    for idx, enrollment in enumerate(enrollments, 1):
        student = enrollment.student
        record = attendance_dict.get(student.id)

        status_text = 'Not Recorded'
        if record:
            status_text = record.status.capitalize()

        data.append([
            str(idx),
            f"{student.first_name} {student.last_name}",
            student.username,
            status_text
        ])

    table = Table(data, colWidths=[0.5 * inch, 2.5 * inch, 1.8 * inch, 1.5 * inch])

    # Table styling
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Center # column
        ('ALIGN', (1, 1), (-2, -1), 'LEFT'),  # Left align name and username
        ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),  # Center status column
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    # Add status-specific coloring
    for idx, enrollment in enumerate(enrollments, 1):
        record = attendance_dict.get(enrollment.student.id)
        if record:
            if record.status == 'present':
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor('#27ae60')),
                    ('FONTNAME', (3, idx), (3, idx), 'Helvetica-Bold'),
                ]))
            elif record.status == 'absent':
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor('#e74c3c')),
                    ('FONTNAME', (3, idx), (3, idx), 'Helvetica-Bold'),
                ]))
            elif record.status == 'late':
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor('#f39c12')),
                    ('FONTNAME', (3, idx), (3, idx), 'Helvetica-Bold'),
                ]))
            elif record.status == 'excused':
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor('#3498db')),
                    ('FONTNAME', (3, idx), (3, idx), 'Helvetica-Bold'),
                ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    # Send file
    from flask import send_file
    filename = f"attendance_{course.course_code}_{date_str}.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

# ==========================================
# STUDENT MATERIALS & LESSON PLANS
# ==========================================

# VIEW LESSON PLANS FOR A SPECIFIC COURSE (STUDENT)
@app.route('/student/course/<int:course_id>/lessons')
@login_required
def student_course_lessons(course_id):
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    # Check if student is enrolled in this course
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        flash("You are not enrolled in this course.", "error")
        return redirect(url_for('student_home'))

    course = Course.query.get_or_404(course_id)
    lesson_plans = LessonPlan.query.filter_by(course_id=course_id).order_by(
        LessonPlan.created_at.desc()
    ).all()

    return render_template('student_course_lessons.html',
                           course=course,
                           lesson_plans=lesson_plans)


# VIEW SPECIFIC LESSON PLAN (STUDENT)
@app.route('/student/lesson/<int:plan_id>')
@login_required
def student_view_lesson(plan_id):
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    plan = LessonPlan.query.get_or_404(plan_id)

    # Check if student is enrolled in the course
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=plan.course_id
    ).first()

    if not enrollment:
        flash("You are not enrolled in this course.", "error")
        return redirect(url_for('student_home'))

    return render_template('student_view_lesson.html', plan=plan)


# DOWNLOAD MATERIAL (STUDENT)
@app.route('/student/material/<int:material_id>/download')
@login_required
def student_download_material(material_id):
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    material = LearningMaterial.query.get_or_404(material_id)
    plan = material.lesson_plan

    # Check if student is enrolled in the course
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=plan.course_id
    ).first()

    if not enrollment:
        flash("You are not enrolled in this course.", "error")
        return redirect(url_for('student_home'))

    # Send file for download
    from flask import send_file
    return send_file(material.filepath, as_attachment=True, download_name=material.filename)


# VIEW ALL MATERIALS FOR A COURSE (STUDENT)
@app.route('/student/course/<int:course_id>/materials')
@login_required
def student_course_materials(course_id):
    if current_user.role != 'student':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        flash("You are not enrolled in this course.", "error")
        return redirect(url_for('student_home'))

    course = Course.query.get_or_404(course_id)

    # Get all lesson plans with materials
    lesson_plans = LessonPlan.query.filter_by(course_id=course_id).order_by(
        LessonPlan.created_at.desc()
    ).all()

    # Count total materials
    total_materials = sum(len(plan.materials) for plan in lesson_plans)

    return render_template('student_course_materials.html',
                           course=course,
                           lesson_plans=lesson_plans,
                           total_materials=total_materials)


# ==========================================
# CONTACT PAGE ROUTES
# ==========================================

# CONTACT PAGE
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    from forms import ContactForm
    from models import ContactMessage

    form = ContactForm()

    if form.validate_on_submit():
        # Create new contact message
        new_message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )

        db.session.add(new_message)
        db.session.commit()

        flash("Thank you for your message! We'll get back to you soon.", "success")
        return redirect(url_for('contacts'))

    return render_template('contacts.html', form=form)


# ==========================================
# ADMIN - VIEW CONTACT MESSAGES
# ==========================================

# VIEW ALL CONTACT MESSAGES (ADMIN)
@app.route('/admin/messages')
@login_required
def admin_messages():
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    from models import ContactMessage

    # Get all messages, ordered by newest first
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()

    # Count unread messages
    unread_count = ContactMessage.query.filter_by(is_read=False).count()

    return render_template('admin_messages.html', messages=messages, unread_count=unread_count)


# MARK MESSAGE AS READ (ADMIN)
@app.route('/admin/message/<int:message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    from models import ContactMessage

    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()

    flash("Message marked as read.", "success")
    return redirect(url_for('admin_messages'))


# DELETE MESSAGE (ADMIN)
@app.route('/admin/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    from models import ContactMessage

    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()

    flash("Message deleted successfully.", "success")
    return redirect(url_for('admin_messages'))