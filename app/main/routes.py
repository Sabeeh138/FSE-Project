from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    return render_template('main/home.html', title='Home')

@main.route('/about')
def about():
    return render_template('main/about.html', title='About')

@main.route('/dashboard')
@login_required
def dashboard():
    # Redirect to role-specific dashboard
    if current_user.role == 'doctor':
        return redirect(url_for('doctors.dashboard'))
    elif current_user.role == 'nurse':
        return redirect(url_for('nurses.dashboard'))
    elif current_user.role == 'receptionist':
        return redirect(url_for('receptionists.dashboard'))
    elif current_user.role == 'store_manager':
        return redirect(url_for('store.dashboard'))
    else:
        return render_template('main/dashboard.html', title='Dashboard')