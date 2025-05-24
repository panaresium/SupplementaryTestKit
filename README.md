# SupplementaryTestKit

This project provides a minimal backend prototype for the health questionnaire application.
It uses Python standard library modules and SQLite for data storage. The server exposes
simple JSON endpoints for user registration, login and questionnaire submission.

## Requirements

The environment should have Python 3 installed. No external packages are required.

## Running the server

```
python3 backend/server.py
```

The server listens on port `8000` by default. Open `http://localhost:8000/` in a browser to use the simple web interface.

### Endpoints

- `POST /register` – Register a new user. Body: `{"username": "name", "password": "secret"}`
- `POST /login` – Validate credentials. Body: `{"username": "name", "password": "secret"}`
- `POST /questionnaire` – Store questionnaire answers. Body:
  `{"username": "name", "answers": { ... }}`
- `POST /upload` – Upload an image file using `multipart/form-data`. Returns the path to the stored file.
- `GET /questionnaire/<username>` – Retrieve all questionnaire entries for the user.

Questionnaire answers are stored as raw JSON strings in the SQLite database.
