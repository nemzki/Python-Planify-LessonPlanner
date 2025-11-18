from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=3, max=20)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    contact_number = StringField("Contact number", validators=[DataRequired(), Length(min=11, max=11, message="Contact number must be 11 digits"), Regexp(r'^[0-9]*$', message = "Contact number must contain only digits" )])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=6), EqualTo('password', message="Passwords must match")])
    role = SelectField("Role",
    choices=[("educator", "Educator"), ("student", "Student")],
    validators=[DataRequired()])
    submit = SubmitField("Register")