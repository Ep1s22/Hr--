import os
from functools import wraps
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_coursework'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_page'))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_page'))
        if session.get('user_role') != 'admin':
            return "Доступ запрещен", 403
        return view(*args, **kwargs)
    return wrapped


def redirect_by_role():
    role = session.get('user_role')
    if role == 'admin':
        return redirect(url_for('admin_panel'))
    return redirect(url_for('dashboard'))


ROLE_LABELS = {
    'admin': 'Администратор',
    'recruiter': 'Рекрутер',
    'candidate': 'Соискатель',
}


# --- 1. РОУТЫ СТРАНИЦ ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/vacancies')
def vacancies_page():
    return render_template('vacancies.html')


@app.route('/auth')
def auth_page():
    if 'user_id' in session:
        return redirect_by_role()
    return render_template('auth.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_panel'))

    conn = get_db_connection()
    cursor = conn.cursor()

    user_role = session.get('user_role')
    user_id = session.get('user_id')

    vacancies_list = []
    responses_list = []

    if user_role == 'recruiter':
        cursor.execute("SELECT * FROM vacancies WHERE recruiter_id = ?", (user_id,))
        vacancies_list = cursor.fetchall()

        cursor.execute("""
            SELECT r.id, r.cover_letter, r.status, r.resume_url, v.title as vacancy_title, u.full_name, u.phone
            FROM responses r
            JOIN vacancies v ON r.vacancy_id = v.id
            JOIN users u ON r.candidate_id = u.id
            WHERE v.recruiter_id = ?
            ORDER BY r.date_created DESC
        """, (user_id,))
        responses_list = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT r.id, r.status, v.title, v.company_name, v.city
            FROM responses r
            JOIN vacancies v ON r.vacancy_id = v.id
            WHERE r.candidate_id = ?
            ORDER BY r.date_created DESC
        """, (user_id,))
        responses_list = cursor.fetchall()

    conn.close()
    return render_template('dashboard.html', role=user_role, vacancies=vacancies_list, responses=responses_list)


@app.route('/admin')
@admin_required
def admin_panel():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'recruiter'")
    total_recruiters = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'candidate'")
    total_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vacancies")
    total_vacancies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM responses")
    total_responses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT id, username, email, role, full_name, phone
        FROM users
        ORDER BY id
    """)
    users = cursor.fetchall()

    cursor.execute("""
        SELECT v.id, v.title, v.company_name, v.city, v.date_created, u.full_name as recruiter_name
        FROM vacancies v
        LEFT JOIN users u ON v.recruiter_id = u.id
        ORDER BY v.date_created DESC
    """)
    vacancies = cursor.fetchall()

    cursor.execute("""
        SELECT r.id, r.status, r.date_created, r.resume_url,
               v.title as vacancy_title, u.full_name as candidate_name
        FROM responses r
        JOIN vacancies v ON r.vacancy_id = v.id
        JOIN users u ON r.candidate_id = u.id
        ORDER BY r.date_created DESC
    """)
    responses = cursor.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        stats={
            'users': total_users,
            'recruiters': total_recruiters,
            'candidates': total_candidates,
            'vacancies': total_vacancies,
            'responses': total_responses,
        },
        users=users,
        vacancies=vacancies,
        responses=responses,
        role_labels=ROLE_LABELS,
    )


# --- 2. API АВТЕНТИФИКАЦИИ ---

@app.route('/api/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')

    if role not in ('candidate', 'recruiter'):
        return "Регистрация доступна только для соискателей и рекрутеров", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, password, role, full_name, phone))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Пользователь с таким логином или email уже существует", 400

    conn.close()
    return redirect(url_for('auth_page'))


@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['user_username'] = user['username']
        session['user_role'] = user['role']
        session['user_name'] = user['full_name']
        return redirect_by_role()
    else:
        return "Неверный логин или пароль", 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- 3. API АДМИН-ПАНЕЛИ ---

@app.route('/admin/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Нельзя удалить свой аккаунт'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'Пользователь не найден'}), 404

    if user['role'] == 'admin':
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        if cursor.fetchone()[0] <= 1:
            conn.close()
            return jsonify({'error': 'Нельзя удалить последнего администратора'}), 400

    cursor.execute("DELETE FROM responses WHERE candidate_id = ?", (user_id,))
    cursor.execute("DELETE FROM responses WHERE vacancy_id IN (SELECT id FROM vacancies WHERE recruiter_id = ?)", (user_id,))
    cursor.execute("DELETE FROM vacancies WHERE recruiter_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': 'Пользователь удалён'})


@app.route('/admin/api/users/<int:user_id>/role', methods=['POST'])
@admin_required
def admin_change_user_role(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Нельзя изменить свою роль'}), 400

    new_role = request.json.get('role')
    if new_role not in ('candidate', 'recruiter'):
        return jsonify({'error': 'Допустимые роли: candidate, recruiter'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Пользователь не найден'}), 404

    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

    return jsonify({'success': f'Роль изменена на «{ROLE_LABELS[new_role]}»'})


@app.route('/admin/api/vacancies/<int:vacancy_id>', methods=['DELETE'])
@admin_required
def admin_delete_vacancy(vacancy_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM vacancies WHERE id = ?", (vacancy_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Вакансия не найдена'}), 404

    cursor.execute("DELETE FROM responses WHERE vacancy_id = ?", (vacancy_id,))
    cursor.execute("DELETE FROM vacancies WHERE id = ?", (vacancy_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': 'Вакансия удалена'})


@app.route('/admin/api/responses/<int:response_id>/status', methods=['POST'])
@admin_required
def admin_update_response_status(response_id):
    new_status = request.json.get('status')
    if not new_status:
        return jsonify({'error': 'Статус не передан'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM responses WHERE id = ?", (response_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Отклик не найден'}), 404

    cursor.execute("UPDATE responses SET status = ? WHERE id = ?", (new_status, response_id))
    conn.commit()
    conn.close()

    return jsonify({'success': f'Статус изменён на «{new_status}»'})


# --- 4. API ВАКАНСИЙ ---

@app.route('/api/filters', methods=['GET'])
def get_filters():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM categories")
    categories = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT code, name FROM experiences")
    experiences = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT code, name FROM employment_types")
    emp_types = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'categories': categories, 'experiences': experiences, 'employment_types': emp_types})


@app.route('/api/vacancies', methods=['GET'])
def get_vacancies():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM vacancies WHERE 1=1"
    params = []

    search_query = request.args.get('search')
    category = request.args.get('category')
    experience = request.args.get('experience')
    employment_types = request.args.getlist('employment_type')

    if search_query:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
    if category:
        query += " AND category_code = ?"
        params.append(category)
    if experience:
        query += " AND experience_code = ?"
        params.append(experience)
    if employment_types:
        placeholders = ', '.join(['?'] * len(employment_types))
        query += f" AND employment_code IN ({placeholders})"
        params.extend(employment_types)

    query += " ORDER BY date_created DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/api/add_vacancy', methods=['POST'])
def add_vacancy():
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return "Доступ запрещен", 403

    recruiter_id = session['user_id']
    title = request.form.get('title')
    category = request.form.get('category')
    salary_from = request.form.get('salary_from') or None
    salary_to = request.form.get('salary_to') or None
    experience = request.form.get('experience')
    employment_type = request.form.get('employment_type')
    description = request.form.get('description')
    company_name = request.form.get('company_name')
    city = request.form.get('city')

    image_url = None
    if 'company_logo' in request.files:
        file = request.files['company_logo']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filename += '.jpg'
            filename = f"user_{recruiter_id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/uploads/{filename}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vacancies (
            recruiter_id, title, category_code, salary_from, salary_to,
            experience_code, employment_code, description, company_name, city, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (recruiter_id, title, category, salary_from, salary_to, experience, employment_type, description, company_name, city, image_url))

    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


# --- 5. API ОТКЛИКОВ И УПРАВЛЕНИЯ СТАТУСАМИ ---

@app.route('/api/respond/<int:vacancy_id>', methods=['POST'])
def respond_to_vacancy(vacancy_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Авторизуйтесь как соискатель'}), 401
    if session.get('user_role') != 'candidate':
        return jsonify({'error': 'Только соискатели могут откликаться'}), 403

    candidate_id = session['user_id']
    cover_letter = request.form.get('cover_letter', '')

    resume_url = None
    if 'resume_file' in request.files:
        file = request.files['resume_file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
                filename += '.pdf'
            filename = f"resume_cand_{candidate_id}_vac_{vacancy_id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resume_url = f"/static/uploads/{filename}"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO responses (vacancy_id, candidate_id, cover_letter, resume_url, status)
            VALUES (?, ?, ?, ?, 'Новый')
        """, (vacancy_id, candidate_id, cover_letter, resume_url))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Вы уже откликались на эту вакансию'}), 400

    conn.close()
    return jsonify({'success': 'Отклик и резюме успешно отправлены!'})


@app.route('/api/response/<int:response_id>/status', methods=['POST'])
def update_response_status(response_id):
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return jsonify({'error': 'Доступ запрещен'}), 403

    new_status = request.json.get('status')
    if not new_status:
        return jsonify({'error': 'Статус не передан'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE responses SET status = ?
        WHERE id = ? AND vacancy_id IN (
            SELECT id FROM vacancies WHERE recruiter_id = ?
        )
    """, (new_status, response_id, session['user_id']))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Отклик не найден или нет доступа'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': f'Статус отклика успешно изменен на "{new_status}"'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
