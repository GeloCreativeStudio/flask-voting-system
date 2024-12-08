from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.core.forms import CandidateForm, PositionForm, CourseForm, AdminLoginForm
from app.core.models import Candidate, Position, Course, Vote, Voter, Admin
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('core.vote'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get total voters and votes
    total_voters = Voter.query.count()
    total_votes = Vote.query.count()
    turnout_percentage = (total_votes / total_voters * 100) if total_voters > 0 else 0

    # Get positions and candidates
    positions = Position.query.all()
    total_positions = len(positions)
    total_candidates = Candidate.query.count()

    # Get position statistics
    position_stats = []
    for position in positions:
        candidates = Candidate.query.filter_by(position_id=position.id).all()
        votes = Vote.query.filter_by(position_id=position.id).count()
        position_stats.append({
            'position': position,
            'candidates': len(candidates),
            'votes': votes,
            'turnout': (votes / total_voters * 100) if total_voters > 0 else 0
        })

    # Get recent votes
    recent_votes = Vote.query.order_by(Vote.timestamp.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_voters=total_voters,
                         total_votes=total_votes,
                         turnout_percentage=turnout_percentage,
                         total_positions=total_positions,
                         total_candidates=total_candidates,
                         position_stats=position_stats,
                         recent_votes=recent_votes)

@admin_bp.route('/candidates', methods=['GET', 'POST'])
@login_required
@admin_required
def candidates():
    form = CandidateForm()
    edit_form = CandidateForm()  # Create separate form for editing
    form.position.choices = [(p.id, p.title) for p in Position.query.all()]
    edit_form.position.choices = [(p.id, p.title) for p in Position.query.all()]
    
    if form.validate_on_submit():
        candidate = Candidate(
            name=form.name.data,
            platform=form.platform.data,
            position_id=form.position.data
        )
        db.session.add(candidate)
        db.session.commit()
        flash('Candidate added successfully!', 'success')
        return redirect(url_for('admin.candidates'))
        
    candidates = Candidate.query.all()
    return render_template('admin/candidates.html', form=form, edit_form=edit_form, candidates=candidates)

@admin_bp.route('/candidates/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def candidates_delete(id):
    candidate = Candidate.query.get_or_404(id)
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted successfully!', 'success')
    return redirect(url_for('admin.candidates'))

@admin_bp.route('/candidates/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def candidates_edit(id):
    candidate = Candidate.query.get_or_404(id)
    form = CandidateForm()
    # Populate position choices before validation
    form.position.choices = [(p.id, p.title) for p in Position.query.all()]
    
    if form.validate_on_submit():
        candidate.name = form.name.data
        candidate.platform = form.platform.data
        candidate.position_id = form.position.data
        db.session.commit()
        flash('Candidate updated successfully!', 'success')
    else:
        # Populate form with existing data if validation fails
        form.name.data = candidate.name
        form.platform.data = candidate.platform
        form.position.data = candidate.position_id
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('admin.candidates'))

@admin_bp.route('/positions', methods=['GET', 'POST'])
@login_required
@admin_required
def positions():
    form = PositionForm()
    edit_form = PositionForm()  # Create separate form for editing
    
    if form.validate_on_submit():
        position = Position(
            title=form.title.data,
            max_winners=form.max_winners.data
        )
        db.session.add(position)
        db.session.commit()
        flash('Position added successfully!', 'success')
        return redirect(url_for('admin.positions'))
        
    positions = Position.query.all()
    return render_template('admin/positions.html', form=form, edit_form=edit_form, positions=positions)

@admin_bp.route('/positions/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def positions_delete(id):
    position = Position.query.get_or_404(id)
    db.session.delete(position)
    db.session.commit()
    flash('Position deleted successfully!', 'success')
    return redirect(url_for('admin.positions'))

@admin_bp.route('/positions/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def positions_edit(id):
    position = Position.query.get_or_404(id)
    form = PositionForm(obj=position)
    if form.validate_on_submit():
        position.title = form.title.data
        position.max_winners = form.max_winners.data
        db.session.commit()
        flash('Position updated successfully!', 'success')
    return redirect(url_for('admin.positions'))

@admin_bp.route('/courses', methods=['GET', 'POST'])
@login_required
@admin_required
def courses():
    form = CourseForm()
    edit_form = CourseForm()  # Create separate form for editing
    
    if form.validate_on_submit():
        course = Course(
            name=form.name.data,
            code=form.code.data
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin.courses'))
        
    courses = Course.query.all()
    return render_template('admin/courses.html', form=form, edit_form=edit_form, courses=courses)

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def courses_delete(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/courses/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def courses_edit(id):
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.name = form.name.data
        course.code = form.code.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/results')
@login_required
@admin_required
def results():
    positions = Position.query.all()
    results = {}
    
    for position in positions:
        candidates = Candidate.query.filter_by(position_id=position.id).all()
        votes = []
        for candidate in candidates:
            vote_count = Vote.query.filter_by(candidate_id=candidate.id).count()
            votes.append({
                'candidate': candidate,
                'votes': vote_count
            })
        # Sort by vote count in descending order
        votes.sort(key=lambda x: x['votes'], reverse=True)
        results[position] = votes
        
    return render_template('admin/results.html', results=results)

@admin_bp.route('/voters')
@login_required
@admin_required
def voters():
    voters = Voter.query.all()
    return render_template('admin/voters.html', voters=voters)
