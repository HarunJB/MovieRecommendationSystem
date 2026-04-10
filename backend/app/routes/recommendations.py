from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/dashboard')
@login_required
def dashboard():
    if not current_user.onboarding_complete:
        from flask import redirect, url_for
        return redirect(url_for('auth.onboarding'))
    return render_template('dashboard.html')

@recommendations.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@recommendations.route('/api/recommendations')
@login_required
def get_recommendations():
    return jsonify({'recommendations': []})
