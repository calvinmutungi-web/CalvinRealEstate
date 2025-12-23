import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'luxury_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///properties.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit for speed

db = SQLAlchemy(app)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True) # Villa or Apartment
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)

# --- DATABASE REPAIR ROUTE ---
@app.route('/setup-db')
def setup_db():
    db.drop_all()
    db.create_all()
    return "Database Optimized & Reset! You can now use the Admin panel."

@app.route('/')
def index():
    q = request.args.get('q', '')
    cat = request.args.get('category', '')
    max_p = request.args.get('price')
    
    query = Listing.query
    if q: query = query.filter(Listing.location.contains(q) | Listing.title.contains(q))
    if cat: query = query.filter_by(category=cat)
    if max_p: query = query.filter(Listing.price <= int(max_p))
    
    properties = query.all()
    return render_template('index.html', properties=properties)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'calvin' and request.form['password'] == 'vault2025':
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_prop = Listing(
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
            
    properties = Listing.query.all()
    return render_template('admin.html', properties=properties)

@app.route('/delete/<int:id>')
def delete(id):
    p = Listing.query.get(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)