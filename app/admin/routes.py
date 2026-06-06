from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, date, timedelta
from app import db
from app.admin import admin
from sqlalchemy import func
from app.models import User, Menu, MenuItem, AttendanceConfirmation, Notification

DEFAULT_PASSWORD = 'Ueab@2026'


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return f(*args, **kwargs)
    return decorated


def admin_or_staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('admin', 'staff'):
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/dashboard')
@login_required
@admin_or_staff_required
def dashboard():
    today = date.today()
    return render_template('admin/dashboard.html',
        total_students=User.query.filter_by(role='student').count(),
        total_staff=User.query.filter_by(role='staff').count(),
        today_menus=Menu.query.filter_by(date=today).count(),
        today_confirmations=(
            AttendanceConfirmation.query
            .join(Menu)
            .filter(Menu.date == today)
            .count()
        ),
        today=today,
    )


@admin.route('/users')
@login_required
@admin_or_staff_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_or_staff_required
def toggle_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('Cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/role/<int:user_id>', methods=['POST'])
@login_required
@admin_or_staff_required
def change_role(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('Cannot change your own role.', 'danger')
        return redirect(url_for('admin.users'))
    new_role = request.form.get('role')
    if new_role in ('student', 'staff', 'admin'):
        user.role = new_role
        db.session.commit()
        flash(f'Role updated to {new_role}.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_or_staff_required
def add_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        student_id = request.form.get('student_id', '').strip() or None
        role = request.form.get('role', 'student')
        if role not in ('student', 'staff', 'admin'):
            role = 'student'

        # Staff can only add students
        if current_user.role == 'staff' and role != 'student':
            role = 'student'

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return render_template('admin/add_student.html')

        if User.query.filter_by(email=email).first():
            flash('A user with that email already exists.', 'danger')
            return render_template('admin/add_student.html')

        if student_id and User.query.filter_by(student_id=student_id).first():
            flash('That Student ID is already taken.', 'danger')
            return render_template('admin/add_student.html')

        new_user = User(
            name=name,
            email=email,
            student_id=student_id if role == 'student' else None,
            role=role,
            must_change_password=True,
        )
        new_user.set_password(DEFAULT_PASSWORD)
        db.session.add(new_user)
        db.session.commit()

        flash(
            f'{role.capitalize()} "{name}" added. Default password: {DEFAULT_PASSWORD} '
            f'— they will be required to change it on first login.',
            'success'
        )
        return redirect(url_for('admin.users'))

    return render_template('admin/add_student.html')


@admin.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_or_staff_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{name}" has been permanently deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_or_staff_required
def reset_password(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('Cannot reset your own password this way.', 'danger')
        return redirect(url_for('admin.users'))
    user.set_password(DEFAULT_PASSWORD)
    user.must_change_password = True
    db.session.commit()
    flash(
        f'Password for {user.name} has been reset to the default ({DEFAULT_PASSWORD}). '
        f'They will be required to change it on next login.',
        'success'
    )
    return redirect(url_for('admin.users'))


@admin.route('/menus')
@login_required
@admin_or_staff_required
def menus():
    all_menus = Menu.query.order_by(Menu.date.desc(), Menu.meal_type).all()
    return render_template('admin/menus.html', menus=all_menus)


@admin.route('/menus/add', methods=['GET', 'POST'])
@login_required
@admin_or_staff_required
def add_menu():
    if request.method == 'POST':
        try:
            menu_date = datetime.strptime(request.form.get('date', ''), '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/add_menu.html', today=date.today())

        meal_type = request.form.get('meal_type')
        description = request.form.get('description', '').strip()
        item_names = request.form.getlist('items[]')

        if Menu.query.filter_by(date=menu_date, meal_type=meal_type).first():
            flash(f'A {meal_type} menu already exists for {menu_date}.', 'danger')
            return render_template('admin/add_menu.html', today=date.today())

        menu = Menu(date=menu_date, meal_type=meal_type, description=description)
        db.session.add(menu)
        db.session.flush()

        for name in item_names:
            if name.strip():
                db.session.add(MenuItem(menu_id=menu.id, name=name.strip()))

        db.session.commit()
        flash('Menu added successfully.', 'success')
        return redirect(url_for('admin.menus'))

    return render_template('admin/add_menu.html', today=date.today())


@admin.route('/menus/edit/<int:menu_id>', methods=['GET', 'POST'])
@login_required
@admin_or_staff_required
def edit_menu(menu_id):
    menu = db.get_or_404(Menu, menu_id)
    if request.method == 'POST':
        try:
            menu_date = datetime.strptime(request.form.get('date', ''), '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/edit_menu.html', menu=menu)

        meal_type = request.form.get('meal_type')
        description = request.form.get('description', '').strip()
        item_names = request.form.getlist('items[]')

        conflict = Menu.query.filter(
            Menu.date == menu_date,
            Menu.meal_type == meal_type,
            Menu.id != menu_id
        ).first()
        if conflict:
            flash(f'A {meal_type} menu already exists for {menu_date}.', 'danger')
            return render_template('admin/edit_menu.html', menu=menu)

        menu.date = menu_date
        menu.meal_type = meal_type
        menu.description = description

        MenuItem.query.filter_by(menu_id=menu.id).delete()
        db.session.flush()
        for name in item_names:
            if name.strip():
                db.session.add(MenuItem(menu_id=menu.id, name=name.strip()))

        db.session.commit()
        flash('Menu updated successfully.', 'success')
        return redirect(url_for('admin.menus'))

    return render_template('admin/edit_menu.html', menu=menu)


@admin.route('/menus/delete/<int:menu_id>', methods=['POST'])
@login_required
@admin_or_staff_required
def delete_menu(menu_id):
    menu = db.get_or_404(Menu, menu_id)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu deleted.', 'success')
    return redirect(url_for('admin.menus'))


@admin.route('/notify', methods=['GET', 'POST'])
@login_required
@admin_or_staff_required
def send_notification():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()

        if not title or not message:
            flash('Title and message are required.', 'danger')
            return redirect(url_for('admin.send_notification'))

        students = User.query.filter_by(role='student', is_active=True).all()
        for user in students:
            db.session.add(Notification(user_id=user.id, title=title, message=message))
        db.session.commit()

        flash(f'Notification sent to {len(students)} student(s).', 'success')
        return redirect(url_for('admin.send_notification'))

    recent = (
        db.session.query(
            Notification.title,
            Notification.message,
            func.max(Notification.created_at).label('sent_at'),
            func.count(Notification.id).label('recipients'),
        )
        .group_by(Notification.title, Notification.message)
        .order_by(func.max(Notification.created_at).desc())
        .limit(5)
        .all()
    )
    return render_template('admin/notify.html', recent=recent)


@admin.route('/students')
@login_required
@admin_or_staff_required
def students():
    all_students = User.query.filter_by(role='student').order_by(User.name).all()
    return render_template('admin/students.html', students=all_students)


@admin.route('/menus/weekly', methods=['GET', 'POST'])
@login_required
@admin_or_staff_required
def weekly_menu():
    week_start_str = request.args.get('week_start')
    try:
        week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    meal_types = ['breakfast', 'lunch', 'dinner']

    if request.method == 'POST':
        created = 0
        skipped = 0
        for d in week_dates:
            for meal in meal_types:
                key = f"{d.isoformat()}_{meal}"
                description = request.form.get(f'desc_{key}', '').strip()
                items_raw = request.form.get(f'items_{key}', '').strip()

                if not description and not items_raw:
                    continue

                if Menu.query.filter_by(date=d, meal_type=meal).first():
                    skipped += 1
                    continue

                menu = Menu(date=d, meal_type=meal, description=description)
                db.session.add(menu)
                db.session.flush()

                for item_name in items_raw.split(','):
                    item_name = item_name.strip()
                    if item_name:
                        db.session.add(MenuItem(menu_id=menu.id, name=item_name))
                created += 1

        db.session.commit()
        msg = f'{created} menu(s) created.'
        if skipped:
            msg += f' {skipped} slot(s) skipped (already exist).'
        flash(msg, 'success' if created else 'warning')
        return redirect(url_for('admin.weekly_menu', week_start=week_start.isoformat()))

    existing_menus = {
        (m.date, m.meal_type): m
        for m in Menu.query.filter(Menu.date.in_(week_dates)).all()
    }
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    return render_template('admin/weekly_menu.html',
        week_dates=week_dates,
        meal_types=meal_types,
        existing_menus=existing_menus,
        week_start=week_start,
        prev_week=prev_week,
        next_week=next_week,
    )
