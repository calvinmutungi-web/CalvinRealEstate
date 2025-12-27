import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)
# High-security secret key
app.secret_key = os.environ.get("SECRET_KEY", "signature_elite_2025_private_key")

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signature.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50)) 
    location = db.Column(db.String(100))
    category = db.Column(db.String(50)) 
    image = db.Column(db.String(500), default='property_default.jpg')
    source = db.Column(db.String(50), default='Manual') 
    is_elite = db.Column(db.Boolean, default=True)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- THE SCRAPER ENGINE ---
def sync_market_data():
    url = "https://www.buyrentkenya.com/listings?q=luxury"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('div', class_='flex-grow', limit=8) 
        for item in listings:
            title_node = item.find('h2') or item.find('a', class_='no-underline')
            if title_node:
                title = title_node.text.strip()
                if not Property.query.filter_by(title=title).first():
                    img_tag = item.find('img')
                    img_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else 'property_default.jpg'
                    price_node = item.find('p', class_='text-xl')
                    price_val = price_node.text.strip() if price_node else "Inquire"
                    new_prop = Property(title=title, location="Nairobi Region", category="Luxury Estate", source="BuyRentKenya", price=price_val, image=img_url)
                    db.session.add(new_prop)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Scraper Error: {e}")
        return False

# --- ROUTES ---

@app.route('/')
def index():
    q = request.args.get('q')
    cat = request.args.get('category')
    query = Property.query
    if q: query = query.filter(Property.location.icontains(q))
    if cat: query = query.filter_by(category=cat)
    props = query.order_by(Property.id.desc()).all()
    return render_template('index.html', properties=props)

@app.route('/inquire', methods=['POST'])
def inquire():
    name = request.form.get('client_name')
    phone = request.form.get('client_phone')
    message = request.form.get('client_message')

    if not name or not phone:
        return jsonify({"status": "error", "message": "Required fields missing"}), 400

    new_lead = Lead(name=name, phone=phone, message=message)
    db.session.add(new_lead)
    db.session.commit()

    # --- WHATSAPP BRIDGE ---
    WHATSAPP_INSTANCE = "instanceXXXX" # Replace with your UltraMsg Instance ID
    WHATSAPP_TOKEN = "tokenYYYY"       # Replace with your UltraMsg Token
    MY_NUMBER = "2547XXXXXXXX"         # Your number in international format

    url = f"https://api.ultramsg.com/{WHATSAPP_INSTANCE}/messages/chat"
    payload = {"token": WHATSAPP_TOKEN, "to": MY_NUMBER, "body": f"💎 *NEW LEAD*\n\n*Name:* {name}\n*Phone:* {phone}\n*Msg:* {message}"}
    
    try:
        requests.post(url, data=payload, timeout=5)
    except:
        pass 

    return jsonify({"status": "success", "message": "Consultation Initialized Successfully"}), 200

@app.route('/vault/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'signature2025':
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', error="Invalid Key")
    return render_template('login.html')

# FIXED: Added POST method to handle asset deployment
@app.route('/vault/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handles "Deploy Asset" from the admin panel
        new_p = Property(
            title=request.form.get('title'),
            price=request.form.get('price'),
            location=request.form.get('location'),
            category=request.form.get('category'),
            image=request.form.get('image'),
            source="Manual"
        )
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('admin'))

    leads = Lead.query.order_by(Lead.timestamp.desc()).all()
    properties = Property.query.order_by(Property.id.desc()).all()
    return render_template('admin.html', leads=leads, properties=properties)

@app.route('/vault/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/system/sync')
def run_sync():
    if sync_market_data(): return "Sync Complete."
    return "Sync Failed."

@app.route('/system/rebuild')
def rebuild():
    db.drop_all()
    db.create_all()
    return "DB Reset."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)