import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'calvin_ultra_luxury_2025_vault'

# --- DATABASE CONFIG (SELF-HEALING) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'signature.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), default="Nairobi")
    category = db.Column(db.String(50), default="Villa")
    beds = db.Column(db.Integer, default=4)
    baths = db.Column(db.Integer, default=4)
    sqft = db.Column(db.String(20), default="4,500")
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)

# --- WHATSAPP NOTIFICATION (CallMeBot) ---
def send_whatsapp_alert(name, phone, msg):
    apikey = "9531589"
    target = "254796250286"
    text = f"💎 *NEW LUXURY LEAD*\n\n*Client:* {name}\n*Phone:* {phone}\n*Inquiry:* {msg}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={target}&text={text.replace(' ', '+')}&apikey={apikey}"
    try: requests.get(url, timeout=5)
    except: pass

# --- APP STARTUP ---
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    properties = Property.query.order_by(Property.id.desc()).all()
    return render_template('index.html', properties=properties)

@app.route('/inquire', methods=['POST'])
def inquire():
    name = request.form.get('name')
    phone = request.form.get('phone')
    msg = request.form.get('message')
    new_lead = Lead(name=name, phone=phone, message=msg)
    db.session.add(new_lead)
    db.session.commit()
    send_whatsapp_alert(name, phone, msg)
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

# FIXING YOUR 404: Use this exact URL to login
@app.route('/management/vault/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/management/vault/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_prop = Property(
                title=request.form['title'],
                price=int(request.form['price']),
                location=request.form['location'],
                category=request.form['category'],
                beds=request.form['beds'],
                baths=request.form['baths'],
                sqft=request.form['sqft'],
                details=request.form['details'],
                image=f'uploads/{filename}'
            )
            db.session.add(new_prop)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template('admin.html', properties=Property.query.all(), leads=Lead.query.all())

@app.route('/rebuild-system')
def rebuild():
    db.drop_all()
    db.create_all()
    return "System Synchronized. Database Rebuilt."

if __name__ == '__main__':
    app.run(debug=True)