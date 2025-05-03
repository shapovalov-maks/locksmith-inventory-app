# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import sqlite3, uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class User(UserMixin):
    def __init__(self, id_, email, session_token):
        self.id = id_
        self.email = email
        self.session_token = session_token

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, session_token FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        if 'session_token' in session and session['session_token'] == user[2]:
            return User(user[0], user[1], user[2])
        else:
            logout_user()
    return None

def get_all_keys(search_query=None):
    if not current_user.is_authenticated:
        return []
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    if search_query:
        query = f"%{search_query.lower()}%"
        cursor.execute('''
            SELECT id, fcc_id, make, model, year, box_slot, quantity, available, comments
            FROM keys
            WHERE user_id = ? AND (lower(fcc_id) LIKE ? OR lower(make) LIKE ? OR lower(model) LIKE ? OR CAST(year AS TEXT) LIKE ?)
            ORDER BY id DESC
        ''', (current_user.id, query, query, query, query))
    else:
        cursor.execute('''
            SELECT id, fcc_id, make, model, year, box_slot, quantity, available, comments
            FROM keys
            WHERE user_id = ?
            ORDER BY id DESC
        ''', (current_user.id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(['id','fcc_id','make','model','year','box_slot','quantity','available','comments'], row)) for row in rows]

@app.route('/')
@login_required
def index():
    search = request.args.get('search')
    keys = get_all_keys(search_query=search)
    return render_template('index.html', keys=keys, search=search)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        session_token = str(uuid.uuid4())
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, password, session_token) VALUES (?, ?, ?)', (email, password, session_token))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Email already registered."
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result and check_password_hash(result[1], password):
            session_token = str(uuid.uuid4())
            cursor.execute('UPDATE users SET session_token = ? WHERE id = ?', (session_token, result[0]))
            conn.commit()
            conn.close()
            user = User(result[0], email, session_token)
            session['session_token'] = session_token
            login_user(user)
            return redirect(url_for('index'))
        conn.close()
        return "Invalid credentials."
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('session_token', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add_key():
    fcc_id = request.form['fcc_id']
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    box_slot = request.form.get('box_slot', '')
    quantity = request.form['quantity']
    available = 1 if 'available' in request.form else 0
    comments = request.form.get('comments', '')
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO keys (fcc_id, make, model, year, box_slot, quantity, available, comments, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fcc_id, make, model, year, box_slot, quantity, available, comments, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/quick_add', methods=['POST'])
@login_required
def quick_add():
    fcc_id = request.form['fcc_id'].strip().upper()
    quantity_to_add = int(request.form['quantity'])
    box_slot = request.form.get('box_slot', '')

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, quantity FROM keys WHERE fcc_id = ? AND user_id = ?', (fcc_id, current_user.id))
    result = cursor.fetchone()

    if result:
        key_id, current_quantity = result
        new_quantity = current_quantity + quantity_to_add
        cursor.execute('''
            UPDATE keys
            SET quantity = ?, box_slot = ?, available = CASE WHEN ? > 0 THEN 1 ELSE 0 END
            WHERE id = ?
        ''', (new_quantity, box_slot, new_quantity, key_id))
    else:
        cursor.execute('''
            INSERT INTO keys (fcc_id, make, model, year, box_slot, quantity, available, comments, user_id)
            VALUES (?, '', '', 0, ?, ?, 1, '', ?)
        ''', (fcc_id, box_slot, quantity_to_add, current_user.id))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/upload_order', methods=['POST'])
@login_required
def upload_order():
    file = request.files['file']
    if not file:
        return "No file uploaded."

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filename.endswith('.txt'):
            df = pd.read_csv(filepath, delimiter=",", header=None)
            df.columns = ['fcc_id', 'quantity', 'box_slot']
        else:
            return "Unsupported file type."

        expected = {'fcc_id', 'quantity', 'box_slot'}
        if not expected.issubset(set(df.columns)):
            return "Missing required columns: fcc_id, quantity, box_slot"

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        for _, row in df.iterrows():
            fcc_id = str(row['fcc_id']).strip().upper()
            try:
                quantity = int(row['quantity'])
            except:
                quantity = 0
            box_slot = str(row['box_slot']).strip()

            cursor.execute('SELECT id, quantity FROM keys WHERE fcc_id = ? AND user_id = ?', (fcc_id, current_user.id))
            result = cursor.fetchone()

            if result:
                key_id, current_quantity = result
                new_quantity = current_quantity + quantity
                cursor.execute('''
                    UPDATE keys
                    SET quantity = ?, box_slot = ?, available = CASE WHEN ? > 0 THEN 1 ELSE 0 END
                    WHERE id = ?
                ''', (new_quantity, box_slot, new_quantity, key_id))
            else:
                cursor.execute('''
                    INSERT INTO keys (fcc_id, make, model, year, box_slot, quantity, available, comments, user_id)
                    VALUES (?, '', '', 0, ?, ?, 1, '', ?)
                ''', (fcc_id, box_slot, quantity, current_user.id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
