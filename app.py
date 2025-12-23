import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'calvin_vault_2025_ultimate'

# DATABASE CONFIG
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'luxury.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# MODELS
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    location = db.Column(db.String(100), default="Nairobi")
    category = db.Column(db.String(50), default="Villa")
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# INITIALIZE DIRECTORIES
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    properties = Property.query.all()
    return render_template('index.html', properties=properties)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            file = request.files['image']
            if file:
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
            return f"ADMIN UPLOAD ERROR: {str(e)}"

    props = Property.query.all()
    leads = Lead.query.all()
    return render_template('admin.html', properties=props, leads=leads)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Hardcoded credentials for your security
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['admin_logged'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/force-reset-db')
def force_reset():
    db.drop_all()
    db.create_all()
    return "Database Cleaned. Go to /admin now."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)