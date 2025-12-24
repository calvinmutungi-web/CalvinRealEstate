import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'calvin_platinum_ultimate_2025'

# --- DATABASE CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'calvin_v5.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db = SQLAlchemy(app)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100))
    category = db.Column(db.String(50)) # Villa, Penthouse, Land
    beds = db.Column(db.Integer)
    baths = db.Column(db.Integer)
    sqft = db.Column(db.String(20))
    details = db.Column(db.Text)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

@app.route('/')
def index():
    q = request.args.get('q', '')
    cat = request.args.get('category', '')
    
    query = Property.query
    if q: query = query.filter(Property.location.contains(q))
    if cat: query = query.filter(Property.category == cat)
    
    props = query.order_by(Property.created_at.desc()).all()
    return render_template('index.html', properties=props)

@app.route('/inquire', methods=['POST'])
def inquire():
    name, phone, msg = request.form.get('name'), request.form.get('phone'), request.form.get('message')
    lead = Lead(name=name, phone=phone, message=msg)
    db.session.add(lead)
    db.session.commit()
    
    # WhatsApp Direct Push
    try:
        txt = f"💎 *PLATINUM LEAD*\n\n*Name:* {name}\n*Phone:* {phone}\n*Inquiry:* {msg}"
        requests.get(f"https://api.callmebot.com/whatsapp.php?phone=254796250286&text={txt.replace(' ','+')}&apikey=9531589")
    except: pass
    return jsonify({"status": "success"})

@app.route('/vault/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['auth'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/vault/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('auth'): return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            from werkzeug.utils import secure_filename
            fn = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            p = Property(title=request.form['title'], price=int(request.form['price']),
                         location=request.form['location'], category=request.form['category'],
                         beds=int(request.form['beds']), baths=int(request.form['baths']),
                         sqft=request.form['sqft'], details=request.form['details'],
                         image=f'uploads/{fn}')
            db.session.add(p)
            db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin.html', properties=Property.query.all(), leads=Lead.query.all())

@app.route('/system/rebuild')
def rebuild():
    db.drop_all()
    db.create_all()
    return "Database Optimized & Rebuilt."

if __name__ == '__main__':
    app.run(debug=True)