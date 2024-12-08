from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.core.models import Admin, Voter

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VoterRegistrationForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired(), Length(min=4, max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_student_id(self, field):
        if Voter.query.filter_by(student_id=field.data).first():
            raise ValidationError('Student ID already registered.')

    def validate_email(self, field):
        if Voter.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class VoterLoginForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CandidateForm(FlaskForm):
    name = StringField('Candidate Name', validators=[DataRequired(), Length(max=100)])
    platform = TextAreaField('Platform', validators=[DataRequired()])
    position = SelectField('Position', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit Candidate')

class PositionForm(FlaskForm):
    title = StringField('Position Title', validators=[DataRequired(), Length(max=50)])
    max_winners = SelectField('Maximum Winners', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (12, '12')], coerce=int)
    submit = SubmitField('Submit Position')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Course Code', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Submit Course')
