import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# This line tells the app to use the Render database you just set up
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the "Listing" structure for your database
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(200))
    image = db.Column(db.String(100))

@app.route("/")
def home():
    # This pulls properties from the DB instead of hardcoding them
    properties = Listing.query.all()
    return render_template("index.html", properties=properties)

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    print(f"Lead captured: {data.get('name')}")
    return jsonify({"status": "success", "message": "Inquiry received!"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # This creates the tables on Render automatically
    app.run(debug=True)
if __name__ == "__main__":
    with app.app_context():
        # This is the magic line that fixes the "UndefinedTable" error
        db.create_all() 
        print("Database tables created successfully!")
    app.run(debug=True)