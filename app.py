import os
import requests
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "signature_elite_2025"

# --- WHATSAPP CONFIG ---
def send_whatsapp_lead(name, phone, message):
    api_key = "9531589"
    my_number = "254796250286"
    
    # URL Encoding is critical for WhatsApp messages to send
    content = f"💎 *SIGNATURE LEAD*\n\n*Name:* {name}\n*Phone:* {phone}\n*Msg:* {message}"
    encoded_msg = requests.utils.quote(content)
    
    url = f"https://api.callmebot.com/whatsapp.php?phone={my_number}&text={encoded_msg}&apikey={api_key}"
    
    try:
        requests.get(url, timeout=5) # Fast timeout for mobile performance
    except:
        pass

# --- ROUTES ---

@app.route('/')
def index():
    # Load properties from the permanent JSON file
    try:
        with open('properties.json', 'r') as f:
            props = json.load(f)
    except:
        props = []
        
    return render_template('index.html', properties=props)

@app.route('/inquire', methods=['POST'])
def inquire():
    name = request.form.get('client_name')
    phone = request.form.get('client_phone')
    message = request.form.get('client_message')

    # Send WhatsApp alert immediately
    send_whatsapp_lead(name, phone, message)

    return jsonify({"status": "success"}), 200

# --- ADMIN ACCESS ---
@app.route('/vault/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'signature2025':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/vault/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)