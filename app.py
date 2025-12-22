import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Config
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

# --- ROUTES ---
@app.route("/")
def home():
    try:
        properties = Listing.query.all()
        return render_template("index.html", properties=properties)
    except Exception as e:
        return f"Database Error: {e}" # This will tell us EXACTLY why it's failing instead of a generic 500

@app.route("/contact", methods=["POST"])
def contact():
    # Your existing contact logic
    return jsonify({"status": "success", "message": "Inquiry received!"})

# THIS BLOCK CREATES THE TABLES
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)