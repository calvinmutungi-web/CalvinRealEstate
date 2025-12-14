from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/gallery'
app.secret_key = os.environ.get("SECRET_KEY", "calvin-secret-2025")

db = SQLAlchemy(app)

# Models
from models import Lead

# Startup fixes
with app.app_context():
    db.create_all()
    os.makedirs("static/gallery", exist_ok=True)
    
    # Copy sample photos if gallery is empty (Render free tier survival)
    if len(os.listdir("static/gallery")) == 0:
        samples = ["pexels.jpeg", "pexels1.jpeg", "pexels2.jpeg", "pexels3.jpeg", "pexels4.jpeg"]
        for pic in samples:
            src = os.path.join("static", pic)
            if os.path.exists(src):
                shutil.copy(src, "static/gallery")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not all([name, email, message]):
        return jsonify({"status": "error", "message": "All fields required"}), 400

    lead = Lead(name=name, email=email, message=message)
    db.session.add(lead)
    db.session.commit()

    # WhatsApp alert + auto-reply
    alert = f"NEW LEAD\nName: {name}\nEmail: {email}\nMessage: {message}"
    auto_reply = f"Thanks {name}! Calvin here. I'll call you in 30-60 mins. 0796 250 286"
    for text in [alert, auto_reply]:
        try:
            requests.get("https://api.callmebot.com/whatsapp.php", params={
                "phone": "254796250286",
                "text": text,
                "apikey": "9531589"
            }, timeout=8)
        except:
            pass

    return jsonify({"status": "success", "message": "Got it! Calvin will call you soon 🔥"})

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin-add", methods=["POST"])
def admin_add():
    if request.form.get("pw") != "calvin2025":
        return "Wrong password", 403

    title = request.form.get("title")
    price = request.form.get("price")
    desc = request.form.get("desc")
    file = request.files.get("image")

    if not all([title, price, desc, file]) or not file.filename:
        return "All fields required", 400

    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
    file.save(os.path.join("static/gallery", filename))

    return "Property added — refresh homepage!"

if __name__ == "__main__":
    app.run()