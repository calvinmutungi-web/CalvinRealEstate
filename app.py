import os
from flask import Flask, render_template, request, jsonify
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

# --- THE SECRET FIX ROUTE ---
@app.route("/setup-db")
def setup_db():
    try:
        db.create_all()
        # Check if we already have listings so we don't double-add
        if Listing.query.count() == 0:
            sample_houses = [
                Listing(title='Luxury Villa', price='$250,000', details='5 Beds • 4 Baths', image='pexels2.jpeg'),
                Listing(title='Modern Apartment', price='$120,000', details='3 Beds • 2 Baths', image='pexels3.jpeg'),
                Listing(title='Family House', price='$180,000', details='4 Beds • 3 Baths', image='pexels1.jpeg'),
                Listing(title='Countryside Home', price='$150,000', details='2 Beds • 1 Bath', image='pexels4.jpeg')
            ]
            db.session.add_all(sample_houses)
            db.session.commit()
        return "Database tables created and seeded successfully! Go back to the home page."
    except Exception as e:
        return f"Setup Error: {e}"

@app.route("/")
def home():
    try:
        properties = Listing.query.all()
        return render_template("index.html", properties=properties)
    except Exception:
        # If the DB isn't ready, show a friendly message or redirect to setup
        return "Site is initializing. Please visit /setup-db to prepare the database."

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    new_lead = Lead(name=data.get('name'), email=data.get('email'), message=data.get('message'))
    db.session.add(new_lead)
    db.session.commit()
    return jsonify({"status": "success", "message": "Inquiry received!"})

if __name__ == "__main__":
    app.run(debug=True)