import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'calvin_luxury_vault_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agency.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# --- MODELS ---
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), default="Nairobi")
    category = db.Column(db.String(50), default="Villa")
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# --- ROUTES ---
@app.route('/')
def index():
    # Fetch properties for the high-end grid
    properties = Property.query.all()
    return render_template('index.html', properties=properties)

@app.route('/contact', methods=['POST'])
def contact():
    new_lead = Lead(
        name=request.form.get('name'),
        email=request.form.get('email'),
        message=request.form.get('message')
    )
    db.session.add(new_lead)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'calvin' and request.form['p'] == 'vault2025':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'): return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['image']
        if file:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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

    # Load everything for the admin dashboard
    props = Property.query.all()
    leads = Lead.query.all()
    return render_template('admin.html', properties=props, leads=leads)

@app.route('/delete/<int:id>')
def delete(id):
    Property.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/setup-db')
def setup():
    db.create_all()
    return "Database sync successful. Admin and Contacts fixed!"

if __name__ == '__main__':
    app.run(debug=True)