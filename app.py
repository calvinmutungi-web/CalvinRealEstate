import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'calvin_vault_2025_ultimate'

# --- DATABASE CONFIG ---
# This ensures Render uses an absolute path so it never loses the file
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'luxury_v3.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db = SQLAlchemy(app)

# --- MODELS ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False) # Store as simple integer for stability
    location = db.Column(db.String(100), default="Nairobi")
    category = db.Column(db.String(50), default="Villa")
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# --- APP INITIALIZATION ---
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    try:
        properties = Property.query.all()
        return render_template('index.html', properties=properties)
    except Exception as e:
        # If the DB is broken, show a clean message instead of a 500 error
        return f"System updating. Please visit /setup-db to initialize. Error: {e}"

@app.route('/setup-db')
def setup_db():
    try:
        db.drop_all()
        db.create_all()
        return "<h1>SUCCESS: Database Rebuilt.</h1><p>You can now go to <a href='/admin'>Admin</a> and add properties.</p>"
    except Exception as e:
        return f"Setup Failed: {e}"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            file = request.files.get('image')
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                new_prop = Property(
                    title=request.form['title'],
                    price=int(request.form['price']),
                    location=request.form['location'],
                    category=request.form['category'],
                    details=request.form['details'],
                    image=f'uploads/{filename}'
                )
                db.session.add(new_prop)
                db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            return f"Error adding property: {e}"

    props = Property.query.all()
    leads = Lead.query.all()
    return render_template('admin.html', properties=props, leads=leads)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['admin_logged'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/contact', methods=['POST'])
def contact():
    try:
        new_lead = Lead(
            name=request.form.get('name'),
            email=request.form.get('email'),
            message=request.form.get('message')
        )
        db.session.add(new_lead)
        db.session.commit()
        return "Message Sent! We will contact you shortly."
    except:
        return "Error sending message."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)