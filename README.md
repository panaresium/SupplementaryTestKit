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
