"""
Seed script — creates demo accounts and sample menus.

Run once after db.create_all():
    python seed.py

Demo accounts created:
    Admin   : admin@ueab.ac.ke        / Admin@Ueab2026!
    Staff   : staff@ueab.ac.ke        / Staff@Ueab2026!
    Student : faith.chepchumba@ueab.ac.ke  / (default → must change on login)
    Student : john.kamau@ueab.ac.ke        / (default → must change on login)
    Student : mary.wanjiku@ueab.ac.ke      / (default → must change on login)
"""

from datetime import date, timedelta
from app import create_app, db
from app.models import User, Menu, MenuItem

DEFAULT_PASSWORD = 'Ueab@2026'

app = create_app()

with app.app_context():
    db.create_all()

    # ── Guard: skip if already seeded ────────────────────────────────────────
    if User.query.count() > 0:
        print('Database already has users — skipping seed to avoid duplicates.')
        print('To re-seed, drop the database and run this script again.')
        exit(0)

    # ── Users ─────────────────────────────────────────────────────────────────
    admin = User(name='System Admin', email='admin@ueab.ac.ke', role='admin')
    admin.set_password('Admin@Ueab2026!')

    staff = User(name='Cafeteria Staff', email='staff@ueab.ac.ke', role='staff')
    staff.set_password('Staff@Ueab2026!')

    students = [
        User(name='Faith Chepchumba', email='faith.chepchumba@ueab.ac.ke',
             student_id='SCHEFA2312', role='student', must_change_password=True),
        User(name='John Kamau',       email='john.kamau@ueab.ac.ke',
             student_id='SCJKAM2301', role='student', must_change_password=True),
        User(name='Mary Wanjiku',     email='mary.wanjiku@ueab.ac.ke',
             student_id='SCMWAN2305', role='student', must_change_password=True),
    ]
    for s in students:
        s.set_password(DEFAULT_PASSWORD)

    db.session.add_all([admin, staff] + students)

    # ── Sample menus (today + next 2 days) ────────────────────────────────────
    today = date.today()
    meal_plan = [
        # (day offset, meal_type, description, [items])
        (0, 'breakfast', 'Monday Breakfast',
            ['Mandazi', 'Tea', 'Porridge']),
        (0, 'lunch',     'Monday Lunch',
            ['Ugali', 'Beef stew', 'Kachumbari', 'Sukuma wiki']),
        (0, 'dinner',    'Monday Dinner',
            ['Rice', 'Beans', 'Fried cabbage']),

        (1, 'breakfast', 'Tuesday Breakfast',
            ['Chapati', 'Eggs', 'Milk tea']),
        (1, 'lunch',     'Tuesday Lunch',
            ['Githeri', 'Avocado', 'Juice']),
        (1, 'dinner',    'Tuesday Dinner',
            ['Ugali', 'Fish', 'Spinach']),

        (2, 'breakfast', 'Wednesday Breakfast',
            ['Bread', 'Butter', 'Tea', 'Fruit']),
        (2, 'lunch',     'Wednesday Lunch',
            ['White rice', 'Chicken curry', 'Salad']),
        (2, 'dinner',    'Wednesday Dinner',
            ['Ugali', 'Lentil soup', 'Cabbage']),
    ]

    for offset, meal_type, description, items in meal_plan:
        menu = Menu(
            date=today + timedelta(days=offset),
            meal_type=meal_type,
            description=description,
        )
        db.session.add(menu)
        db.session.flush()
        for item_name in items:
            db.session.add(MenuItem(menu_id=menu.id, name=item_name))

    db.session.commit()

    print('\nDatabase seeded successfully!\n')
    print('  Role     Email                           Password')
    print('  -------  ------------------------------  -----------------')
    print('  Admin    admin@ueab.ac.ke                Admin@Ueab2026!')
    print('  Staff    staff@ueab.ac.ke                Staff@Ueab2026!')
    print('  Student  faith.chepchumba@ueab.ac.ke     Ueab@2026  (must change)')
    print('  Student  john.kamau@ueab.ac.ke           Ueab@2026  (must change)')
    print('  Student  mary.wanjiku@ueab.ac.ke         Ueab@2026  (must change)')
    print()
