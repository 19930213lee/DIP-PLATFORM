"""
西南交通大学希望学院 · 数字图像处理教学平台
数据库工具模块 —— SQLite 封装
设计 & 技术支持：李康乐
"""

import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'platform.db')


def get_conn():
    """获取数据库连接，自动创建 data 目录"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库表结构"""
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student', 'teacher', 'admin')),
            student_id TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS class_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            FOREIGN KEY (student_id) REFERENCES users(id),
            UNIQUE(class_id, student_id)
        );

        CREATE TABLE IF NOT EXISTS operation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chapter_id TEXT,
            operation_id TEXT,
            operation_name TEXT,
            params_json TEXT,
            image_filename TEXT,
            result_type TEXT CHECK(result_type IN ('success', 'error')),
            error_msg TEXT,
            duration_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS ai_analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            operation_log_id INTEGER,
            analysis_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (operation_log_id) REFERENCES operation_logs(id)
        );

        CREATE TABLE IF NOT EXISTS chapter_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            is_deleted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES chapter_comments(id)
        );
    ''')

    conn.commit()
    conn.close()


def create_initial_admin():
    """创建初始管理员账户（如果不存在），返回是否新建"""
    from werkzeug.security import generate_password_hash
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if cur.fetchone() is None:
        initial_password = 'admin123456'
        pw_hash = generate_password_hash(initial_password)
        cur.execute(
            "INSERT INTO users (username, password, role, student_id, display_name) VALUES (?, ?, ?, ?, ?)",
            ('admin', pw_hash, 'admin', '223101', '李康乐')
        )
        conn.commit()
        conn.close()
        return True, initial_password
    conn.close()
    return False, None
