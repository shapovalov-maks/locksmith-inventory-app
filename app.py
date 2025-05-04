from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
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
    keys = db.query(Key).filter_by(user_id=current_user.id).order_by(Key.id.desc()).all()
    return render_template('index.html', keys=keys)

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
    new_key = Key(
        fcc_id=request.form.get('fcc_id'),
        barcode=request.form.get('barcode'),
        type=request.form.get('type', 'fcc'),
        make=request.form.get('make') or None,
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

# ============================
# DB Init (only for first launch)
# ============================

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
