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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not all([name, email, message]) or len(message) > 2000:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

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
                "apikey": "9531589"   # ← YOUR KEY LOCKED IN
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

    title = request.form["title"]
    price = request.form["price"]
    desc = request.form["desc"]
    file = request.files["image"]

    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        import json
        new_prop = {"title": title, "price": price, "desc": desc, "img": filename}
        try:
            with open("static/properties.json", "r+") as f:
                data = json.load(f)
                data.append(new_prop)
                f.seek(0)
                json.dump(data, f, indent=2)
        except:
            with open("static/properties.json", "w") as f:
                json.dump([new_prop], f, indent=2)

    return "Property added – live instantly"

if __name__ == "__main__":
    app.run()