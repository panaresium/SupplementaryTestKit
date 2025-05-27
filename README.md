# SupplementaryTestKit

This project provides a small Flask application that serves a multi-language health questionnaire. Answers are stored in a SQLite database and results are shown with optional AI-generated suggestions.

## Requirements

* Python 3.8+
* Packages listed in `requirements.txt`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

## Running

Start the Flask server with:
```bash
python app.py
```
The application will be available at `http://localhost:5000/`.

## Development


Tests can be run with `pytest`.

The questionnaire text and translations are stored in `static/questionnaire_structure.json` and rendered dynamically by `static/script.js`.

