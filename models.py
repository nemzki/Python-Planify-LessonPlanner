from database import db
from flask_login import UserMixin
from datetime import datetime
import string
import random

# ==========================================
# USER MODEL
# ==========================================
# Stores user information for authentication
# Supports three roles: admin, educator, student
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_number = db.Column(db.String(11), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    # Relationships
    courses = db.relationship('Course', backref='educator', lazy=True, cascade='all, delete-orphan')
    lesson_plans = db.relationship('LessonPlan', backref='creator', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW: Add enrollment code (unique, auto-generated)
    enrollment_code = db.Column(db.String(10), unique=True, nullable=False)

    # Relationships
    lesson_plans = db.relationship('LessonPlan', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='course', lazy=True, cascade='all, delete-orphan')

    # Method to generate enrollment code
    @staticmethod
    def generate_enrollment_code():
        """Generate a unique 8-character enrollment code"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(8))
            # Check if code already exists
            if not Course.query.filter_by(enrollment_code=code).first():
                return code


# ==========================================
# LESSON PLAN MODEL
# ==========================================
# Stores lesson plan details created by educators
class LessonPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    educator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Lesson Plan Content
    objectives = db.Column(db.Text, nullable=True)
    topic = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    materials = db.relationship('LearningMaterial', backref='lesson_plan', lazy=True, cascade='all, delete-orphan')


# ==========================================
# LEARNING MATERIAL MODEL
# ==========================================
# Stores files/resources attached to lesson plans
class LearningMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_plan_id = db.Column(db.Integer, db.ForeignKey('lesson_plan.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==========================================
# ENROLLMENT MODEL
# ==========================================
# Links students to courses
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure a student can't enroll in the same course twice
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)


# ==========================================
# ATTENDANCE RECORD MODEL
# ==========================================
# Stores attendance records for students in courses
class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present, absent, excused, late
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to recorder (educator)
    recorder = db.relationship('User', foreign_keys=[recorded_by])

    # Ensure unique attendance record per student per course per date
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'date', name='unique_attendance'),)


# ==========================================
# CONTACT MESSAGE MODEL
# ==========================================
# Stores contact messages from users
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ContactMessage {self.id} from {self.email}>'