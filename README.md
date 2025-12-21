CalvinRealEstate

A real estate property dashboard built for Kenyan agents to showcase listings, manage inquiries, and present a modern, premium-facing web experience.

Live demo: [https://calvinrealestate-3.onrender.com/](https://calvinrealestate-3.onrender.com/)

---

Overview

CalvinRealEstate is a Flask-based web application designed to provide a clean, fast, and visually premium platform for real estate listings. It focuses on simplicity, speed, and a polished UI suitable for agents and small firms operating in the Kenyan real estate market.

The project emphasizes:

* Clear property presentation
* Responsive design
* Dark-mode premium styling
* Simple deployment and iteration

---

## Screenshots

### Homepage
![Homepage](screenshots/home.png)

### Listings
![Listings](screenshots/listings.png)

### Dark Mode
![Dark Mode](screenshots/dark-mode.png)
---

## Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** HTML, CSS, JavaScript
* **Templating:** Jinja2
* **Deployment:** Render (Procfile included)

---

## Project Structure

```
CalvinRealEstate/
│
├── app.py              # Main Flask application
├── models.py           # Data models and logic
├── templates/          # HTML templates (Jinja2)
├── static/             # CSS, JavaScript, images
├── Procfile            # Deployment configuration
├── .vscode/            # Editor configuration
└── README.md           # Project documentation
```

---

## Setup Instructions

### Requirements

Create a `requirements.txt` file with the following content:

```
flask
```

This allows consistent installs and clean deployment.

### 1. Clone the repository

```bash
git clone https://github.com/calvinmutungi-web/CalvinRealEstate.git
cd CalvinRealEstate
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask
```

> Note: Dependencies are minimal and intentionally kept simple.

### 4. Run the application

```bash
python app.py
```

The app will be available at:

```
http://127.0.0.1:5000
```

---

## Deployment

This project is configured for deployment on Render using the included `Procfile`.

Basic flow:

1. Push changes to the `main` branch
2. Render pulls the repo
3. App is built and served automatically

---

## Status

This project is actively developed and iterated. Features and UI enhancements are added continuously.

---

## License

This project is open for learning, experimentation, and extension. Attribution appreciated.
