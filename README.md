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
The value should appear exactly as in the OpenAI dashboard with no quotes or
trailing spaces. Quoting the key (e.g. `OPENAI_API_KEY="sk-..."`) will cause a
"Malformed API key" error.

You can also set the model used for AI suggestions with the `OPENAI_MODEL`
environment variable. If not provided, the application defaults to
`gpt-3.5-turbo`.

### Configuring your OpenAI API key

If you prefer not to use a `.env` file, you can set the key in other ways:

* Set the environment variable directly before running the application:
  ```bash
  export OPENAI_API_KEY=your-key-here
  ```
* Assign it in code with `openai.api_key = "your-key-here"`.
* Point the OpenAI library to a file containing the key using `openai.api_key_path = "/path/to/key.txt"`.

You can generate API keys in the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

## Running

Start the Flask server with:
```bash
python app.py
```
The application will be available at `http://localhost:5000/`.
You may set `OPENAI_MODEL` before running if you want to use a different
OpenAI model.

## Development


Tests can be run with `pytest`.

The questionnaire text and translations are stored in `static/questionnaire_structure.json` and rendered dynamically by `static/script.js`.

### CSV Import/Export

From the admin results page you can export all responses to a CSV file or import
responses from a CSV created by the same export feature. The import form accepts
a `.csv` file and adds any new rows to the database.

