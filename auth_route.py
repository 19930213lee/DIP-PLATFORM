"""
西南交通大学希望学院 · 数字图像处理教学平台
认证路由模块 —— 注册 / 登录 / 登出 / 班级管理 / 数据中台 API
设计 & 技术支持：李康乐
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import db

auth_bp = Blueprint('auth', __name__)

# ──────────────────── 登录校验装饰器 ────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        if session.get('role') not in ('teacher', 'admin'):
            return jsonify({'status': 'error', 'message': '需要教师或管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return None
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, student_id, display_name FROM users WHERE id=?", (session['user_id'],))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ──────────────────── 页面路由 ────────────────────

@auth_bp.route('/login')
def login_page():
    """登录/注册页面"""
    if 'user_id' in session:
        return redirect(url_for('chapters'))
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('index'))


# ──────────────────── API：登录 ────────────────────


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': '请求数据为空'}), 400

    student_id = (data.get('student_id') or '').strip()
    password = (data.get('password') or '').strip()

    if not student_id or not password:
        return jsonify({'status': 'error', 'message': '学号/工号或密码不能为空'}), 400

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role, display_name, student_id FROM users WHERE student_id=?", (student_id,))
    row = cur.fetchone()
    conn.close()

    if not row or not check_password_hash(row['password'], password):
        return jsonify({'status': 'error', 'message': '学号/工号或密码错误'}), 401

    session['user_id'] = row['id']
    session['username'] = row['username']
    session['role'] = row['role']
    session['display_name'] = row['display_name']
    session['student_id'] = row['student_id']

    return jsonify({'status': 'success', 'message': '登录成功', 'role': row['role']})


# ──────────────────── 管理员用户管理 API ────────────────────

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        if session.get('role') != 'admin':
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/api/users', methods=['GET'])
@login_required
def api_list_users():
    """管理员列出所有用户"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute('''
        SELECT u.id, u.username, u.role, u.student_id, u.display_name, u.created_at,
               c.id as class_id, c.name as class_name
        FROM users u
        LEFT JOIN class_students cs ON cs.student_id = u.id
        LEFT JOIN classes c ON c.id = cs.class_id
        ORDER BY c.name, u.role, u.student_id
    ''')
    rows = cur.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'users': [dict(r) for r in rows]})


@auth_bp.route('/api/users/add', methods=['POST'])
@login_required
def api_add_user():
    """管理员新增用户"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': '请求数据为空'}), 400

    student_id = (data.get('student_id') or '').strip()
    display_name = (data.get('display_name') or '').strip()
    role = (data.get('role') or 'student').strip()
    password = (data.get('password') or student_id).strip()
    class_id = data.get('class_id')

    if role not in ('student', 'teacher'):
        return jsonify({'status': 'error', 'message': '角色只能是 student 或 teacher'}), 400
    if not all([student_id, display_name]):
        return jsonify({'status': 'error', 'message': '学号/工号和姓名均为必填'}), 400
    if len(password) < 6:
        return jsonify({'status': 'error', 'message': '密码至少 6 位'}), 400
    if role == 'student' and not class_id:
        return jsonify({'status': 'error', 'message': '创建学生必须指定班级'}), 400

    conn = db.get_conn()
    cur = conn.cursor()

    # 验证班级存在
    if class_id:
        cur.execute("SELECT id, name FROM classes WHERE id=?", (class_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({'status': 'error', 'message': '指定的班级不存在'}), 400

    cur.execute("SELECT id FROM users WHERE student_id=?", (student_id,))
    if cur.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': '学号/工号已存在'}), 409

    username = student_id
    pw_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password, role, student_id, display_name) VALUES (?,?,?,?,?)",
        (username, pw_hash, role, student_id, display_name)
    )
    user_id = cur.lastrowid

    # 学生自动加入班级
    if role == 'student' and class_id:
        cur.execute("INSERT INTO class_students (class_id, student_id) VALUES (?,?)", (class_id, user_id))

    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': '用户创建成功', 'user_id': user_id})


@auth_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def api_delete_user(user_id):
    """管理员删除用户（管理员不可删除自己）"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403

    if int(user_id) == int(session['user_id']):
        return jsonify({'status': 'error', 'message': '不能删除自己'}), 400

    conn = db.get_conn()
    cur = conn.cursor()

    cur.execute("SELECT role FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    if row['role'] == 'admin':
        conn.close()
        return jsonify({'status': 'error', 'message': '不能删除管理员账号'}), 403

    # 删除用户及其关联数据
    cur.execute("DELETE FROM class_students WHERE student_id=?", (user_id,))
    cur.execute("DELETE FROM ai_analysis_logs WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM operation_logs WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': '用户已删除'})


# ──────────────────── 密码修改 API ────────────────────

@auth_bp.route('/api/change_password', methods=['POST'])
@login_required
def api_change_password():
    """当前登录用户修改自己密码"""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': '请求数据为空'}), 400

    old_password = (data.get('old_password') or '')
    new_password = (data.get('new_password') or '').strip()

    if not old_password or not new_password:
        return jsonify({'status': 'error', 'message': '旧密码和新密码均为必填'}), 400
    if len(new_password) < 6:
        return jsonify({'status': 'error', 'message': '新密码至少 6 位'}), 400

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE id=?", (session['user_id'],))
    row = cur.fetchone()
    conn.close()

    if not row or not check_password_hash(row['password'], old_password):
        return jsonify({'status': 'error', 'message': '旧密码不正确'}), 403

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password=? WHERE id=?",
        (generate_password_hash(new_password), session['user_id'])
    )
    conn.commit()
    conn.close()

    session.clear()
    return jsonify({'status': 'success', 'message': '密码修改成功，请重新登录'})


@auth_bp.route('/api/users/<int:user_id>/reset_password', methods=['POST'])
@login_required
def api_reset_password(user_id):
    """管理员重置指定用户密码"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': '请求数据为空'}), 400

    new_password = (data.get('new_password') or '').strip()
    if not new_password or len(new_password) < 6:
        return jsonify({'status': 'error', 'message': '新密码至少 6 位'}), 400

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    cur.execute(
        "UPDATE users SET password=? WHERE id=?",
        (generate_password_hash(new_password), user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': '密码重置成功'})


# ──────────────────── 当前用户 ────────────────────

@auth_bp.route('/api/me', methods=['GET'])
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    return jsonify({'status': 'success', 'user': user})


# ──────────────────── 班级管理 API（教师）────────────────────

@auth_bp.route('/api/teacher/classes', methods=['GET', 'POST'])
@teacher_required
def teacher_classes():
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if request.method == 'GET':
        if is_admin:
            cur.execute('''
                SELECT c.id, c.name, c.created_at,
                       COUNT(cs.student_id) as student_count,
                       u.display_name as teacher_name
                FROM classes c
                LEFT JOIN class_students cs ON cs.class_id = c.id
                LEFT JOIN users u ON u.id = c.teacher_id
                GROUP BY c.id
                ORDER BY c.created_at DESC
            ''')
        else:
            cur.execute('''
                SELECT c.id, c.name, c.created_at,
                       COUNT(cs.student_id) as student_count
                FROM classes c
                LEFT JOIN class_students cs ON cs.class_id = c.id
                WHERE c.teacher_id = ?
                GROUP BY c.id
                ORDER BY c.created_at DESC
            ''', (teacher_id,))
        rows = cur.fetchall()
        conn.close()
        return jsonify({'status': 'success', 'classes': [dict(r) for r in rows]})

    if request.method == 'POST':
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        if not name:
            conn.close()
            return jsonify({'status': 'error', 'message': '班级名称不能为空'}), 400

        # 管理员创建班级时必须指定归属教师
        if is_admin:
            req_teacher_id = data.get('teacher_id')
            if not req_teacher_id:
                conn.close()
                return jsonify({'status': 'error', 'message': '请指定归属教师'}), 400
            # 验证 teacher_id 是否为有效教师
            cur.execute("SELECT id, display_name FROM users WHERE id=? AND role='teacher'", (req_teacher_id,))
            teacher_row = cur.fetchone()
            if not teacher_row:
                conn.close()
                return jsonify({'status': 'error', 'message': '指定教师不存在或角色非教师'}), 400
            target_teacher_id = req_teacher_id
        else:
            target_teacher_id = teacher_id

        # 检查同名班级
        cur.execute("SELECT id FROM classes WHERE name=? AND teacher_id=?", (name, target_teacher_id))
        if cur.fetchone():
            conn.close()
            return jsonify({'status': 'error', 'message': '班级名称已存在'}), 409

        cur.execute("INSERT INTO classes (name, teacher_id) VALUES (?,?)", (name, target_teacher_id))
        conn.commit()
        class_id = cur.lastrowid
        conn.close()
        return jsonify({'status': 'success', 'class_id': class_id, 'name': name})


@auth_bp.route('/api/teacher/classes/<int:class_id>', methods=['DELETE', 'PUT'])
@teacher_required
def teacher_manage_class(class_id):
    """管理员/教师管理班级（删除/编辑）"""
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    # ── PUT：编辑班级（仅管理员）──
    if request.method == 'PUT':
        if not is_admin:
            conn.close()
            return jsonify({'status': 'error', 'message': '仅管理员可编辑班级'}), 403

        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        new_teacher_id = data.get('teacher_id')

        if not name and not new_teacher_id:
            conn.close()
            return jsonify({'status': 'error', 'message': '未提供任何修改内容'}), 400

        # 验证班级存在
        cur.execute("SELECT id, name, teacher_id FROM classes WHERE id=?", (class_id,))
        existing = cur.fetchone()
        if not existing:
            conn.close()
            return jsonify({'status': 'error', 'message': '班级不存在'}), 404

        # 修改名称
        if name:
            cur.execute("SELECT id FROM classes WHERE name=? AND id!=?", (name, class_id))
            if cur.fetchone():
                conn.close()
                return jsonify({'status': 'error', 'message': '班级名称已存在'}), 409
            cur.execute("UPDATE classes SET name=? WHERE id=?", (name, class_id))

        # 修改归属教师
        if new_teacher_id:
            cur.execute("SELECT id, display_name FROM users WHERE id=? AND role='teacher'", (new_teacher_id,))
            if not cur.fetchone():
                conn.close()
                return jsonify({'status': 'error', 'message': '指定教师不存在或角色非教师'}), 400
            cur.execute("UPDATE classes SET teacher_id=? WHERE id=?", (new_teacher_id, class_id))

        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': '班级信息已更新'})

    # ── DELETE：删除班级 ──
    if is_admin:
        cur.execute("SELECT id FROM classes WHERE id=?", (class_id,))
    else:
        cur.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, teacher_id))
    if not cur.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': '班级不存在或无权操作'}), 403

    cur.execute("DELETE FROM class_students WHERE class_id=?", (class_id,))
    cur.execute("DELETE FROM classes WHERE id=?", (class_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': '班级已删除'})


@auth_bp.route('/api/teacher/classes/<int:class_id>/students', methods=['GET', 'POST', 'DELETE'])
@teacher_required
def teacher_class_students(class_id):
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']

    # 验证班级归属
    cur.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, teacher_id))
    if not cur.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': '班级不存在或无权访问'}), 403

    if request.method == 'GET':
        cur.execute('''
            SELECT u.id, u.student_id, u.display_name, cs.id as cs_id
            FROM class_students cs
            JOIN users u ON u.id = cs.student_id
            WHERE cs.class_id = ?
            ORDER BY u.student_id
        ''', (class_id,))
        rows = cur.fetchall()
        conn.close()
        return jsonify({'status': 'success', 'students': [dict(r) for r in rows]})

    if request.method == 'POST':
        data = request.get_json() or {}
        student_id_str = (data.get('student_id') or '').strip()
        if not student_id_str:
            conn.close()
            return jsonify({'status': 'error', 'message': '学号不能为空'}), 400

        cur.execute("SELECT id FROM users WHERE student_id=? AND role='student'", (student_id_str,))
        student = cur.fetchone()
        if not student:
            conn.close()
            return jsonify({'status': 'error', 'message': '未找到该学号的学生'}), 404

        try:
            cur.execute("INSERT INTO class_students (class_id, student_id) VALUES (?,?)", (class_id, student['id']))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'status': 'error', 'message': '该学生已在班级中'}), 409
        conn.close()
        return jsonify({'status': 'success', 'message': '添加成功'})

    if request.method == 'DELETE':
        data = request.get_json() or {}
        student_id_val = data.get('student_id')
        if student_id_val is None:
            conn.close()
            return jsonify({'status': 'error', 'message': '缺少 student_id'}), 400
        cur.execute("DELETE FROM class_students WHERE class_id=? AND student_id=?", (class_id, student_id_val))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': '移除成功'})


@auth_bp.route('/api/teacher/students', methods=['GET'])
@teacher_required
def teacher_search_students():
    q = (request.args.get('q') or '').strip()
    conn = db.get_conn()
    cur = conn.cursor()
    if q:
        cur.execute(
            "SELECT id, student_id, display_name FROM users WHERE role='student' AND (student_id LIKE ? OR display_name LIKE ?) LIMIT 50",
            (f'%{q}%', f'%{q}%')
        )
    else:
        cur.execute("SELECT id, student_id, display_name FROM users WHERE role='student' LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'students': [dict(r) for r in rows]})


# ──────────────────── 操作数据埋点 API ────────────────────

@auth_bp.route('/api/log/operation', methods=['POST'])
def log_operation():
    data = request.get_json() or {}
    user_id = session.get('user_id')

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO operation_logs (user_id, chapter_id, operation_id, operation_name, params_json, image_filename, result_type, error_msg, duration_ms) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            user_id,
            data.get('chapter_id'),
            data.get('operation_id'),
            data.get('operation_name'),
            json.dumps(data.get('params', {}), ensure_ascii=False),
            data.get('image_filename'),
            data.get('result_type', 'success'),
            data.get('error_msg'),
            data.get('duration_ms')
        )
    )
    log_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'log_id': log_id})


@auth_bp.route('/api/log/ai_analysis', methods=['POST'])
def log_ai_analysis():
    data = request.get_json() or {}
    user_id = session.get('user_id')

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ai_analysis_logs (user_id, operation_log_id, analysis_content) VALUES (?,?,?)",
        (user_id, data.get('operation_log_id'), data.get('analysis_content'))
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})


# ──────────────────── 数据中台 API ────────────────────

def _verify_class_ownership(conn, class_id, teacher_id, is_admin):
    """验证班级归属：管理员通过，教师需验证 class 是否属于自己"""
    if is_admin:
        return True
    cur = conn.cursor()
    cur.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, teacher_id))
    return cur.fetchone() is not None


def _get_student_scope(class_id, teacher_id, is_admin):
    """
    返回 (join_clause, filter_clause, params) 用于限定学生范围。
    - class_id 传入：限定到该班级（调用前应已做所有权验证）
    - 未传 + 教师：限定到该教师所有班级的学生
    - 未传 + 管理员：不限定
    """
    if class_id:
        return (
            "JOIN class_students cs ON cs.student_id = u.id",
            "AND cs.class_id = ?",
            [class_id]
        )
    elif not is_admin:
        return (
            "JOIN class_students cs ON cs.student_id = u.id",
            "AND cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?)",
            [teacher_id]
        )
    else:
        return ("", "", [])


@auth_bp.route('/api/dashboard/overview')
@teacher_required
def dashboard_overview():
    class_id = request.args.get('class_id')
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    # 验证班级所有权
    if class_id and not _verify_class_ownership(conn, class_id, teacher_id, is_admin):
        conn.close()
        return jsonify({'status': 'error', 'message': '无权访问此班级'}), 403

    # 总学生数
    if class_id:
        cur.execute(
            "SELECT COUNT(DISTINCT u.id) as cnt FROM users u JOIN class_students cs ON cs.student_id = u.id WHERE cs.class_id = ? AND u.role='student'",
            (class_id,)
        )
    elif not is_admin:
        cur.execute(
            "SELECT COUNT(DISTINCT u.id) as cnt FROM users u JOIN class_students cs ON cs.student_id = u.id WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND u.role='student'",
            (teacher_id,)
        )
    else:
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role='student'")
    total_students = cur.fetchone()['cnt']

    # 总班级数
    if is_admin:
        cur.execute("SELECT COUNT(*) as cnt FROM classes")
    else:
        cur.execute("SELECT COUNT(*) as cnt FROM classes WHERE teacher_id=?", (teacher_id,))
    total_classes = cur.fetchone()['cnt']

    # 总操作次数（仅学生）
    if class_id:
        cur.execute(
            "SELECT COUNT(*) as cnt FROM operation_logs ol JOIN users u ON u.id = ol.user_id JOIN class_students cs ON cs.student_id = u.id WHERE cs.class_id = ? AND u.role='student'",
            (class_id,)
        )
    elif not is_admin:
        cur.execute(
            "SELECT COUNT(*) as cnt FROM operation_logs ol JOIN users u ON u.id = ol.user_id JOIN class_students cs ON cs.student_id = u.id WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND u.role='student'",
            (teacher_id,)
        )
    else:
        cur.execute("SELECT COUNT(*) as cnt FROM operation_logs JOIN users ON users.id = operation_logs.user_id WHERE users.role='student'")
    total_operations = cur.fetchone()['cnt']

    # 今日活跃学生数
    if class_id:
        cur.execute(
            "SELECT COUNT(DISTINCT ol.user_id) as cnt FROM operation_logs ol JOIN users u ON u.id = ol.user_id JOIN class_students cs ON cs.student_id = u.id WHERE cs.class_id = ? AND u.role='student' AND date(ol.created_at)=date('now')",
            (class_id,)
        )
    elif not is_admin:
        cur.execute(
            "SELECT COUNT(DISTINCT ol.user_id) as cnt FROM operation_logs ol JOIN users u ON u.id = ol.user_id JOIN class_students cs ON cs.student_id = u.id WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND u.role='student' AND date(ol.created_at)=date('now')",
            (teacher_id,)
        )
    else:
        cur.execute("SELECT COUNT(DISTINCT user_id) as cnt FROM operation_logs JOIN users ON users.id = operation_logs.user_id WHERE users.role='student' AND date(operation_logs.created_at)=date('now')")
    active_today = cur.fetchone()['cnt']

    conn.close()
    return jsonify({
        'status': 'success',
        'total_students': total_students,
        'total_classes': total_classes,
        'total_operations': total_operations,
        'active_today': active_today
    })


@auth_bp.route('/api/dashboard/operation_stats')
@teacher_required
def dashboard_operation_stats():
    class_id = request.args.get('class_id')
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if class_id and not _verify_class_ownership(conn, class_id, teacher_id, is_admin):
        conn.close()
        return jsonify({'status': 'error', 'message': '无权访问此班级'}), 403

    if class_id:
        cur.execute('''
            SELECT ol.operation_name, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN class_students cs ON cs.student_id = ol.user_id
            JOIN users ON users.id = ol.user_id
            WHERE cs.class_id = ? AND users.role='student'
            GROUP BY ol.operation_name
            ORDER BY cnt DESC
        ''', (class_id,))
    elif not is_admin:
        cur.execute('''
            SELECT ol.operation_name, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            JOIN class_students cs ON cs.student_id = ol.user_id
            WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND users.role='student'
            GROUP BY ol.operation_name
            ORDER BY cnt DESC
        ''', (teacher_id,))
    else:
        cur.execute('''
            SELECT ol.operation_name, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            WHERE users.role='student'
            GROUP BY ol.operation_name
            ORDER BY cnt DESC
        ''')

    rows = cur.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'stats': [dict(r) for r in rows]})


@auth_bp.route('/api/dashboard/student_ranking')
@teacher_required
def dashboard_student_ranking():
    class_id = request.args.get('class_id')
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if class_id and not _verify_class_ownership(conn, class_id, teacher_id, is_admin):
        conn.close()
        return jsonify({'status': 'error', 'message': '无权访问此班级'}), 403

    base_query = '''
        SELECT u.id, u.student_id, u.display_name,
               COUNT(ol.id) as total_ops,
               SUM(CASE WHEN ol.result_type='success' THEN 1 ELSE 0 END) as success_count
        FROM users u
        JOIN operation_logs ol ON ol.user_id = u.id
    '''
    join_clause = ''
    where_clause = ''
    params = []

    if class_id:
        join_clause = ' JOIN class_students cs ON cs.student_id = u.id'
        where_clause = ' WHERE cs.class_id = ? AND u.role=\'student\''
        params.append(class_id)
    elif not is_admin:
        join_clause = ' JOIN class_students cs ON cs.student_id = u.id'
        where_clause = " WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND u.role='student'"
        params.append(teacher_id)
    else:
        where_clause = " WHERE u.role='student'"

    query = f'''
        {base_query}
        {join_clause}
        {where_clause}
        GROUP BY u.id
        ORDER BY total_ops DESC
        LIMIT 50
    '''

    cur.execute(query, params)
    rows = cur.fetchall()

    result = []
    for r in rows:
        d = dict(r)
        d['success_rate'] = round(d['success_count'] / d['total_ops'] * 100, 1) if d['total_ops'] > 0 else 0
        result.append(d)

    conn.close()
    return jsonify({'status': 'success', 'ranking': result})


@auth_bp.route('/api/dashboard/error_analysis')
@teacher_required
def dashboard_error_analysis():
    class_id = request.args.get('class_id')
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if class_id and not _verify_class_ownership(conn, class_id, teacher_id, is_admin):
        conn.close()
        return jsonify({'status': 'error', 'message': '无权访问此班级'}), 403

    if class_id:
        cur.execute('''
            SELECT ol.operation_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN ol.result_type='error' THEN 1 ELSE 0 END) as error_count
            FROM operation_logs ol
            JOIN class_students cs ON cs.student_id = ol.user_id
            JOIN users ON users.id = ol.user_id
            WHERE cs.class_id = ? AND users.role='student'
            GROUP BY ol.operation_name
            ORDER BY error_count DESC
        ''', (class_id,))
    elif not is_admin:
        cur.execute('''
            SELECT ol.operation_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN ol.result_type='error' THEN 1 ELSE 0 END) as error_count
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            JOIN class_students cs ON cs.student_id = ol.user_id
            WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND users.role='student'
            GROUP BY ol.operation_name
            ORDER BY error_count DESC
        ''', (teacher_id,))
    else:
        cur.execute('''
            SELECT ol.operation_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN ol.result_type='error' THEN 1 ELSE 0 END) as error_count
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            WHERE users.role='student'
            GROUP BY ol.operation_name
            ORDER BY error_count DESC
        ''')

    rows = cur.fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d['error_rate'] = round(d['error_count'] / d['total'] * 100, 1) if d['total'] > 0 else 0
        result.append(d)
    conn.close()
    return jsonify({'status': 'success', 'analysis': result})


@auth_bp.route('/api/dashboard/student_detail/<int:student_id>')
@teacher_required
def dashboard_student_detail(student_id):
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    # 非管理员需验证该学生是否在自己班级中
    if not is_admin:
        cur.execute('''
            SELECT cs.id FROM class_students cs
            JOIN classes c ON c.id = cs.class_id
            WHERE cs.student_id = ? AND c.teacher_id = ?
        ''', (student_id, teacher_id))
        if not cur.fetchone():
            conn.close()
            return jsonify({'status': 'error', 'message': '无权查看该学生数据'}), 403

    cur.execute('''
        SELECT ol.operation_name, ol.chapter_id, ol.params_json, ol.duration_ms,
               ol.result_type, ol.error_msg, ol.created_at
        FROM operation_logs ol
        JOIN users ON users.id = ol.user_id
        WHERE ol.user_id = ? AND users.role='student'
        ORDER BY ol.created_at DESC
        LIMIT 200
    ''', (student_id,))

    rows = cur.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'records': [dict(r) for r in rows]})


@auth_bp.route('/api/dashboard/time_trend')
@teacher_required
def dashboard_time_trend():
    days = request.args.get('days', '7')
    class_id = request.args.get('class_id')
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if class_id and not _verify_class_ownership(conn, class_id, teacher_id, is_admin):
        conn.close()
        return jsonify({'status': 'error', 'message': '无权访问此班级'}), 403

    if class_id:
        cur.execute('''
            SELECT date(ol.created_at) as day, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN class_students cs ON cs.student_id = ol.user_id
            JOIN users ON users.id = ol.user_id
            WHERE cs.class_id = ? AND users.role='student' AND ol.created_at >= date('now', ?)
            GROUP BY day
            ORDER BY day
        ''', (class_id, f'-{days} days'))
    elif not is_admin:
        cur.execute('''
            SELECT date(ol.created_at) as day, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            JOIN class_students cs ON cs.student_id = ol.user_id
            WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND users.role='student' AND ol.created_at >= date('now', ?)
            GROUP BY day
            ORDER BY day
        ''', (teacher_id, f'-{days} days'))
    else:
        cur.execute('''
            SELECT date(ol.created_at) as day, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            WHERE users.role='student' AND ol.created_at >= date('now', ?)
            GROUP BY day
            ORDER BY day
        ''', (f'-{days} days',))

    rows = cur.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'trend': [dict(r) for r in rows]})


@auth_bp.route('/api/dashboard/chapter_heat')
@teacher_required
def dashboard_chapter_heat():
    class_id = request.args.get('class_id')
    conn = db.get_conn()
    cur = conn.cursor()
    teacher_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if class_id and not _verify_class_ownership(conn, class_id, teacher_id, is_admin):
        conn.close()
        return jsonify({'status': 'error', 'message': '无权访问此班级'}), 403

    if class_id:
        cur.execute('''
            SELECT ol.chapter_id, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN class_students cs ON cs.student_id = ol.user_id
            JOIN users ON users.id = ol.user_id
            WHERE cs.class_id = ? AND users.role='student' AND ol.chapter_id IS NOT NULL
            GROUP BY ol.chapter_id
            ORDER BY CAST(ol.chapter_id AS INTEGER)
        ''', (class_id,))
    elif not is_admin:
        cur.execute('''
            SELECT ol.chapter_id, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            JOIN class_students cs ON cs.student_id = ol.user_id
            WHERE cs.class_id IN (SELECT id FROM classes WHERE teacher_id=?) AND users.role='student' AND ol.chapter_id IS NOT NULL
            GROUP BY ol.chapter_id
            ORDER BY CAST(ol.chapter_id AS INTEGER)
        ''', (teacher_id,))
    else:
        cur.execute('''
            SELECT ol.chapter_id, COUNT(*) as cnt
            FROM operation_logs ol
            JOIN users ON users.id = ol.user_id
            WHERE users.role='student' AND ol.chapter_id IS NOT NULL
            GROUP BY ol.chapter_id
            ORDER BY CAST(ol.chapter_id AS INTEGER)
        ''')

    rows = cur.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'heat': [dict(r) for r in rows]})


# ──────────────────── 章节讨论区 API ────────────────────

@auth_bp.route('/api/comments/<int:chapter_id>')
@login_required
def get_comments(chapter_id):
    """获取某章所有评论（含回复嵌套）"""
    conn = db.get_conn()
    cur = conn.cursor()
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    # 获取所有未删除的顶级评论（parent_id IS NULL）
    cur.execute('''
        SELECT cc.id, cc.chapter_id, cc.user_id, u.display_name as user_name,
               cc.content, cc.parent_id, cc.is_deleted, cc.created_at
        FROM chapter_comments cc
        JOIN users u ON u.id = cc.user_id
        WHERE cc.chapter_id = ? AND cc.parent_id IS NULL
        ORDER BY cc.created_at DESC
    ''', (chapter_id,))
    parents = [dict(r) for r in cur.fetchall()]

    # 获取所有回复
    cur.execute('''
        SELECT cc.id, cc.chapter_id, cc.user_id, u.display_name as user_name,
               cc.content, cc.parent_id, cc.is_deleted, cc.created_at
        FROM chapter_comments cc
        JOIN users u ON u.id = cc.user_id
        WHERE cc.chapter_id = ? AND cc.parent_id IS NOT NULL
        ORDER BY cc.created_at ASC
    ''', (chapter_id,))
    replies = [dict(r) for r in cur.fetchall()]
    conn.close()

    # 嵌套组装 + 标记 is_own
    for c in parents + replies:
        c['is_own'] = (c['user_id'] == user_id or is_admin)
        c['can_delete'] = (c['user_id'] == user_id or is_admin)

    # 组装：把回复挂到对应父评论下
    reply_map = {}
    for r in replies:
        reply_map.setdefault(r['parent_id'], []).append(r)

    result = []
    for p in parents:
        p['replies'] = reply_map.get(p['id'], [])
        result.append(p)

    return jsonify({'status': 'success', 'comments': result})


@auth_bp.route('/api/comments', methods=['POST'])
@login_required
def create_comment():
    """发表评论或回复"""
    data = request.get_json() or {}
    chapter_id = data.get('chapter_id')
    content = (data.get('content') or '').strip()
    parent_id = data.get('parent_id')

    if not chapter_id or not content:
        return jsonify({'status': 'error', 'message': '章节和内容不能为空'}), 400
    if len(content) > 2000:
        return jsonify({'status': 'error', 'message': '评论内容不能超过2000字'}), 400

    user_id = session['user_id']

    # 如果是回复，验证父评论存在
    if parent_id:
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM chapter_comments WHERE id=? AND chapter_id=? AND parent_id IS NULL AND is_deleted=0",
                    (parent_id, chapter_id))
        if not cur.fetchone():
            conn.close()
            return jsonify({'status': 'error', 'message': '父评论不存在或已被删除'}), 400
        conn.close()

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chapter_comments (chapter_id, user_id, content, parent_id) VALUES (?,?,?,?)",
        (chapter_id, user_id, content, parent_id)
    )
    conn.commit()

    # 获取刚插入的完整信息
    comment_id = cur.lastrowid
    cur.execute('''
        SELECT cc.id, cc.chapter_id, cc.user_id, u.display_name as user_name,
               cc.content, cc.parent_id, cc.is_deleted, cc.created_at
        FROM chapter_comments cc
        JOIN users u ON u.id = cc.user_id
        WHERE cc.id = ?
    ''', (comment_id,))
    row = dict(cur.fetchone())
    conn.close()

    row['is_own'] = True
    row['can_delete'] = True
    return jsonify({'status': 'success', 'comment': row})


@auth_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """删除评论（软删除）"""
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id FROM chapter_comments WHERE id=?", (comment_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'status': 'error', 'message': '评论不存在'}), 404
    if not is_admin and row['user_id'] != user_id:
        conn.close()
        return jsonify({'status': 'error', 'message': '无权删除此评论'}), 403

    cur.execute("UPDATE chapter_comments SET is_deleted=1 WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': '删除成功'})


@auth_bp.route('/api/admin/comment_logs')
@teacher_required
def admin_comment_logs():
    """管理员评论日志（支持筛选和搜索）"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403

    chapter_id = request.args.get('chapter_id', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    conn = db.get_conn()
    cur = conn.cursor()

    conditions = []
    params = []

    if chapter_id:
        conditions.append("cc.chapter_id = ?")
        params.append(int(chapter_id))
    if search:
        conditions.append("(u.display_name LIKE ? OR cc.content LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    # 总数
    cur.execute(f"SELECT COUNT(*) as cnt FROM chapter_comments cc JOIN users u ON u.id = cc.user_id {where}", params)
    total = cur.fetchone()['cnt']

    # 分页查询
    offset = (page - 1) * per_page
    cur.execute(f'''
        SELECT cc.id, cc.chapter_id, cc.user_id, u.display_name as user_name,
               cc.content, cc.parent_id, cc.is_deleted, cc.created_at
        FROM chapter_comments cc
        JOIN users u ON u.id = cc.user_id
        {where}
        ORDER BY cc.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    logs = [dict(r) for r in cur.fetchall()]
    conn.close()

    return jsonify({
        'status': 'success',
        'logs': logs,
        'total': total,
        'page': page,
        'per_page': per_page
    })


# ──────────────────── 数据中台页面 ────────────────────

@auth_bp.route('/dashboard')
@teacher_required
def dashboard_page():
    return render_template('dashboard.html', user=get_current_user())
