# SupplementaryTestKit

This project provides a small demo application for a health questionnaire.
It uses only Python's standard library and SQLite for storage. A tiny web UI is
served from the `static/` directory and the backend exposes JSON endpoints.

## Requirements

Python 3.8+ is required (no external packages).

## Running the server

```bash
python3 backend/server.py
```

The server listens on port `8000`.
Open `http://localhost:8000/` in your browser to use the web interface.


### Endpoints

- `POST /register` – Register a new user. Body: `{"username": "name", "password": "secret"}`
- `POST /login` – Validate credentials. Body: `{"username": "name", "password": "secret"}`
- `POST /questionnaire` – Store questionnaire answers. Body: `{"username": "name", "answers": { ... }}`
- `GET /questionnaire/<username>` – Retrieve questionnaire entries for a user
- `POST /upload` – Upload an image using `multipart/form-data`. Field name `image`
- `GET /uploads/<file>` – Retrieve previously uploaded images

Questionnaire answers are stored as JSON strings in the SQLite database.
Uploaded images are saved to the `uploads/` directory.
