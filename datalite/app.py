from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'func'))
DB_PATH = os.path.join(BASE_DIR, 'data.db')
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'uploads'))
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB per upload


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Create transactions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        type TEXT NOT NULL)''')
    # Create goals table
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        completed INTEGER NOT NULL,
                        date TEXT)''')
    # Create moments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS moments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        note TEXT,
                        image_path TEXT NOT NULL,
                        created_at TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/daily-tracker')
def daily_tracker_page():
    return send_from_directory(STATIC_DIR, 'daily_tracker.html')


@app.route('/accounting')
def accounting_manager_page():
    return send_from_directory(STATIC_DIR, 'accounting_manager.html')

@app.route('/moments-gallery')
def moments_gallery_page():
    return send_from_directory(STATIC_DIR, 'moments.html')

@app.route('/transactions', methods=['GET', 'POST', 'DELETE'])
def transactions():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT id, date, description, amount, type FROM transactions ORDER BY date DESC, id DESC')
        rows = cursor.fetchall()
        conn.close()
        transactions = [
            {
                'id': row['id'],
                'date': row['date'],
                'description': row['description'],
                'amount': row['amount'],
                'type': row['type'],
            }
            for row in rows
        ]
        return jsonify(transactions)

    elif request.method == 'POST':
        data = request.json or {}
        required = {'date', 'description', 'amount', 'type'}
        if not required.issubset(data):
            conn.close()
            return jsonify({'error': 'Missing required transaction fields'}), 400
        cursor.execute('INSERT INTO transactions (date, description, amount, type) VALUES (?, ?, ?, ?)',
                       (data['date'], data['description'], data['amount'], data['type']))
        transaction_id = cursor.lastrowid
        conn.commit()
        cursor.execute('SELECT id, date, description, amount, type FROM transactions WHERE id = ?', (transaction_id,))
        new_row = cursor.fetchone()
        conn.close()
        return jsonify(dict(new_row)), 201

    elif request.method == 'DELETE':
        data = request.json or {}
        if 'id' not in data:
            conn.close()
            return jsonify({'error': 'Missing transaction id'}), 400
        cursor.execute('DELETE FROM transactions WHERE id = ?', (data['id'],))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Transaction deleted successfully'})

@app.route('/goals', methods=['GET', 'POST', 'DELETE'])
def goals():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT id, name, completed, date FROM goals')
        rows = cursor.fetchall()
        conn.close()
        # Format the response as a list of dictionaries
        goals = [
            {
                'id': row[0],
                'name': row[1],
                'completed': row[2],
                'date': row[3]
            } for row in rows
        ]
        return jsonify(goals)

    elif request.method == 'POST':
        data = request.json or {}
        if 'name' not in data:
            conn.close()
            return jsonify({'error': 'Missing goal name'}), 400
        completed = data.get('completed', 0)
        date_value = data.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
        cursor.execute('INSERT INTO goals (name, completed, date) VALUES (?, ?, ?)',
                       (data['name'], completed, date_value))
        goal_id = cursor.lastrowid
        conn.commit()
        cursor.execute('SELECT id, name, completed, date FROM goals WHERE id = ?', (goal_id,))
        new_goal = cursor.fetchone()
        conn.close()
        return jsonify(dict(new_goal)), 201

    elif request.method == 'DELETE':
        data = request.json or {}
        if 'id' not in data:
            conn.close()
            return jsonify({'error': 'Missing goal id'}), 400
        cursor.execute('DELETE FROM goals WHERE id = ?', (data['id'],))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Goal deleted successfully'})


@app.route('/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    conn = get_connection()
    cursor = conn.cursor()
    data = request.json or {}

    fields = []
    values = []
    for column in ('name', 'completed', 'date'):
        if column in data:
            fields.append(f'{column} = ?')
            values.append(data[column])

    if not fields:
        conn.close()
        return jsonify({'error': 'No fields to update'}), 400

    values.append(goal_id)
    set_clause = ', '.join(fields)
    cursor.execute(f'UPDATE goals SET {set_clause} WHERE id = ?', values)
    conn.commit()
    cursor.execute('SELECT id, name, completed, date FROM goals WHERE id = ?', (goal_id,))
    updated_goal = cursor.fetchone()
    conn.close()

    if updated_goal is None:
        return jsonify({'error': 'Goal not found'}), 404

    return jsonify(dict(updated_goal))


@app.route('/moments', methods=['GET', 'POST'])
def moments():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT id, title, note, image_path, created_at FROM moments ORDER BY created_at DESC, id DESC')
        rows = cursor.fetchall()
        conn.close()
        moments = [
            {
                'id': row['id'],
                'title': row['title'],
                'note': row['note'],
                'image_url': f"/uploads/{row['image_path']}",
                'created_at': row['created_at'],
            }
            for row in rows
        ]
        return jsonify(moments)

    data_title = request.form.get('title', '').strip()
    if not data_title:
        conn.close()
        return jsonify({'error': 'Title is required'}), 400

    file = request.files.get('photo')
    if file is None or file.filename == '':
        conn.close()
        return jsonify({'error': 'Photo is required'}), 400

    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    final_name = f"{timestamp}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_name))

    note = request.form.get('note', '').strip() or None
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        'INSERT INTO moments (title, note, image_path, created_at) VALUES (?, ?, ?, ?)',
        (data_title, note, final_name, created_at),
    )
    moment_id = cursor.lastrowid
    conn.commit()
    cursor.execute('SELECT id, title, note, image_path, created_at FROM moments WHERE id = ?', (moment_id,))
    new_moment = cursor.fetchone()
    conn.close()

    response = dict(new_moment)
    response['image_url'] = f"/uploads/{new_moment['image_path']}"
    return jsonify(response), 201


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
