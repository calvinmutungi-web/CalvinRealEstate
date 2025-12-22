import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# Connects to your Render PostgreSQL database
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
    image = db.Column(db.String(100)) # Stores names like 'pexels1.jpeg'

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# --- ROUTES ---

@app.route("/")
def home():
    try:
        # Pulls all houses from the PostgreSQL database
        properties = Listing.query.all()
        return render_template("index.html", properties=properties)
    except Exception:
        # Fallback if the database tables aren't created yet
        return "Site is initializing. Please visit /setup-db to prepare the database."

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/admin-add", methods=["POST"])
def admin_add():
    # Verify the password 'calvin2025' from your form
    password = request.form.get("pw")
    if password != "calvin2025":
        return "Unauthorized Access", 401

    # Create the new house object from form data
    new_house = Listing(
        title=request.form.get("title"),
        price=request.form.get("price"),
        details=request.form.get("desc"),
        image=request.form.get("image_name")
    )
    db.session.add(new_house)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/delete-property/<int:id>")
def delete_property(id):
    prop = Listing.query.get_or_404(id)
    db.session.delete(prop)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/setup-db")
def setup_db():
    # Force creates the 'listing' and 'lead' tables
    db.create_all()
    return "Database Ready! You can now go to /admin to add your properties."

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    new_lead = Lead(name=data.get('name'), email=data.get('email'), message=data.get('message'))
    db.session.add(new_lead)
    db.session.commit()
    return jsonify({"status": "success", "message": "Inquiry received!"})

if __name__ == "__main__":
    app.run(debug=True)