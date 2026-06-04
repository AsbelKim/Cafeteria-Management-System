-- Cafeteria Attendance & Meal Management System
-- University of Eastern Africa, Baraton
-- INSY 492 Senior Project — Chepchumba Faith

CREATE DATABASE IF NOT EXISTS cafeteria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cafeteria_db;

-- SQLAlchemy creates these via db.create_all(); this file is for reference / manual setup

CREATE TABLE IF NOT EXISTS users (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(100)  NOT NULL,
    email               VARCHAR(120)  NOT NULL UNIQUE,
    student_id          VARCHAR(20)   UNIQUE,
    password_hash       VARCHAR(256)  NOT NULL,
    role                ENUM('student','staff','admin') NOT NULL DEFAULT 'student',
    is_active           BOOLEAN       NOT NULL DEFAULT TRUE,
    must_change_password BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS menus (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    meal_type   ENUM('breakfast','lunch','dinner') NOT NULL,
    description TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_menu_date_meal (date, meal_type)
);

CREATE TABLE IF NOT EXISTS menu_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    menu_id     INT NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance_confirmations (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    menu_id      INT NOT NULL,
    confirmed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attended     BOOLEAN  NOT NULL DEFAULT FALSE,
    UNIQUE KEY uq_user_menu (user_id, menu_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    title      VARCHAR(100) NOT NULL,
    message    TEXT         NOT NULL,
    is_read    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_reset_codes (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT         NOT NULL,
    code       VARCHAR(6)  NOT NULL,
    expires_at DATETIME    NOT NULL,
    used       BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- NOTE: Do NOT insert the admin account here with a hardcoded hash.
--       Run seed.py instead — it generates a proper hash at runtime.
