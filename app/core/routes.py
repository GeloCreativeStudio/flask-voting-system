from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.core.models import Position, Candidate, Vote, Voter
from app import db

core_bp = Blueprint('core', __name__)

@core_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('core.vote'))
    return render_template('core/index.html')

@core_bp.route('/vote')
@login_required
def vote():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if current_user.has_voted:
        flash('You have already cast your vote.', 'info')
        return redirect(url_for('core.results'))
    
    positions = Position.query.all()
    candidates = {pos.id: Candidate.query.filter_by(position_id=pos.id).all() 
                 for pos in positions}
    return render_template('core/vote.html', 
                         positions=positions,
                         candidates=candidates)

@core_bp.route('/cast_vote', methods=['POST'])
@login_required
def cast_vote():
    if current_user.is_admin or current_user.has_voted:
        return jsonify({'status': 'error', 'message': 'Invalid voting attempt'}), 400
    
    try:
        votes = request.get_json()
        if not votes:
            return jsonify({'status': 'error', 'message': 'No votes received'}), 400
        
        # Validate votes
        positions = Position.query.all()
        position_ids = {str(p.id): p for p in positions}
        
        for position_id, candidate_id in votes.items():
            if position_id not in position_ids:
                return jsonify({'status': 'error', 'message': 'Invalid position'}), 400
                
            candidate = Candidate.query.get(candidate_id)
            if not candidate or str(candidate.position_id) != position_id:
                return jsonify({'status': 'error', 'message': 'Invalid candidate'}), 400
            
            vote = Vote(
                voter_id=current_user.id,
                candidate_id=candidate_id,
                position_id=position_ids[position_id].id
            )
            db.session.add(vote)
        
        # Mark voter as having voted
        current_user.has_voted = True
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Vote cast successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@core_bp.route('/results')
@login_required
def results():
    if not current_user.has_voted and not current_user.is_admin:
        flash('You must cast your vote first to view results.', 'warning')
        return redirect(url_for('core.vote'))
    
    positions = Position.query.all()
    results = {}
    total_voters = Voter.query.count()
    total_votes = Vote.query.filter_by(position_id=positions[0].id if positions else 0).count()
    
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
        
    return render_template('core/results.html', 
                         results=results,
                         total_voters=total_voters,
                         total_votes=total_votes)

@core_bp.route('/thank_you')
@login_required
def thank_you():
    if not current_user.has_voted:
        return redirect(url_for('core.vote'))
    return render_template('core/thank_you.html')
