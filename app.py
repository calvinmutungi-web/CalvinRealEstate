import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "calvin_agency_luxury_key_2025"

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
    price = db.Column(db.Integer, nullable=False) # Store as integer for filtering
    details = db.Column(db.String(200))
    image = db.Column(db.String(100))
    category = db.Column(db.String(50)) # Fixed: This caused your 500 error

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# --- PROTECTION ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---
@app.route("/")
def home():
    q = request.args.get('q', '')
    max_p = request.args.get('price', type=int)
    cat = request.args.get('category', '')

    query = Listing.query
    if q:
        query = query.filter(Listing.title.ilike(f'%{q}%'))
    if max_p:
        query = query.filter(Listing.price <= max_p)
    if cat:
        query = query.filter(Listing.category == cat)
    
    properties = query.all()
    return render_template("index.html", properties=properties)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        if request.form.get("password") == "calvin2025":
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return "Invalid Credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route("/admin")
@login_required
def admin_dashboard():
    properties = Listing.query.all()
    leads = Lead.query.all()
    return render_template("admin.html", properties=properties, leads=leads)

@app.route("/admin-add", methods=["POST"])
@login_required
def admin_add():
    try:
        # Convert price string to integer (remove commas if user types them)
        raw_price = request.form.get("price").replace(",", "")
        new_house = Listing(
            title=request.form.get("title"),
            price=int(raw_price),
            details=request.form.get("desc"),
            image=request.form.get("image_name"),
            category=request.form.get("category")
        )
        db.session.add(new_house)
        db.session.commit()
    except Exception as e:
        return f"Error adding property: {e}"
    return redirect(url_for('admin_dashboard'))

@app.route("/delete-property/<int:id>", methods=["POST"])
@login_required
def delete_property(id):
    prop = Listing.query.get_or_404(id)
    db.session.delete(prop)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/setup-db")
def setup_db():
    # BULLETPROOF FIX: This resets the table to add the missing 'category' column
    db.drop_all() 
    db.create_all()
    return "Database Synchronized! All columns are now present."

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    new_lead = Lead(name=data.get('name'), email=data.get('email'), message=data.get('message'))
    db.session.add(new_lead)
    db.session.commit()
    return jsonify({"status": "success", "message": "Inquiry Sent Successfully!"})

if __name__ == "__main__":
    app.run(debug=True)