from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    # Here you would save to DB or send email
    print(f"New message from {name} ({email}): {message}")

    return jsonify({"status": "success", "message": "Message sent successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
