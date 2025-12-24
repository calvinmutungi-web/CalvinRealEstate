import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'calvin_ultra_premium_2025'

# --- DATABASE SETUP (FIXES ERROR 500) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'calvin_hq.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# --- MODELS ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), default="Nairobi")
    category = db.Column(db.String(50), default="Villa")
    beds = db.Column(db.Integer, default=4)
    baths = db.Column(db.Integer, default=4)
    sqft = db.Column(db.String(20), default="3,500")
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)

# --- WHATSAPP LOGIC ---
def notify_calvin(name, phone, message):
    api_key = "9531589"
    my_phone = "254796250286"
    text = f"*New High-End Lead!*\n\n*Name:* {name}\n*Phone:* {phone}\n*Inquiry:* {message}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={my_phone}&text={text.replace(' ', '+')}&apikey={api_key}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- INITIALIZE SYSTEM ---
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

@app.route('/')
def index():
    props = Property.query.order_by(Property.id.desc()).all()
    return render_template('index.html', properties=props)

@app.route('/inquire', methods=['POST'])
def inquire():
    name = request.form.get('name')
    phone = request.form.get('phone')
    msg = request.form.get('message')
    new_lead = Lead(name=name, phone=phone, message=msg)
    db.session.add(new_lead)
    db.session.commit()
    notify_calvin(name, phone, msg)
    return "SUCCESS"

@app.route('/secret-vault-login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['auth'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('auth'): return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            from werkzeug.utils import secure_filename
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

@app.route('/delete/<int:id>')
def delete(id):
    Property.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/rebuild-db')
def rebuild():
    db.drop_all()
    db.create_all()
    return "<h1>Database Cleared & Synchronized.</h1><p>The Error 500 is gone. <a href='/admin'>Go to Admin</a></p>"

if __name__ == '__main__':
    app.run(debug=True)