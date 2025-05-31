import pytest
from app import (
    _calculate_scores,
    _generate_recommendation,
    _load_questionnaire_structure,
    GROUP_NAMES,
    GROUP_NAMES_LOCALIZED,
    DB_PATH as APP_DB_PATH,
    init_db,
    GROUP_IDS,
    LANGUAGE_NAMES,
    # GROUP_INFO_FILE as APP_GROUP_INFO_FILE, # We will patch app.GROUP_INFO_FILE directly
)
import json
import sqlite3
import csv
import io
import os
import tempfile

# It's better to import the app instance itself for configuring
from app import app as flask_app


@pytest.fixture
def client():
    db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")

    # Store original DB_PATH from app.py and override it for tests
    original_db_path = APP_DB_PATH # This refers to the original DB_PATH from app.py

    # Modify flask_app.DB_PATH if app.py uses flask_app.config['DB_PATH']
    # If app.py uses a global 'DB_PATH' variable directly, we need to patch that.
    # For this exercise, let's assume app.py's DB_PATH can be influenced via flask_app.DB_PATH
    # or by patching the 'app.DB_PATH' directly.
    # The most direct way if app.py's global DB_PATH is used is to patch it.

    flask_app.config.update({
        "TESTING": True,
        # We will patch app.DB_PATH directly instead of using app.config for this path
        # because the functions in app.py use the global DB_PATH.
    })

    # Patch the DB_PATH in the 'app' module directly
    import app as app_module
    original_module_db_path = app_module.DB_PATH
    app_module.DB_PATH = temp_db_path

    with flask_app.app_context():
        init_db() # Initialize schema in the temporary database using the patched DB_PATH

    with flask_app.test_client() as client:
        yield client

    # Clean up: close and remove the temporary database file
    os.close(db_fd)
    os.unlink(temp_db_path)
    # Restore original DB_PATH in the module
    app_module.DB_PATH = original_module_db_path


@pytest.fixture
def temp_group_info_file_fixture(monkeypatch):
    # This fixture provides a temporary path for group_info.json and ensures it's cleaned up.
    # It also ensures the app module uses this temporary path.
    # It initializes the temp file with valid empty JSON structure for each group.
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".json")

    import app as app_module
    original_group_info_file = app_module.GROUP_INFO_FILE
    monkeypatch.setattr(app_module, 'GROUP_INFO_FILE', tmp_path)

    # Initialize with default structure expected by _load_group_info
    # to prevent errors if the file is initially empty or non-existent.
    initial_data = {}
    for gid in GROUP_IDS:
        messages = {lang: "" for lang in LANGUAGE_NAMES.keys()}
        initial_data[gid] = {"messages": messages, "image": ""}
    with open(tmp_path, 'w') as f:
        json.dump(initial_data, f)

    yield tmp_path

    os.close(tmp_fd)
    os.unlink(tmp_path)
    # No need to restore original_group_info_file with monkeypatch, it handles it.

from unittest.mock import patch
from urllib.parse import quote


# Sample questionnaire structure for testing
# In a real application, this might be loaded from a fixture or a test-specific file
# For now, we can use a simplified version or load the actual structure.
SAMPLE_STRUCTURE = {
    "questions": [
        {
            "id": "q1_radio",
            "type": "radio",
            "questionText": {"en": "Q1 Radio English", "fr": "Q1 Radio French"},
            "answers": [
                {"value": "a1", "text": {"en": "A1 English", "fr": "A1 French"}, "weights": {"G1": 10, "G2": 5}},
                {"value": "a2", "text": {"en": "A2 English", "fr": "A2 French"}, "weights": {"G3": 8}},
            ],
        },
        {
            "id": "q2_checkbox",
            "type": "checkbox_group",
            "questionText": {"en": "Q2 Checkbox English", "fr": "Q2 Checkbox French"},
            "answers": [
                {"value": "c1", "text": {"en": "C1 English", "fr": "C1 French"}, "weights": {"G1": 3, "G4": 7}},
                {"value": "c2", "text": {"en": "C2 English", "fr": "C2 French"}, "weights": {"G2": 4, "G5": 6}},
                {"value": "c3", "text": {"en": "C3 English", "fr": "C3 French"}, "weights": {"G1": 2, "G6": 5}},
            ],
        },
        {
            "id": "q3_freetext",
            "type": "freetext",
            "questionText": {"en": "Q3 Freetext English", "fr": "Q3 Freetext French"},
        },
        {
            "id": "q4_radio_no_weights",
            "type": "radio",
            "questionText": {"en": "Q4 Radio No Weights", "fr": "Q4 Radio No Weights French"},
            "answers": [
                {"value": "nw1", "text": {"en": "NW1 English", "fr": "NW1 French"}}, # No weights
            ],
        }
    ]
}

# Test cases for _calculate_scores

def test_calculate_scores_basic_radio():
    user_answers = {"q1_radio": "a1"}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 10
    assert scores["G2"] == 5
    assert scores["G3"] == 0
    assert submitted[0][0] == "Q1 Radio English"
    assert submitted[0][1] == "A1 English"

def test_calculate_scores_basic_checkbox_group():
    user_answers = {"q2_checkbox": ["c1", "c3"]}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 5  # 3 from c1 + 2 from c3
    assert scores["G2"] == 0
    assert scores["G4"] == 7
    assert scores["G6"] == 5
    assert submitted[0][0] == "Q2 Checkbox English"
    assert submitted[0][1] == "C1 English, C3 English"

def test_calculate_scores_freetext_question():
    user_answers = {"q3_freetext": "This is a test answer."}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 0  # No scores from freetext
    assert submitted[0][0] == "Q3 Freetext English"
    assert submitted[0][1] == "This is a test answer."

def test_calculate_scores_answer_value_not_found_radio():
    user_answers = {"q1_radio": "invalid_answer"}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 0
    assert scores["G2"] == 0
    assert submitted[0][0] == "Q1 Radio English"
    assert "Selected value not found: invalid_answer" in submitted[0][1]

def test_calculate_scores_answer_value_not_found_checkbox():
    user_answers = {"q2_checkbox": ["c1", "invalid_choice"]}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 3
    assert scores["G4"] == 7
    assert submitted[0][0] == "Q2 Checkbox English"
    assert "C1 English" in submitted[0][1]
    assert "Value not found: invalid_choice" in submitted[0][1]

def test_calculate_scores_empty_answers():
    user_answers = {}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    for group_score in scores.values():
        assert group_score == 0
    assert len(submitted) == 0

def test_calculate_scores_missing_answers_for_some_questions():
    user_answers = {"q1_radio": "a1"} # Only q1 answered
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 10
    assert scores["G2"] == 5
    assert scores["G3"] == 0 # q1_radio:a2 not selected
    assert scores["G4"] == 0 # q2_checkbox not answered
    assert len(submitted) == 1

def test_calculate_scores_with_exclude_qids():
    user_answers = {"q1_radio": "a1", "q2_checkbox": ["c1"]}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en", exclude_qids={"q1_radio"})
    assert scores["G1"] == 3  # q1_radio (10) excluded, only q2_checkbox:c1 (3) counts
    assert scores["G2"] == 0  # q1_radio (5) excluded
    assert scores["G4"] == 7  # from q2_checkbox:c1
    assert len(submitted) == 2 # Both are submitted, but one is not scored

def test_calculate_scores_different_language():
    user_answers = {"q1_radio": "a1"}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "fr")
    assert scores["G1"] == 10 # Scores are language-agnostic
    assert submitted[0][0] == "Q1 Radio French"
    assert submitted[0][1] == "A1 French"

def test_calculate_scores_no_weights_in_option():
    user_answers = {"q4_radio_no_weights": "nw1"}
    scores, submitted = _calculate_scores(user_answers, SAMPLE_STRUCTURE, "en")
    assert scores["G1"] == 0 # No weights associated with nw1
    assert submitted[0][0] == "Q4 Radio No Weights"
    assert submitted[0][1] == "NW1 English"

# Test cases for _generate_recommendation

def test_generate_recommendation_clear_winner_en():
    scores = {"G1": 20, "G2": 5, "G3": 0, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "en")
    expected_group_name = GROUP_NAMES.get("G1", "G1")
    assert f"Your profile suggests you align with: {expected_group_name} (G1)." in recommendation

def test_generate_recommendation_close_scores_two_winners_en():
    scores = {"G1": 20, "G2": 18, "G3": 5, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "en")
    g1_name = GROUP_NAMES.get("G1", "G1")
    g2_name = GROUP_NAMES.get("G2", "G2")
    # Order might vary if scores are identical, but here G1 is slightly higher
    assert f"{g1_name} (G1) and {g2_name} (G2)" in recommendation or \
           f"{g2_name} (G2) and {g1_name} (G1)" in recommendation


def test_generate_recommendation_very_close_scores_two_winners_en():
    scores = {"G1": 20, "G2": 15, "G3": 0, "G4": 0, "G5": 0, "G6": 0} # Difference is 5
    recommendation = _generate_recommendation(scores, "en")
    g1_name = GROUP_NAMES.get("G1", "G1")
    g2_name = GROUP_NAMES.get("G2", "G2")
    assert f"{g1_name} (G1) and {g2_name} (G2)" in recommendation

def test_generate_recommendation_one_dominant_one_secondary_just_outside_threshold():
    scores = {"G1": 20, "G2": 14, "G3": 0, "G4": 0, "G5": 0, "G6": 0} # Difference is 6
    recommendation = _generate_recommendation(scores, "en")
    g1_name = GROUP_NAMES.get("G1", "G1")
    g2_name = GROUP_NAMES.get("G2", "G2") # Should not be included
    assert f"{g1_name} (G1)." in recommendation
    assert g2_name not in recommendation


def test_generate_recommendation_no_significant_scores_en():
    scores = {"G1": 1, "G2": 0, "G3": 2, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "en")
    assert "No specific profile alignment found based on current scores." in recommendation

def test_generate_recommendation_all_zero_scores_en():
    scores = {"G1": 0, "G2": 0, "G3": 0, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "en")
    assert "No specific profile alignment found based on current scores." in recommendation

def test_generate_recommendation_clear_winner_fr():
    scores = {"G1": 20, "G2": 5, "G3": 0, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "fr")
    # Using GROUP_NAMES_LOCALIZED for French
    expected_group_name_fr = GROUP_NAMES_LOCALIZED.get("fr", {}).get("G1", "G1")
    assert f"Votre profil suggère que vous correspondez à : {expected_group_name_fr} (G1)." in recommendation

def test_generate_recommendation_close_scores_two_winners_fr():
    scores = {"G1": 20, "G2": 18, "G3": 5, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "fr")
    g1_name_fr = GROUP_NAMES_LOCALIZED.get("fr", {}).get("G1", "G1")
    g2_name_fr = GROUP_NAMES_LOCALIZED.get("fr", {}).get("G2", "G2")
    expected_recommendation_part = f"{g1_name_fr} (G1) et {g2_name_fr} (G2)"
    assert expected_recommendation_part in recommendation

def test_generate_recommendation_no_significant_scores_fr():
    scores = {"G1": 1, "G2": 0, "G3": 0, "G4": 0, "G5": 0, "G6": 0}
    recommendation = _generate_recommendation(scores, "fr")
    assert "Aucun profil spécifique détecté selon les scores actuels." in recommendation

def test_load_full_questionnaire_structure():
    # This test is more of an integration test for the loader,
    # but useful to ensure tests can run with actual structure if needed.
    # Requires static/questionnaire_structure.json to be present and valid.
    # For now, this is a placeholder or can be skipped if direct loading is too complex for unit tests.
    try:
        structure = _load_questionnaire_structure()
        assert "questions" in structure
        assert len(structure["questions"]) > 0
    except FileNotFoundError:
        pytest.skip("questionnaire_structure.json not found, skipping full structure load test.")

# It might be good to add a fixture for the sample structure if it gets complex or reused more.
@pytest.fixture
def sample_questionnaire_structure():
    return SAMPLE_STRUCTURE

# Example of using the fixture:
# def test_calculate_scores_with_fixture(sample_questionnaire_structure):
#     user_answers = {"q1_radio": "a1"}
#     scores, submitted = _calculate_scores(user_answers, sample_questionnaire_structure, "en")
#     assert scores["G1"] == 10


# Tests for /api/submit endpoint

def test_submit_valid_complex(client):
    payload = {"language": "fr", "answers": {"q1": "a1", "q2_checkbox": ["c1", "c2"], "q3_freetext": "Some free text"}}
    response = client.post('/api/submit', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "id" in data
    assert "timestamp" in data
    response_id = data["id"]

    # Verify database insertion (using the patched DB_PATH via client fixture's setup)
    # Need to import app module again to get the current (patched) DB_PATH
    import app as app_module_for_db_check
    conn = sqlite3.connect(app_module_for_db_check.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT language_code, answers_json FROM responses WHERE id=?", (response_id,))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "fr"
    assert json.loads(row[1]) == payload["answers"]

def test_submit_missing_language(client):
    payload = {"answers": {"q1": "a1"}}
    response = client.post('/api/submit', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Missing language code"

def test_submit_missing_answers_field(client):
    payload = {"language": "en"}
    response = client.post('/api/submit', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Missing answers data"

def test_submit_empty_answers_dict(client):
    payload = {"language": "en", "answers": {}} # Empty answers dict
    response = client.post('/api/submit', json=payload)
    assert response.status_code == 400 # Should be a 400 because empty dict is falsy
    data = response.get_json()
    assert data["error"] == "Missing answers data" # Validated by current app logic

def test_submit_answers_not_a_dict(client): # Technically, JSON body would be a dict, but if 'answers' value is not
    payload = {"language": "en", "answers": "not_a_dictionary"}
    # The code currently does json.dumps(answers_dict), if answers_dict itself is "not_a_dictionary"
    # this will be stored as a JSON string "not_a_dictionary".
    # This test checks if that's the case.
    response = client.post('/api/submit', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    response_id = data["id"]

    import app as app_module_for_db_check
    conn = sqlite3.connect(app_module_for_db_check.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT answers_json FROM responses WHERE id=?", (response_id,))
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert json.loads(row[0]) == "not_a_dictionary"


# Tests for /admin/export_csv

def test_admin_export_csv_no_data(client):
    # Log in admin
    login_res = client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    assert login_res.status_code == 200 # Should redirect to admin dashboard

    res = client.get('/admin/export_csv')
    assert res.status_code == 200
    assert res.mimetype == 'text/csv'
    assert 'attachment; filename=results.csv' in res.headers['Content-Disposition']

    csv_data = res.data.decode('utf-8')
    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    # Expected headers based on _load_questionnaire_structure and score groups
    # This part might need adjustment if questionnaire_structure changes.
    # For a truly robust test, load structure and build expected_headers dynamically.
    # For now, a basic check of row count.
    assert len(rows) == 1 # Only header row
    # Example: Check if 'timestamp' is in the header
    assert 'timestamp' in rows[0]
    assert 'G1' in rows[0]


def test_admin_export_csv_with_data(client):
    # Log in admin
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)

    # Submit sample data using actual question IDs from questionnaire_structure.json
    # Q1 is radio, Q3 is checkbox_group, Q10 is freetext
    payload1 = {"language": "en", "answers": {"1": "Mostly light", "10": "free text one"}}
    submit_res1 = client.post('/api/submit', json=payload1)
    assert submit_res1.status_code == 200
    data1 = submit_res1.get_json()
    response_id1 = data1["id"]

    payload2 = {"language": "fr", "answers": {"3": ["Repetitive motions or long standing", "Heavy lifting or demanding tasks"], "10": "autre texte"}}
    submit_res2 = client.post('/api/submit', json=payload2)
    assert submit_res2.status_code == 200

    res = client.get('/admin/export_csv')
    assert res.status_code == 200
    assert res.mimetype == 'text/csv'

    csv_data = res.data.decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_data)) # Use DictReader for easier column access
    rows = list(reader)
    assert len(rows) == 2 # 2 data rows (submitted data is LIFO in results query)

    # Assuming SAMPLE_STRUCTURE qids are 'q1_radio', 'q2_checkbox', 'q3_freetext', 'q4_radio_no_weights'
    # And scores are G1-G6.
    # The order of rows might depend on how admin_export_csv queries them (ORDER BY timestamp DESC)
    # So, the first row in CSV (rows[0]) should be the latest submission (payload2)

    # Check data for payload2 (French submission) - this should be the first data row
    row_payload2 = None
    for r in rows:
        if r["id"] == submit_res2.get_json()["id"]: # payload2 submitted last, should be first in CSV
            row_payload2 = r
            break
    assert row_payload2 is not None
    # Adjust keys to match actual CSV headers (e.g., Q1, Q2, Q3... Q10)
    assert row_payload2["Q3"] == "['Repetitive motions or long standing', 'Heavy lifting or demanding tasks']"
    assert row_payload2["Q10"] == "autre texte"
    assert row_payload2["G1"] != "" # Check that scores are present

    # Check data for payload1 (English submission)
    row_payload1 = None
    for r in rows:
        if r["id"] == response_id1:
            row_payload1 = r
            break
    assert row_payload1 is not None
    assert row_payload1["Q1"] == "Mostly light"
    assert row_payload1["Q10"] == "free text one"
    assert row_payload1["G2"] != ""


# Tests for /admin/group_info

def test_admin_group_info_get(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)

    res = client.get('/admin/group_info')
    assert res.status_code == 200
    html_content = res.data.decode('utf-8')

    # Check for some form fields
    assert f'name="G1_message_en"' in html_content
    assert f'name="G1_image"' in html_content
    assert f'name="{GROUP_IDS[-1]}_message_{list(LANGUAGE_NAMES.keys())[-1]}"' in html_content # Check for a field from the last group/lang


def test_admin_group_info_post(client, temp_group_info_file_fixture): # Use the new fixture
    # temp_group_info_file_fixture ensures app.GROUP_INFO_FILE is patched
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)

    form_data = {}
    # Populate form_data for all groups and languages to ensure the file is fully written
    # as expected by the _save_group_info and subsequent _load_group_info.
    for gid in GROUP_IDS:
        for lang_code in LANGUAGE_NAMES.keys():
            if gid == "G1" and lang_code == "en":
                form_data[f'{gid}_message_{lang_code}'] = "Updated G1 English Message"
            else:
                form_data[f'{gid}_message_{lang_code}'] = f"Default message for {gid} in {lang_code}"

        if gid == "G1":
            form_data[f'{gid}_image'] = "updated_g1_image.jpg"
        else:
            form_data[f'{gid}_image'] = f"default_{gid}_image.png"

    res_post = client.post('/admin/group_info', data=form_data, follow_redirects=True)
    assert res_post.status_code == 200 # Renders template again

    # Verify content of the temporary group_info.json file
    with open(temp_group_info_file_fixture, 'r', encoding='utf-8') as f:
        updated_info = json.load(f)

    assert updated_info["G1"]["messages"]["en"] == "Updated G1 English Message"
    assert updated_info["G1"]["image"] == "updated_g1_image.jpg"
    # Check another field to be sure
    last_gid = GROUP_IDS[-1]
    last_lang_code = list(LANGUAGE_NAMES.keys())[-1]
    assert updated_info[last_gid]["messages"][last_lang_code] == f"Default message for {last_gid} in {last_lang_code}"
    assert updated_info[last_gid]["image"] == f"default_{last_gid}_image.png"

    # Also check if a GET request now shows the updated values (tests _load_group_info)
    res_get = client.get('/admin/group_info')
    assert res_get.status_code == 200
    html_content_after_post = res_get.data.decode('utf-8')
    assert "Updated G1 English Message" in html_content_after_post
    assert 'value="updated_g1_image.jpg"' in html_content_after_post


# Tests for @admin_required decorator

ADMIN_ROUTES = [
    '/admin',
    '/admin/results',
    '/admin/export_csv',
    # '/admin/import_csv', # This is a POST endpoint, test separately if needed for GET on a page
    '/admin/group_info'
]

@pytest.mark.parametrize("route", ADMIN_ROUTES)
def test_admin_route_unauthenticated(client, route):
    res = client.get(route, follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

@pytest.mark.parametrize("route", ADMIN_ROUTES)
def test_admin_route_authenticated_get_access(client, route): # Renamed to avoid conflict
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    res = client.get(route)
    assert res.status_code == 200 # Basic check, specific content is tested elsewhere

# Special case for /admin/import_csv which is POST only for the action
def test_admin_import_csv_unauthenticated_post(client):
    res = client.post('/admin/import_csv', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

def test_admin_import_csv_authenticated_post_no_file(client): # POST without file
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    # Sending POST without a file, should redirect back to admin_results (or error, but redirect is current)
    res = client.post('/admin/import_csv', follow_redirects=True)
    assert res.status_code == 200 # It redirects to admin_results which is 200
    assert "/admin/results" in res.request.path # Check final path after redirect


# Tests for /thank_you.html route

def test_thank_you_no_data_parameter(client):
    res = client.get('/thank_you.html')
    assert res.status_code == 200
    html_content = res.data.decode('utf-8')
    # Check if it indicates no data was processed, e.g. by looking for a known part of the "no data" state
    # This depends on how thank_you.html is rendered with None values for scores/recommendation
    assert "Your profile suggests you align with:" not in html_content # Assuming this only shows with data
    # Or, more explicitly, if the template shows a message:
    # assert "No survey data provided." in html_content # This depends on template implementation

def test_thank_you_with_valid_data(client):
    # Using IDs from static/questionnaire_structure.json
    answers = {"1": "Mostly light", "10": "Feeling good today!"}
    answers_json = json.dumps(answers)
    # URL encode the JSON string
    data_param = quote(answers_json)

    # Mock _ai_suggestion to avoid external calls and control its output
    # Ensure the path to the function being patched is correct relative to where it's called from (app.py)
    with patch('app._ai_suggestion', return_value="Mocked AI suggestion for you.") as mock_ai:
        res = client.get(f'/thank_you.html?data={data_param}&lang=en')
        assert res.status_code == 200
        mock_ai.assert_called_once()

        html_content = res.data.decode('utf-8')
        assert "Your profile suggests you align with:" in html_content # Check for part of recommendation
        assert "Mocked AI suggestion for you." in html_content

        # Check for submitted answer display (e.g. "Mostly light")
        # This requires knowing how answers are displayed in thank_you.html
        # For example, if they are in a list:
        assert "Mostly light" in html_content # Check if the answer value is displayed
        assert "Feeling good today!" in html_content # Check freetext

def test_thank_you_with_invalid_data_parameter(client):
    res = client.get('/thank_you.html?data=THIS_IS_NOT_JSON&lang=en')
    assert res.status_code == 400
    html_content = res.data.decode('utf-8')
    assert "Invalid data parameter: Expecting value: line 1 column 1 (char 0)" in html_content
