import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIG ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(200))
    image = db.Column(db.String(100))

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# --- ROUTES ---
@app.route("/")
def home():
    try:
        properties = Listing.query.all()
        return render_template("index.html", properties=properties)
    except Exception:
        return "Site is initializing. Please visit /setup-db"

@app.route("/admin")
def admin_page():
    properties = Listing.query.all()
    leads = Lead.query.all()
    return render_template("admin.html", properties=properties, leads=leads)

@app.route("/admin-add", methods=["POST"])
def admin_add():
    if request.form.get("pw") != "calvin2025":
        return "Unauthorized", 401
    new_house = Listing(
        title=request.form.get("title"),
        price=request.form.get("price"),
        details=request.form.get("desc"),
        image=request.form.get("image_name")
    )
    db.session.add(new_house)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route("/delete-property/<int:id>", methods=["POST"])
def delete_property(id):
    if request.form.get("pw") != "calvin2025":
        return "Unauthorized", 401
    prop = Listing.query.get_or_404(id)
    db.session.delete(prop)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route("/setup-db")
def setup_db():
    db.create_all()
    return "Database Ready!"

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    new_lead = Lead(name=data.get('name'), email=data.get('email'), message=data.get('message'))
    db.session.add(new_lead)
    db.session.commit()
    return jsonify({"status": "success", "message": "Inquiry Sent Successfully!"})

if __name__ == "__main__":
    app.run(debug=True)