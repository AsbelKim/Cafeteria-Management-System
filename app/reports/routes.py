import csv
import io
from flask import render_template, redirect, url_for, flash, make_response, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, timedelta
from sqlalchemy import func
from app import db
from app.reports import reports
from app.models import Menu, AttendanceConfirmation, User, MenuItem


def staff_or_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('staff', 'admin'):
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def _csv_response(filename, headers, rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@reports.route('/')
@login_required
@staff_or_admin
def index():
    today = date.today()
    week_ago = today - timedelta(days=6)

    daily_rows = (
        db.session.query(Menu.date, Menu.meal_type, func.count(AttendanceConfirmation.id))
        .outerjoin(AttendanceConfirmation, Menu.id == AttendanceConfirmation.menu_id)
        .filter(Menu.date >= week_ago, Menu.date <= today)
        .group_by(Menu.date, Menu.meal_type)
        .order_by(Menu.date)
        .all()
    )

    dates = [(week_ago + timedelta(days=i)).strftime('%b %d') for i in range(7)]
    chart_data = {'breakfast': [0]*7, 'lunch': [0]*7, 'dinner': [0]*7}
    for row_date, meal_type, count in daily_rows:
        delta = (row_date - week_ago).days
        if 0 <= delta < 7 and meal_type in chart_data:
            chart_data[meal_type][delta] = count

    meal_totals = dict(
        db.session.query(Menu.meal_type, func.count(AttendanceConfirmation.id))
        .outerjoin(AttendanceConfirmation, Menu.id == AttendanceConfirmation.menu_id)
        .group_by(Menu.meal_type)
        .all()
    )

    total_students = User.query.filter_by(role='student', is_active=True).count()
    total_confirmations = AttendanceConfirmation.query.count()

    top_attendees = (
        db.session.query(User, func.count(AttendanceConfirmation.id).label('total'))
        .join(AttendanceConfirmation, User.id == AttendanceConfirmation.user_id)
        .filter(User.role == 'student')
        .group_by(User.id)
        .order_by(func.count(AttendanceConfirmation.id).desc())
        .limit(10)
        .all()
    )

    return render_template('reports/index.html',
        dates=dates,
        chart_data=chart_data,
        meal_totals=meal_totals,
        total_students=total_students,
        total_confirmations=total_confirmations,
        top_attendees=top_attendees,
        today=today,
    )


# ── Download: full attendance report (admin/staff) ────────────────────────────
@reports.route('/download/attendance')
@login_required
@staff_or_admin
def download_attendance():
    rows = (
        db.session.query(
            Menu.date, Menu.meal_type,
            User.name, User.student_id, User.email,
            AttendanceConfirmation.confirmed_at
        )
        .join(Menu, AttendanceConfirmation.menu_id == Menu.id)
        .join(User, AttendanceConfirmation.user_id == User.id)
        .order_by(Menu.date.desc(), Menu.meal_type, User.name)
        .all()
    )

    headers = ['Date', 'Meal Type', 'Student Name', 'Student ID', 'Email', 'Confirmed At']
    data = [
        [str(r.date), r.meal_type, r.name, r.student_id or '', r.email,
         r.confirmed_at.strftime('%Y-%m-%d %H:%M')]
        for r in rows
    ]
    filename = f'attendance_report_{date.today()}.csv'
    return _csv_response(filename, headers, data)


# ── Download: today's confirmed attendance (admin/staff) ──────────────────────
@reports.route('/download/today')
@login_required
@staff_or_admin
def download_today():
    today = date.today()
    rows = (
        db.session.query(
            Menu.meal_type, User.name, User.student_id, User.email,
            AttendanceConfirmation.confirmed_at
        )
        .join(Menu, AttendanceConfirmation.menu_id == Menu.id)
        .join(User, AttendanceConfirmation.user_id == User.id)
        .filter(Menu.date == today)
        .order_by(Menu.meal_type, User.name)
        .all()
    )

    headers = ['Meal Type', 'Student Name', 'Student ID', 'Email', 'Confirmed At']
    data = [
        [r.meal_type, r.name, r.student_id or '', r.email,
         r.confirmed_at.strftime('%H:%M')]
        for r in rows
    ]
    filename = f'attendance_today_{today}.csv'
    return _csv_response(filename, headers, data)


# ── Download: menu schedule (admin/staff) ─────────────────────────────────────
@reports.route('/download/menus')
@login_required
@staff_or_admin
def download_menus():
    menus = Menu.query.order_by(Menu.date.desc(), Menu.meal_type).all()

    headers = ['Date', 'Meal Type', 'Description', 'Items', 'Confirmations']
    data = [
        [
            str(m.date),
            m.meal_type,
            m.description or '',
            ', '.join(i.name for i in m.items),
            m.confirmed_count()
        ]
        for m in menus
    ]
    filename = f'menu_schedule_{date.today()}.csv'
    return _csv_response(filename, headers, data)


# ── Download: user list (admin only) ─────────────────────────────────────────
@reports.route('/download/users')
@login_required
@admin_required
def download_users():
    users = User.query.order_by(User.role, User.name).all()

    headers = ['Name', 'Email', 'Student ID', 'Role', 'Status', 'Date Joined']
    data = [
        [u.name, u.email, u.student_id or '', u.role,
         'Active' if u.is_active else 'Inactive',
         u.created_at.strftime('%Y-%m-%d')]
        for u in users
    ]
    filename = f'user_list_{date.today()}.csv'
    return _csv_response(filename, headers, data)
