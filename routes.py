from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import SessionLocal, KnownCode

bp = Blueprint('known_codes', __name__)

@bp.route('/known-codes')
@login_required
def known_codes():
    db = SessionLocal()
    brand = request.args.get("brand", "").strip()
    code_type = request.args.get("type", "").strip()

    query = db.query(KnownCode)
    if brand:
        query = query.filter(KnownCode.brand.ilike(f"%{brand}%"))
    if code_type:
        query = query.filter(KnownCode.type.ilike(f"%{code_type}%"))

    codes = query.order_by(KnownCode.id.desc()).all()
    return render_template("known_codes.html", codes=codes, brand=brand, code_type=code_type)


@bp.route('/known-codes/api/<barcode>')
@login_required
def get_known_code(barcode):
    db = SessionLocal()
    code = db.query(KnownCode).filter_by(barcode=barcode).first()
    if code:
        return jsonify({
            "type": code.type,
            "description": code.description,
            "brand": code.brand
        })
    return jsonify({}), 404


@bp.route('/known-codes/edit/<int:code_id>', methods=['GET', 'POST'])
@login_required
def edit_known_code(code_id):
    db = SessionLocal()
    code = db.query(KnownCode).get(code_id)
    if request.method == 'POST':
        code.barcode = request.form.get('barcode')
        code.type = request.form.get('type')
        code.description = request.form.get('description')
        code.brand = request.form.get('brand')
        db.commit()
        return redirect(url_for('known_codes.known_codes'))
    return render_template('edit_known_code.html', code=code)


@bp.route('/known-codes/delete/<int:code_id>', methods=['POST'])
@login_required
def delete_known_code(code_id):
    db = SessionLocal()
    code = db.query(KnownCode).get(code_id)
    if code:
        db.delete(code)
        db.commit()
    return redirect(url_for('known_codes.known_codes'))
