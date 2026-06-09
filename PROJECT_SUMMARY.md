# UEAB Cafeteria Management System
## Senior Project Summary — INSY 492

**Student:** Chepchumba Faith  
**Institution:** University of Eastern Africa, Baraton  
**Course:** INSY 492 — Senior Project  
**Year:** 2026

---

## 1. Project Overview

The UEAB Cafeteria Management System is a full-stack web application that digitizes meal planning and student attendance tracking at the university cafeteria. Before this system, attendance and meal planning were handled manually — making it difficult to forecast how many students would attend a given meal, notify students of menu changes, or generate attendance reports.

The system replaces that manual process with a role-based web portal where:
- **Admins and staff** plan weekly menus, manage user accounts, broadcast notifications, and download attendance reports.
- **Students** view today's meals, confirm or cancel their attendance with one click, receive announcements, and download their personal attendance history.

---

## 2. Problem Statement

The university cafeteria lacked a structured system to:

1. Know in advance how many students intended to attend each meal.
2. Communicate menu changes or announcements to students efficiently.
3. Record and report on attendance trends over time.
4. Manage student accounts and access in one place.

This project addresses all four gaps with a single, unified web system.

---

## 3. Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Allow students to confirm meal attendance online | Achieved |
| 2 | Enable admin/staff to plan daily and weekly menus | Achieved |
| 3 | Send broadcast notifications to all students | Achieved |
| 4 | Generate downloadable attendance and menu reports | Achieved |
| 5 | Enforce role-based access (admin / staff / student) | Achieved |
| 6 | Secure user accounts with strong password policy | Achieved |
| 7 | Deploy the system to a live cloud server | Achieved |

---

## 4. Technologies Used

### Programming Languages

| Language | Where Used |
|----------|------------|
| **Python 3.10+** | Backend application logic, database models, report generation |
| **HTML5** | Page structure and templates (Jinja2) |
| **CSS3** | Custom styling and responsive layout |
| **JavaScript (ES6)** | AJAX attendance confirmation, dynamic greeting, toast notifications, auto-dismiss alerts |
| **SQL** | Database schema definition and queries (via ORM) |

### Frameworks & Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **Flask** | 3.0.3 | Web framework — routing, blueprints, templating |
| **Flask-SQLAlchemy** | 3.1.1 | ORM — Python models mapped to MySQL tables |
| **Flask-Login** | 0.6.3 | Session management, login/logout, `@login_required` |
| **Werkzeug** | (bundled) | Password hashing (PBKDF2-SHA256) |
| **PyMySQL** | 1.1.1 | MySQL database driver |
| **python-dotenv** | 1.0.1 | Load environment variables from `.env` |
| **openpyxl** | 3.1.5 | Generate styled Excel (.xlsx) reports |
| **Pillow** | 10.0+ | Generate watermark image embedded in Excel exports |
| **Gunicorn** | 21.2.0 | Production WSGI server |
| **cryptography** | 42.0.8 | SSL/TLS support for secure database connection |

### Frontend Libraries (CDN)

| Library | Version | Purpose |
|---------|---------|---------|
| **Bootstrap** | 5.3.2 | Responsive layout, components, navbar, cards, modals |
| **Font Awesome** | 6.5.1 | Icons throughout the UI |

### Database

| Component | Technology |
|-----------|------------|
| **RDBMS** | MySQL 8.0 |
| **Charset** | utf8mb4 / utf8mb4_unicode_ci |
| **Cloud DB** | Aiven (managed MySQL, production) |
| **Local DB** | MySQL on localhost (development) |

### Deployment & Infrastructure

| Tool | Purpose |
|------|---------|
| **Render** | Cloud hosting platform (web service) |
| **Aiven** | Managed cloud MySQL with SSL |
| **Netlify + serverless-wsgi** | Alternative serverless deployment target |
| **Gunicorn** | WSGI HTTP server (2 workers, 60s timeout) |
| **GitHub** | Source control and CI/CD trigger for Render |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Git / GitHub** | Version control, collaboration |
| **VS Code** | Primary code editor |
| **Python venv** | Isolated Python environment |
| **curl** | Manual API and route testing |
| **MySQL Workbench** | Database inspection and management |

---

## 5. System Architecture

The application follows the **Model-View-Controller (MVC)** pattern, implemented using Flask's **Blueprint** structure.

```
Browser  ──►  Flask App (run.py)
                   │
          ┌────────┼─────────────────────────┐
          │        │                         │
       Blueprints (Controllers)          Templates (Views)
       ┌──────────┐                      ┌──────────────────┐
       │  auth    │  login / logout       │  auth/           │
       │  student │  dashboard / confirm  │  student/        │
       │  staff   │  attendance detail    │  staff/          │
       │  admin   │  users / menus        │  admin/          │
       │  reports │  charts / downloads   │  reports/        │
       └──────────┘                      └──────────────────┘
                │
           Models (app/models.py)
           SQLAlchemy ORM
                │
           MySQL Database
```

### Blueprint URL Prefixes

| Blueprint | URL Prefix | Access Level |
|-----------|------------|--------------|
| `auth` | `/auth` | Public |
| `student` | `/student` | Students only |
| `staff` | `/staff` | Staff + Admin |
| `admin` | `/admin` | Staff + Admin |
| `reports` | `/reports` | Staff + Admin |

---

## 6. Project File Structure

```
Cafeteria-Management-System/
│
├── app/
│   ├── __init__.py            # App factory, blueprint registration
│   ├── config.py              # DB URI, secret key, SSL config
│   ├── models.py              # SQLAlchemy models
│   │
│   ├── auth/
│   │   ├── __init__.py        # Blueprint definition
│   │   └── routes.py          # Login, logout, change-password
│   │
│   ├── student/
│   │   ├── __init__.py
│   │   └── routes.py          # Dashboard, menu, confirm, notifications, reports
│   │
│   ├── staff/
│   │   ├── __init__.py
│   │   └── routes.py          # Staff dashboard, attendance detail, mark attended
│   │
│   ├── admin/
│   │   ├── __init__.py
│   │   └── routes.py          # Users, menus, weekly planner, notifications
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   └── routes.py          # Charts, xlsx/csv downloads, watermark generator
│   │
│   ├── static/
│   │   ├── css/style.css      # Custom stylesheet (CSS variables, responsive)
│   │   └── js/main.js         # Toast helper, alert auto-dismiss
│   │
│   └── templates/
│       ├── base.html          # Base layout (navbar, footer, flash messages)
│       ├── auth/              # login, change_password, profile_change_password, register
│       ├── student/           # dashboard, menu, notifications, reports
│       ├── staff/             # dashboard, attendance_detail
│       ├── admin/             # dashboard, users, students, menus, weekly_menu, notify, add_menu, edit_menu, add_student
│       └── reports/           # index (charts + downloads)
│
├── run.py                     # Entry point — create app + start server
├── schema.sql                 # Reference SQL schema for manual DB setup
├── seed.py                    # Seeds demo users and sample menus
├── requirements.txt           # Python dependencies
├── render.yaml                # Render cloud deployment config
├── netlify.toml               # Netlify serverless config
├── Procfile                   # Gunicorn start command
├── runtime.txt                # Python version pin
└── .env                       # Environment variables (not committed)
```

---

## 7. Database Design

The system uses six relational tables:

### Entity-Relationship Overview

```
users ──────────────── attendance_confirmations ──────── menus
  │                                                        │
  │  (one user → many notifications)                       │  (one menu → many menu_items)
  │                                                        │
notifications                                          menu_items

users ── password_reset_codes
```

### Tables

#### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK | Auto-increment |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(120) | Unique, used as login |
| student_id | VARCHAR(20) | Unique, nullable (staff/admin have none) |
| password_hash | VARCHAR(256) | PBKDF2-SHA256 via Werkzeug |
| role | ENUM | `student` / `staff` / `admin` |
| is_active | BOOLEAN | Deactivated users cannot log in |
| must_change_password | BOOLEAN | Forced on first login |

#### `menus`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK | |
| date | DATE | |
| meal_type | ENUM | `breakfast` / `lunch` / `dinner` |
| description | TEXT | Optional short description |
| UNIQUE | (date, meal_type) | One slot per meal per day |

#### `menu_items`
Child rows of `menus`. Each row is one food item (e.g., "Ugali", "Beef stew").

#### `attendance_confirmations`
| Column | Type | Notes |
|--------|------|-------|
| user_id | INT FK → users | |
| menu_id | INT FK → menus | |
| confirmed_at | DATETIME | When the student confirmed |
| attended | BOOLEAN | Staff physically marks this true |
| UNIQUE | (user_id, menu_id) | One confirmation per student per meal |

#### `notifications`
Per-student messages. Admin bulk-sends one message; the system creates one row per active student.

#### `password_reset_codes`
6-digit codes with 15-minute expiry, scaffolded for a future "Forgot Password" flow.

---

## 8. System Modules & Features

### Module 1 — Authentication (`/auth`)
- Email + password login with "Remember me"
- Role-based redirect after login (admin/staff → Admin Dashboard; student → Student Dashboard)
- Strong password policy enforced on all password changes:
  - Minimum 8 characters
  - Must contain uppercase, lowercase, digit, and special character
- Forced first-login password change (default password is invalidated)
- Voluntary password change from profile dropdown

### Module 2 — Student Portal (`/student`)
- **Dashboard** — Shows today's meals with real-time one-click attendance confirmation/cancellation via AJAX (no page reload). Greeting adapts to time of day (Morning / Afternoon / Evening / Night).
- **Menu Browser** — Lists all upcoming and recent past meals grouped by date.
- **Notifications** — Inbox of admin broadcast messages; marks all as read on visit.
- **Attendance Report** — Personal history table of all confirmed meals with CSV download.

### Module 3 — Staff Panel (`/staff`)
- **Dashboard** — Today's meals with confirmation counts per meal.
- **Attendance Detail** — Lists every student who confirmed a specific meal; staff can toggle the "physically attended" checkbox for each student.

### Module 4 — Admin Panel (`/admin`)
- **Dashboard** — Live stats: total students, staff, today's menus, today's confirmations.
- **User Management** — View all users; activate/deactivate accounts; change roles; reset passwords to default; delete accounts.
- **Add User** — Create student, staff, or admin accounts (staff can only create students).
- **Menu Management** — Add, edit, and delete individual meal entries with food items.
- **Weekly Planner** — Plan an entire week's meals (21 slots) in a single form submission.
- **Notifications** — Broadcast a titled message to all active students at once; shows recent notification history.

### Module 5 — Reports (`/reports`)
- **Dashboard** — Line chart (last 7 days, by meal type) and top-10 attendee leaderboard.
- **Attendance Report** (Excel) — All confirmed meals across all students; styled with alternating rows, column auto-fit, and a tiled "UEAB CAFETERIA" watermark image.
- **Today's Attendance** (Excel) — Same format, filtered to today's date.
- **Menu Schedule** (Excel) — All menus with their items and confirmation counts.
- **User List** (Excel, admin only) — Full user roster with roles and status.
- **My Attendance** (CSV, student) — Personal attendance history.

---

## 9. User Roles & Access Control

| Feature | Student | Staff | Admin |
|---------|:-------:|:-----:|:-----:|
| View & confirm today's meals | ✓ | — | — |
| Receive notifications | ✓ | — | — |
| Download personal CSV | ✓ | — | — |
| View staff dashboard | — | ✓ | ✓ |
| Mark student as attended | — | ✓ | ✓ |
| Add / edit / delete menus | — | ✓ | ✓ |
| Weekly menu planner | — | ✓ | ✓ |
| Send notifications to students | — | ✓ | ✓ |
| View attendance reports / charts | — | ✓ | ✓ |
| Download Excel reports | — | ✓ | ✓ |
| Manage user accounts | — | ✓ | ✓ |
| Add students | — | ✓ | ✓ |
| Add staff / admin accounts | — | — | ✓ |
| Download user list (Excel) | — | — | ✓ |

Access is enforced at the route level using Python decorator functions (`@admin_required`, `@admin_or_staff_required`, `@student_required`) — not just hidden links.

---

## 10. Security Features

| Feature | Implementation |
|---------|---------------|
| Password hashing | Werkzeug `generate_password_hash` (PBKDF2-SHA256, salted) |
| Password strength | Server-side regex validation (uppercase, lowercase, digit, special char) |
| Forced password change | `must_change_password` flag checked on every protected route |
| Session management | Flask-Login with signed session cookies (`SECRET_KEY`) |
| Role enforcement | Decorator on every route — no security by obscurity |
| Account deactivation | `is_active=False` prevents login immediately |
| Self-protection | Users cannot deactivate, delete, or change role of their own account |
| SSL database connection | TLS via `cryptography` library for Aiven cloud MySQL |
| Secrets management | All credentials in `.env` file, never committed to git |

---

## 11. UI/UX Design

- **Colour scheme** — UEAB green (`#1a6e3c`) as the primary brand colour, used in navbar, footer, and accents.
- **Responsive** — Bootstrap 5 grid; fully functional on mobile and tablet.
- **Meal type colour coding** — Breakfast (amber), Lunch (green), Dinner (indigo) applied consistently across all views.
- **AJAX confirmation** — Attendance toggle updates instantly without a page reload; uses a spinner while the request is in flight and shows a slide-in toast notification on completion.
- **Time-aware greeting** — Student dashboard greets users by name with Morning / Afternoon / Evening / Night based on their browser's local time.
- **Flash messages** — Auto-dismiss after 5 seconds.
- **Empty states** — Every list page shows a helpful prompt when there is no data.

---

## 12. Deployment

The system supports two production deployment targets:

### Primary — Render + Aiven
| Component | Service |
|-----------|---------|
| Web server | Render (Python web service, Oregon region) |
| Database | Aiven managed MySQL (with SSL/TLS) |
| Process manager | Gunicorn (2 workers, 60s timeout) |
| CI/CD | Push to `main` branch on GitHub triggers auto-deploy on Render |

### Alternative — Netlify (Serverless)
The `netlify.toml` and `netlify/` function configuration wrap the Flask app in `serverless-wsgi` to run as a Netlify Function, enabling a fully serverless deployment.

### Environment Variables
```
SECRET_KEY        — Flask session signing key (auto-generated by Render)
FLASK_DEBUG       — false in production
MYSQL_HOST        — Database host
MYSQL_PORT        — Database port
MYSQL_USER        — Database user
MYSQL_PASSWORD    — Database password
MYSQL_DATABASE    — Database name
MYSQL_SSL_CA      — Path to SSL CA certificate (Aiven)
```

---

## 13. Development Workflow

1. **Local development** — Flask dev server with `FLASK_DEBUG=true`; local MySQL on port 3307.
2. **Database seeding** — `seed.py` creates demo accounts (admin, staff, 3 students) and 9 sample menus spanning 3 days.
3. **Version control** — Git with GitHub remote (`AsbelKim/Cafeteria-Management-System`); all changes committed with descriptive messages.
4. **Testing** — Manual testing of all routes using browser sessions and `curl`; all 5 blueprints and 4 report downloads verified.

---

## 14. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Attendance toggle without page reload | Used JavaScript `fetch()` to POST to the confirm endpoint; updated the card and badge in the DOM on success |
| Styled Excel reports with watermark | Used `openpyxl` for cell formatting + `Pillow` to generate a tiled diagonal watermark PNG embedded as an image in the sheet |
| Server running in UTC, users in Kenya (UTC+3) | Time-based greeting uses `new Date().getHours()` in the browser — always reflects the student's local time |
| Staff vs admin access — same features, different roles | Single `admin_or_staff_required` decorator covers both; only a handful of admin-only routes use the stricter `admin_required` decorator |
| SSL-secured cloud database | `cryptography` library + Aiven CA certificate committed to `certs/ca.pem`; loaded via `MYSQL_SSL_CA` env var |

---

## 15. Future Enhancements

1. **Forgot Password flow** — The `PasswordResetCode` model and 6-digit code logic are already built; the email delivery and verification routes remain to be wired up.
2. **Real-time notifications** — Use WebSockets (Flask-SocketIO) to push meal confirmations and admin notifications live.
3. **Mobile app** — Expose a REST API layer to support an Android/iOS companion app.
4. **Meal feedback / ratings** — Allow students to rate meals after attending; surface average ratings to admin.
5. **Analytics dashboard** — Trend lines over months, peak meal days, and student engagement metrics.

---

## 16. Summary Statistics

| Metric | Value |
|--------|-------|
| Total Python files | 12 |
| Total HTML templates | 20 |
| Database tables | 6 |
| User roles | 3 (student, staff, admin) |
| Protected routes | ~30 |
| Export formats | Excel (.xlsx) + CSV |
| Deployment targets | 2 (Render, Netlify) |
| Lines of CSS | ~280 |
| GitHub commits | 7+ |

---

*UEAB Cafeteria Attendance & Meal Management System — INSY 492 Senior Project, 2026*
