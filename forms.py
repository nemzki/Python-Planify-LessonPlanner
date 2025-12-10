from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, Optional


# ==========================================
# AUTHENTICATION FORMS
# ==========================================

# PLANIFY | REGISTRATION FORM
class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=3, max=20)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    contact_number = StringField("Contact number", validators=[
        DataRequired(),
        Length(min=11, max=11, message="Contact number must be 11 digits"),
        Regexp(r'^[0-9]*$', message="Contact number must contain only digits")
    ])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('password', message="Passwords must match")
    ])
    role = SelectField("Role",
                       choices=[("educator", "Educator"), ("student", "Student")],
                       validators=[DataRequired()]
                       )
    submit = SubmitField("Register")


# PLANIFY | LOGIN FORM
class LoginForm(FlaskForm):
    username_or_email = StringField("Username or Email", validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Login")


# ==========================================
# COURSE FORMS
# ==========================================

# FORM FOR CREATING/EDITING COURSES
class CourseForm(FlaskForm):
    course_name = StringField("Course Name", validators=[DataRequired(), Length(min=3, max=100)])
    course_code = StringField("Course Code", validators=[DataRequired(), Length(min=2, max=20)])
    block_section = StringField("Block Section", validators=[DataRequired(), Length(max=20)])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Save Course")


# ==========================================
# LESSON PLAN FORMS
# ==========================================

# FORM FOR CREATING/EDITING LESSON PLANS
class LessonPlanForm(FlaskForm):
    title = StringField("Lesson Title", validators=[DataRequired(), Length(min=3, max=200)])
    topic = StringField("Topic", validators=[Optional(), Length(max=200)])
    objectives = TextAreaField("Learning Objectives", validators=[Optional()])
    description = TextAreaField("Lesson Description", validators=[Optional()])

    # Multiple file upload for learning materials
    materials = MultipleFileField("Learning Materials", validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'jpg', 'png'],
                    'Only documents and images allowed!')
    ])

    submit = SubmitField("Save Lesson Plan")


# ==========================================
# ATTENDANCE FORMS
# ==========================================

# FORM FOR RECORDING ATTENDANCE
class AttendanceForm(FlaskForm):
    date = DateField("Attendance Date", validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField("Record Attendance")


# ==========================================
# ENROLLMENT FORMS - UPDATED
# ==========================================

# FORM FOR ENROLLING STUDENTS BY EMAIL (EDUCATOR)
class EnrollByEmailForm(FlaskForm):
    student_email = StringField("Student Email",
                                validators=[DataRequired(), Email()])
    submit = SubmitField("Enroll Student")

# FORM FOR STUDENTS TO JOIN COURSE BY CODE
class JoinCourseForm(FlaskForm):
    enrollment_code = StringField("Course Code",
                                  validators=[
                                      DataRequired(),
                                      Length(min=8, max=8, message="Course code must be 8 characters")
                                  ])
    submit = SubmitField("Join Course")

# ==========================================
# CONTACT FORM
# ==========================================

# FORM FOR CONTACT PAGE
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField("Send Message")