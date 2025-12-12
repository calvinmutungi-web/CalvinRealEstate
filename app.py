from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/gallery'
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-calvin-2025")

db = SQLAlchemy(app)

from models import Lead

# Create DB + folders on startup
with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if not os.path.exists("static/properties.json"):
        with open("static/properties.json", "w") as f:
            f.write("[]")
# After db.create_all()
os.makedirs("static/gallery", exist_ok=True)
if not os.path.exists("static/properties.json"):
    with open("static/properties.json", "w") as f:
        f.write("[]")
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact", methods=["POST"])
def contact():
    # ... your existing save code ...

    # Auto-reply message
    auto_reply = f"Thanks {name}! 🙌\nCalvin here from Calvin Real Estate.\nI just got your message and I'm on it.\nI'll call you in the next 30–60 mins to discuss your dream property.\n\nTalk soon!\nCalvin 0796 250 286"
    try:
        requests.get(
            "https://api.callmebot.com/whatsapp.php",
            params={
                "phone": "254796250286",  # your number
                "text": auto_reply,
                "apikey": "9531589"
            },
            timeout=8
        )
    except:
        pass

    return jsonify({"status": "success", "message": "Message received! Calvin will call you within 1 hour 🔥"})

    # Save to DB
    lead = Lead(name=name, email=email, message=message)
    db.session.add(lead)
    db.session.commit()

    # INSTANT WhatsApp Alert (your key already in)
    wa_text = f"NEW LEAD - Calvin Real Estate\n\nName: {name}\nEmail: {email}\nMessage: {message}\nTime: {datetime.utcnow().strftime('%b %d %H:%M')}"
    try:
        requests.get(
            "https://api.callmebot.com/whatsapp.php",
            params={
                "phone": "254796250286",
                "text": wa_text,
                "apikey": "9531589"   
            },
            timeout=10
        )
    except:
        pass

    return jsonify({"status": "success", "message": "Got it! Calling you in < 1 hour"})

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

    # Create gallery folder if missing
    os.makedirs("static/gallery", exist_ok=True)

    # Save image
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
    file.save(os.path.join("static/gallery", filename))

    # Update JSON
    new_prop = {"title": title, "price": price, "desc": desc, "img": filename}
    json_path = "static/properties.json"
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(new_prop)
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    return "Property added — refresh homepage now!"

if __name__ == "__main__":
    app.run()