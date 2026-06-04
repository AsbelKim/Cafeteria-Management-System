from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.staff import staff
from app.models import Menu, AttendanceConfirmation, User
from datetime import date


def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('staff', 'admin'):
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return f(*args, **kwargs)
    return decorated


@staff.route('/dashboard')
@login_required
@staff_required
def dashboard():
    today = date.today()
    menus = Menu.query.filter_by(date=today).order_by(Menu.meal_type).all()
    meal_data = [
        {'menu': m, 'confirmed': AttendanceConfirmation.query.filter_by(menu_id=m.id).count()}
        for m in menus
    ]
    return render_template('staff/dashboard.html', meal_data=meal_data, today=today)


@staff.route('/attendance/<int:menu_id>')
@login_required
@staff_required
def attendance_detail(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    confirmations = AttendanceConfirmation.query.filter_by(menu_id=menu_id).all()
    data = [(c, db.session.get(User, c.user_id)) for c in confirmations]
    data = [(c, u) for c, u in data if u is not None]
    attended_count = sum(1 for c, _ in data if c.attended)
    return render_template('staff/attendance_detail.html',
        menu=menu, data=data, attended_count=attended_count)


@staff.route('/mark_attended/<int:confirmation_id>', methods=['POST'])
@login_required
@staff_required
def mark_attended(confirmation_id):
    confirmation = AttendanceConfirmation.query.get_or_404(confirmation_id)
    confirmation.attended = not confirmation.attended
    db.session.commit()
    return redirect(request.referrer or url_for('staff.dashboard'))
