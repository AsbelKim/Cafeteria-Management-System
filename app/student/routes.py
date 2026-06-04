import csv
import io
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.student import student
from app.models import Menu, AttendanceConfirmation, Notification
from datetime import date


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return f(*args, **kwargs)
    return decorated


@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    today = date.today()
    menus = Menu.query.filter_by(date=today).order_by(Menu.meal_type).all()
    confirmed_ids = {
        a.menu_id for a in AttendanceConfirmation.query.filter_by(user_id=current_user.id).all()
    }
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('student/dashboard.html',
        menus=menus, confirmed_ids=confirmed_ids, today=today, unread_count=unread_count)


@student.route('/menu')
@login_required
@student_required
def view_menu():
    today = date.today()
    upcoming = Menu.query.filter(Menu.date >= today).order_by(Menu.date.asc(), Menu.meal_type).all()
    past = Menu.query.filter(Menu.date < today).order_by(Menu.date.desc(), Menu.meal_type).limit(21).all()
    menus = upcoming + past
    confirmed_ids = {
        a.menu_id for a in AttendanceConfirmation.query.filter_by(user_id=current_user.id).all()
    }
    return render_template('student/menu.html', menus=menus, confirmed_ids=confirmed_ids, today=today)


@student.route('/confirm/<int:menu_id>', methods=['POST'])
@login_required
@student_required
def confirm_attendance(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    if menu.date < date.today():
        return jsonify({'status': 'error', 'message': 'Cannot change confirmation for past meals.'})
    existing = AttendanceConfirmation.query.filter_by(
        user_id=current_user.id, menu_id=menu_id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'cancelled', 'message': 'Attendance cancelled.'})
    db.session.add(AttendanceConfirmation(user_id=current_user.id, menu_id=menu_id))
    db.session.commit()
    return jsonify({'status': 'confirmed', 'message': 'Attendance confirmed!'})


@student.route('/notifications')
@login_required
@student_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('student/notifications.html', notifications=notifs)


@student.route('/reports')
@login_required
@student_required
def download_history():
    records = (
        db.session.query(Menu.date, Menu.meal_type, AttendanceConfirmation.confirmed_at)
        .join(Menu, AttendanceConfirmation.menu_id == Menu.id)
        .filter(AttendanceConfirmation.user_id == current_user.id)
        .order_by(Menu.date.desc(), Menu.meal_type)
        .all()
    )
    total = len(records)
    return render_template('student/reports.html', records=records, total=total)


@student.route('/reports/download')
@login_required
@student_required
def download_history_csv():
    records = (
        db.session.query(Menu.date, Menu.meal_type, AttendanceConfirmation.confirmed_at)
        .join(Menu, AttendanceConfirmation.menu_id == Menu.id)
        .filter(AttendanceConfirmation.user_id == current_user.id)
        .order_by(Menu.date.desc(), Menu.meal_type)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Meal Type', 'Confirmed At'])
    for r in records:
        writer.writerow([str(r.date), r.meal_type, r.confirmed_at.strftime('%Y-%m-%d %H:%M')])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = (
        f'attachment; filename="my_attendance_{current_user.student_id or current_user.id}.csv"'
    )
    return response
