
# SupplementaryTestKit

This project provides a small demo application for a health questionnaire. A Flask backend serves the web UI from the `static/` directory and stores responses in SQLite. Translations for questions and UI strings are loaded from the JSON files in `static/`.

## Requirements

Python 3.8+ is required.

## Running the server

```bash
pip install -r requirements.txt
python app.py
```

The server listens on port `5000`. Open `http://localhost:5000/` in your browser to use the questionnaire.

Questionnaire answers are stored as JSON strings in the SQLite database.

# Supplementary Test Kit

This repository provides a minimal example of handling user submissions while respecting privacy.

## Features

1. **HTTPS Required**: The server is configured to run with a self-signed certificate in development. In production, run behind an HTTPS reverse proxy.
2. **User Consent**: The HTML form includes a mandatory consent checkbox linking to the privacy policy.
3. **Minimal Data Storage**: Only name, a hashed version of the email, and an optional comment are stored.
4. **Pseudonymization**: Email addresses are hashed before storage to reduce the risk of identifying individuals.

## Running

Install the dependencies and run the server as shown above. Then open `http://localhost:5000/` in your browser.

## Privacy Policy

Edit `static/privacy_policy.html` with the details of your actual policy.

