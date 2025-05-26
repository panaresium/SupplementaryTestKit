import json
import os
from typing import Dict, Any

import openai

STORAGE_FILE = 'survey_data.json'

openai.api_key = os.getenv('OPENAI_API_KEY')


def _load_storage() -> list:
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def _save_storage(data: list):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def send_survey_to_openai(survey_data: Dict[str, Any]) -> str:
    """Send survey data to OpenAI and return the raw response text."""
    messages = [
        {"role": "system", "content": "You are a nutrition expert providing supplement suggestions."},
        {"role": "user", "content": f"Survey data: {json.dumps(survey_data)}"}
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"]


def summarize_supplements(text: str) -> str:
    """Summarize supplement suggestions from OpenAI's response."""
    messages = [
        {"role": "system", "content": "Summarize the supplement suggestions."},
        {"role": "user", "content": text}
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"].strip()


def record_survey_with_analysis(survey_data: Dict[str, Any]):
    """Store survey data and AI analysis together."""
    raw_analysis = send_survey_to_openai(survey_data)
    summary = summarize_supplements(raw_analysis)
    storage = _load_storage()
    storage.append({
        "survey": survey_data,
        "analysis": raw_analysis,
        "summary": summary
    })
    _save_storage(storage)

