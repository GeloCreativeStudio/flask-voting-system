from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.core.forms import VoterLoginForm, VoterRegistrationForm
from app.core.models import Voter, Course
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.vote'))
    
    form = VoterLoginForm()
    if form.validate_on_submit():
        voter = Voter.query.filter_by(student_id=form.student_id.data).first()
        if voter and voter.check_password(form.password.data):
            login_user(voter)
            return redirect(url_for('core.vote'))
        flash('Invalid student ID or password', 'error')
    
    return render_template('auth/login.html', voter_form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    
    form = VoterRegistrationForm()
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.order_by('name').all()]
    
    if form.validate_on_submit():
        voter = Voter(
            student_id=form.student_id.data,
            name=form.name.data,
            email=form.email.data,
            course_id=form.course_id.data,
            gender=form.gender.data
        )
        voter.set_password(form.password.data)
        
        db.session.add(voter)
        try:
            db.session.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint' in str(e):
                if 'student_id' in str(e):
                    flash('Student ID already registered.', 'error')
                elif 'email' in str(e):
                    flash('Email already registered.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
