from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect  # God-tier security
from flask_caching import Cache  # For scalability
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import requests
import urllib.parse
import logging
import structlog  # Fancy logging
from PIL import Image  # Image processing
import numpy as np  # For recommendations

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_super_secret_key')  # No more crashes on missing env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit uploads to 16MB
app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY')
app.config['CACHE_TYPE'] = 'SimpleCache'  # Or Redis for prod
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Logging setup
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
cache = Cache(app)

# CallMeBot from env/screenshot
ADMIN_PHONE = os.environ.get('ADMIN_WHATSAPP_PHONE', '+254796250286')
CALLMEBOT_KEY = os.environ.get('CALLMEBOT_APIKEY', '9531589')

# Models
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    sqm = db.Column(db.Integer)
    category = db.Column(db.String(50))
    details = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # For recommendations: Simple embedding (e.g., one-hot or basic vector)
    embedding = db.Column(db.PickleType)  # Store numpy array

ADMIN_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'supersecurepassword'))

@app.errorhandler(404)
def not_found(e):
    logger.error("404 error", path=request.path)
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error("500 error", exc_info=True)
    return jsonify({"error": "Server error"}), 500

@cache.cached(timeout=300, key_prefix='listings')
def get_listings():
    return Listing.query.all()

@app.route("/")
def home():
    listings = get_listings()
    featured = listings[:2]
    gallery = listings[2:]
    return render_template("index.html", featured=featured, gallery=gallery, maps_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route("/contact", methods=["POST"])
@csrf.exempt  # If API, but protect in prod
def contact():
    data = request.json
    if not data or not all(key in data for key in ['name', 'email', 'message']):
        logger.warning("Invalid contact data")
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    lead = Lead(name=data['name'], email=data['email'], message=data['message'])
    db.session.add(lead)
    db.session.commit()
    text = f"New High-End Lead!\nName: {data['name']}\nEmail: {data['email']}\nInquiry: {data['message']}"
    encoded = urllib.parse.quote(text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={ADMIN_PHONE}&text={encoded}&apikey={CALLMEBOT_KEY}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            logger.error("CallMeBot failed", status=resp.status_code, text=resp.text)
    except Exception as e:
        logger.error("CallMeBot exception", exc_info=True)
    return jsonify({"status": "success", "message": "Inquiry received. Expect WhatsApp contact."})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if check_password_hash(ADMIN_HASH, request.form.get("password", "")):
            session['admin'] = True
            logger.info("Admin login success")
            return redirect(url_for('admin'))
        flash("Wrong password. Try again, champ.")
        logger.warning("Admin login fail")
    return render_template("login.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == "POST":
        file = request.files.get('image')
        image_url = None
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            # Resize for god-tier performance
            img = Image.open(path)
            img.thumbnail((800, 800))
            img.save(path)
            image_url = url_for('static', filename=f'uploads/{filename}')
        listing = Listing(
            title=request.form['title'],
            price=int(request.form.get('price', 0)),
            location=request.form['location'],
            bedrooms=int(request.form.get('beds', 0)),
            bathrooms=int(request.form.get('baths', 0)),
            sqm=int(request.form.get('sqm', 0)),
            category=request.form['category'],
            details=request.form['details'],
            image_url=image_url
        )
        # Innovative: Simple embedding for recs (e.g., vector from category, beds, etc.)
        listing.embedding = np.array([listing.bedrooms or 0, listing.bathrooms or 0, listing.sqm or 0, listing.price / 1e6])
        db.session.add(listing)
        db.session.commit()
        cache.clear()
        flash("Asset deployed flawlessly.")
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    listings = get_listings()
    return render_template("admin.html", leads=leads, listings=listings)

@app.route("/admin/delete_lead/<int:id>", methods=["POST"])
def delete_lead(id):
    if not session.get('admin'): return '', 403
    lead = Lead.query.get(id)
    if lead:
        db.session.delete(lead)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin/delete_listing/<int:id>", methods=["POST"])
def delete_listing(id):
    if not session.get('admin'): return '', 403
    listing = Listing.query.get(id)
    if listing:
        if listing.image_url:
            path = listing.image_url.lstrip('/').replace('static/', 'static/')
            if os.path.exists(path):
                os.remove(path)
        db.session.delete(listing)
        db.session.commit()
        cache.clear()
    return redirect(url_for('admin'))

@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json.get('preferences', {})
    user_vec = np.array([data.get('beds', 0), data.get('baths', 0), data.get('sqm', 0), data.get('price', 0) / 1e6])
    listings = get_listings()
    scores = [np.dot(user_vec, l.embedding) / (np.linalg.norm(user_vec) * np.linalg.norm(l.embedding)) if l.embedding is not None else 0 for l in listings]
    top_idx = np.argsort(scores)[-3:]
    recs = [listings[i] for i in top_idx]
    return jsonify([{'title': r.title, 'price': r.price} for r in recs])

@app.route("/sitemap.xml")
def sitemap():
    listings = get_listings()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '  <url><loc>https://yourdomain.com/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    for l in listings:
        xml += f'  <url><loc>https://yourdomain.com/property/{l.id}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
    xml += '</urlset>'
    resp = make_response(xml)
    resp.headers["Content-Type"] = "application/xml"
    return resp

@app.before_first_request
def init_db():
    db.create_all()
    if Listing.query.count() == 0:
        try:
            with open('properties.json') as f:
                data = json.load(f)
                for p in data:
                    price_str = p['price'].replace('KSh ', '').replace(',', '').replace('Price Upon Request', '0')
                    price = int(price_str) if price_str.isdigit() else 0
                    embedding = np.array([p.get('beds', 0), p.get('baths', 0), p.get('sqm', 0), price / 1e6])
                    listing = Listing(title=p['title'], price=price, location=p['location'], category=p['category'], image_url=p['image'], embedding=embedding)
                    db.session.add(listing)
                db.session.commit()
                logger.info("DB seeded")
        except Exception as e:
            logger.error("Seeding failed", exc_info=True)

if __name__ == "__main__":
    app.run(debug=True)