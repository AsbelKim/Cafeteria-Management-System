import re
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth
from app.models import User

DEFAULT_PASSWORD = 'Ueab@2026'


def _validate_password(password):
    """Return an error message if password is too weak, else None."""
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return 'Password must contain at least one lowercase letter.'
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one number.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return 'Password must contain at least one special character (e.g. @, #, !, %).'
    return None


def _dashboard_for(user):
    if user.role in ('admin', 'staff'):
        return url_for('admin.dashboard')
    return url_for('student.dashboard')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            if user.must_change_password:
                flash('You must set a new password before continuing.', 'warning')
                return redirect(url_for('auth.change_password'))
            next_page = request.args.get('next')
            return redirect(next_page or _dashboard_for(user))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        error = _validate_password(new_password)
        if error:
            flash(error, 'danger')
            return render_template('auth/change_password.html')

        if new_password == DEFAULT_PASSWORD:
            flash('You must choose a different password from the default.', 'danger')
            return render_template('auth/change_password.html')

        if new_password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/change_password.html')

        current_user.set_password(new_password)
        current_user.must_change_password = False
        db.session.commit()

        flash('Password updated successfully. Welcome!', 'success')
        return redirect(_dashboard_for(current_user))

    return render_template('auth/change_password.html')


@auth.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def profile_change_password():
    """Voluntary password change — requires current password."""
    if current_user.must_change_password:
        return redirect(url_for('auth.change_password'))

    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not current_user.check_password(current_pw):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/profile_change_password.html')

        error = _validate_password(new_password)
        if error:
            flash(error, 'danger')
            return render_template('auth/profile_change_password.html')

        if new_password != confirm:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/profile_change_password.html')

        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(_dashboard_for(current_user))

    return render_template('auth/profile_change_password.html')


@auth.route('/register')
def register():
    flash('Student accounts are created by the admin or staff. Please contact them to get access.', 'warning')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
