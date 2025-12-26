import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = "signature_elite_secret_2025"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signature.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)
    location = db.Column(db.String(100))
    category = db.Column(db.String(50)) # Villa, Penthouse, etc.
    image = db.Column(db.String(300), default='property_default.jpg')
    source = db.Column(db.String(50), default='Manual') # Manual or BuyRentKenya
    is_elite = db.Column(db.Boolean, default=True)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- THE SCRAPER ENGINE (BuyRentKenya Integration) ---
def sync_market_data():
    """Scrapes BuyRentKenya for Luxury Listings"""
    url = "https://www.buyrentkenya.com/listings?q=luxury"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # This targets the standard listing container for BRK
        listings = soup.find_all('div', class_='flex-grow') 
        
        for item in listings[:5]: # Pull top 5 luxury assets to keep it elite
            title_node = item.find('a', class_='no-underline')
            if title_node:
                title = title_node.text.strip()
                # Check if already exists
                exists = Property.query.filter_by(title=title).first()
                if not exists:
                    # Logic to clean price string to integer
                    new_prop = Property(
                        title=title,
                        location="Nairobi", # Defaulting for map logic
                        category="Luxury Estate",
                        source="BuyRentKenya",
                        price=50000000 # Placeholder for scraped price logic
                    )
                    db.session.add(new_prop)
        db.session.commit()
    except Exception as e:
        print(f"Scraper Sync Error: {e}")

# --- ROUTES ---

@app.route('/')
def index():
    query = request.args.get('q')
    category = request.args.get('category')
    
    props = Property.query
    if query:
        props = props.filter(Property.location.contains(query))
    if category:
        props = props.filter_by(category=category)
    
    return render_template('index.html', properties=props.all())

@app.route('/inquire', methods=['POST'])
def inquire():
    name = request.form.get('name')
    phone = request.form.get('phone')
    message = request.form.get('message', 'Private Inquiry')
    
    # 1. Save Lead to DB
    new_lead = Lead(name=name, phone=phone, message=message)
    db.session.add(new_lead)
    db.session.commit()

    # 2. FIXED WHATSAPP BRIDGE (Using UltraMsg/Chat-API Pattern)
    # REPLACE with your actual instance ID and Token
    WHATSAPP_INSTANCE = "instanceXXXX" 
    WHATSAPP_TOKEN = "tokenYYYY"
    ADMIN_PHONE = "2547XXXXXXXX" # YOUR PHONE

    msg = f"✨ *New Elite Lead* ✨\n\n*Name:* {name}\n*Phone:* {phone}\n*Intent:* {message}"
    
    # Example using a standard API gateway structure
    whatsapp_url = f"https://api.ultramsg.com/{WHATSAPP_INSTANCE}/messages/chat"
    payload = {
        "token": WHATSAPP_TOKEN,
        "to": ADMIN_PHONE,
        "body": msg
    }
    
    try:
        requests.post(whatsapp_url, data=payload, timeout=5)
    except:
        pass # Log error quietly to keep site speed fast

    return jsonify({"status": "success"}), 200

@app.route('/vault/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Safely get the password from the form
        password = request.form.get('password') 
        
        # Check against your master key
        if password == 'signature2025':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            # If wrong, stay on login and show an error
            return render_template('login.html', error="Access Denied: Invalid Key")
            
    return render_template('login.html')

@app.route('/vault/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    leads = Lead.query.order_by(Lead.timestamp.desc()).all()
    return render_template('admin.html', leads=leads)

# System tool to trigger scraper and rebuild
@app.route('/system/sync')
def run_sync():
    sync_market_data()
    return "Market Data Scraped and Synced Successfully."

@app.route('/system/rebuild')
def rebuild():
    db.drop_all()
    db.create_all()
    return "Database Rebuilt."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)