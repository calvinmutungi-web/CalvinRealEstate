import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'calvin_the_one_and_only_2025'

# --- DATABASE & PATH CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'calvin_godtier.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Max Upload

db = SQLAlchemy(app)

# --- MODELS (Luxury Schema) ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), default="Nairobi")
    category = db.Column(db.String(50), default="Penthouse")
    beds = db.Column(db.Integer, default=4)
    baths = db.Column(db.Integer, default=4)
    sqft = db.Column(db.String(20), default="5,000")
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- WHATSAPP CONCIERGE API ---
def notify_calvin(name, phone, message):
    api_key = "9531589"
    target = "254796250286"
    text = f"⚜️ *NEW ELITE LEAD*\n\n*Client:* {name}\n*Contact:* {phone}\n*Inquiry:* {message}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={target}&text={text.replace(' ', '+')}&apikey={api_key}"
    try:
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"WhatsApp Notify Failed: {e}")

# --- SELF-HEALING STARTUP ---
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# --- ERROR HANDLERS (Luxury Branding) ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404 # Redirect home instead of showing ugly 404

@app.errorhandler(500)
def internal_error(e):
    return "<h1>Luxury Maintenance in Progress.</h1>", 500

# --- ROUTES ---

@app.route('/')
def index():
    properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('index.html', properties=properties)

@app.route('/inquire', methods=['POST'])
def inquire():
    name = request.form.get('name')
    phone = request.form.get('phone')
    msg = request.form.get('message')
    
    lead = Lead(name=name, phone=phone, message=msg)
    db.session.add(lead)
    db.session.commit()
    
    notify_calvin(name, phone, msg)
    return redirect(url_for('index', success="true"))

# --- SECURE VAULT (Admin) ---

@app.route('/vault/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Replace with your ultra-secure credentials
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['elite_auth'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/vault/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('elite_auth'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        file = request.files.get('image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_prop = Property(
                title=request.form['title'],
                price=int(request.form['price']),
                location=request.form['location'],
                category=request.form['category'],
                beds=int(request.form['beds']),
                baths=int(request.form['baths']),
                sqft=request.form['sqft'],
                details=request.form['details'],
                image=f'uploads/{filename}'
            )
            db.session.add(new_prop)
            db.session.commit()
            return redirect(url_for('admin'))
            
    properties = Property.query.all()
    leads = Lead.query.order_by(Lead.timestamp.desc()).all()
    return render_template('admin.html', properties=properties, leads=leads)

@app.route('/vault/delete/<int:id>')
def delete(id):
    if not session.get('elite_auth'): return abort(403)
    p = Property.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/system/sync')
def sync():
    """Forces the DB to update its structure without deleting data"""
    db.create_all()
    return "<h1>System Synchronized.</h1><p><a href='/'>Return Home</a></p>"

if __name__ == '__main__':
    app.run(debug=True)