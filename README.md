
# SupplementaryTestKit

This project provides a small demo application for a health questionnaire. It uses Python's standard library and SQLite for storage. A web UI is served from the `static/` directory and the backend exposes JSON endpoints.

## Requirements

Python 3.8+ is required (no external packages).

## Running the server

```bash
python3 backend/server.py
```

The server listens on port `8000`. Open `http://localhost:8000/` in your browser to use the web interface.

### Endpoints

- `POST /register` – Register a new user. Body: `{"username": "name", "password": "secret"}`
- `POST /login` – Validate credentials. Body: `{"username": "name", "password": "secret"}`
- `POST /questionnaire` – Store questionnaire answers. Body: `{"username": "name", "answers": { ... }}`
- `GET /questionnaire/<username>` – Retrieve questionnaire entries for a user
- `POST /upload` – Upload an image using `multipart/form-data`. Field name `image`
- `GET /uploads/<file>` – Retrieve previously uploaded images

Questionnaire answers are stored as JSON strings in the SQLite database. Uploaded images are saved to the `uploads/` directory.

# Supplementary Test Kit

This repository provides a minimal example of handling user submissions while respecting privacy.

## Features

1. **HTTPS Required**: The server is configured to run with a self-signed certificate in development. In production, run behind an HTTPS reverse proxy.
2. **User Consent**: The HTML form includes a mandatory consent checkbox linking to the privacy policy.
3. **Minimal Data Storage**: Only name, a hashed version of the email, and an optional comment are stored.
4. **Pseudonymization**: Email addresses are hashed before storage to reduce the risk of identifying individuals.

## Running

Install the dependencies (Flask) and run the server:

```bash
pip install Flask
python server.py
```

Then open `https://localhost:5000/` in your browser. You may need to accept a self-signed certificate.

## Privacy Policy

Edit `static/privacy_policy.html` with the details of your actual policy.

