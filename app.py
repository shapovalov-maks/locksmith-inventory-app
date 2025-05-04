from flask import Flask, render_template, request, redirect, url_for, after_this_request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, or_
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, declarative_base
import os
from dotenv import load_dotenv
import uuid

# ============================
# Setup
# ============================

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev")

app = Flask(__name__)
app.secret_key = SECRET_KEY

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============================
# Add proper MIME type for .wasm
# ============================

@app.after_request
def set_headers(response):
    if request.path.endswith('.wasm'):
        response.headers['Content-Type'] = 'application/wasm'
    return response

# ============================
# Models
# ============================

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    session_token = Column(String)
    keys = relationship("Key", back_populates="user")

class Key(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True)
    fcc_id = Column(String)
    barcode = Column(String)
    type = Column(String, default='fcc')
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    box_slot = Column(String)
    quantity = Column(Integer, default=0)
    available = Column(Boolean, default=True)
    comments = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="keys")

class KnownCode(Base):
    __tablename__ = 'known_codes'
    id = Column(Integer, primary_key=True)
    barcode = Column(String, unique=True)
    type = Column(String)
    description = Column(String)
    brand = Column(String)

# ============================
# User Loader
# ============================

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    return db.query(User).get(int(user_id))

# ============================
# Routes
# ============================

@app.route('/')
@login_required
def index():
    db = SessionLocal()
    search = request.args.get("search", "").strip()
    query = db.query(Key).filter_by(user_id=current_user.id)

    if search:
        query = query.filter(or_(
            Key.fcc_id.ilike(f"%{search}%"),
            Key.make.ilike(f"%{search}%"),
            Key.model.ilike(f"%{search}%"),
            Key.type.ilike(f"%{search}%"),
            Key.barcode.ilike(f"%{search}%")
        ))

    keys = query.order_by(Key.id.desc()).all()
    return render_template('index.html', keys=keys, search=search)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = SessionLocal()
        email = request.form['email']
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return 'Email already registered.'
        password = generate_password_hash(request.form['password'])
        token = str(uuid.uuid4())
        user = User(email=email, password=password, session_token=token)
        db.add(user)
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = SessionLocal()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add_key():
    db = SessionLocal()
    barcode = request.form.get('barcode')
    known = db.query(KnownCode).filter_by(barcode=barcode).first()

    new_key = Key(
        fcc_id=request.form.get('fcc_id'),
        barcode=barcode,
        type=request.form.get('type') or (known.type if known else 'fcc'),
        make=request.form.get('make') or (known.description if known else None),
        model=request.form.get('model') or None,
        year=int(request.form.get('year')) if request.form.get('year') else None,
        box_slot=request.form.get('box_slot'),
        quantity=int(request.form.get('quantity', 0)),
        available='available' in request.form,
        comments=request.form.get('comments'),
        user_id=current_user.id
    )
    db.add(new_key)
    db.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:key_id>', methods=['POST'])
@login_required
def delete_key(key_id):
    db = SessionLocal()
    key = db.query(Key).filter_by(id=key_id, user_id=current_user.id).first()
    if key:
        db.delete(key)
        db.commit()
    return redirect(url_for('index'))

# ============================
# Register blueprint
# ============================

from routes import bp as known_codes_bp
app.register_blueprint(known_codes_bp)

# ============================
# DB Init (only for local)
# ============================

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
