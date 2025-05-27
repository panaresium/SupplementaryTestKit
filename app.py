import os
import sqlite3
import json # Added json import
from flask import Flask, request, jsonify, send_from_directory, render_template # Added render_template
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime, timezone # Updated import

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'responses.db')

# Serve the survey front-end
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/thank_you.html')
def thank_you():
    return send_from_directory('static', 'thank_you.html')

def init_db():
    print("DEBUG INIT_DB: Attempting to initialize database...") # New
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print(f"DEBUG INIT_DB: Database path is {DB_PATH}") # New
    print("DEBUG INIT_DB: Dropping old responses table if it exists...") # New
    cur.execute("DROP TABLE IF EXISTS responses")
    conn.commit() # Commit the drop
    print("DEBUG INIT_DB: Creating new responses table with current schema...") # New
    
    # Ensure this schema string is exactly the one that includes language_code and other recent changes
    create_table_sql = """CREATE TABLE IF NOT EXISTS responses (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        language_code TEXT, -- ADDED
        age TEXT,
        gender TEXT,
        occupation TEXT,
        location TEXT,
        work_hours TEXT,
        work_env TEXT,
        posture TEXT,
        transport TEXT,
        commute_time TEXT,
        physical_demand TEXT,
        exercise_freq TEXT,
        exercise_duration TEXT,
        exercise_types TEXT, -- RENAMED from exercise_type
        exercise_type_other TEXT, -- ADDED
        sleep_time TEXT,
        wake_time TEXT,
        avg_sleep TEXT,
        food_like TEXT,
        food_dislike TEXT,
        diet_preference TEXT,
        diet_restrictions TEXT,
        meals_per_day TEXT,
        beverage_choices TEXT, -- RENAMED from beverages
        beverages_other TEXT, -- ADDED
        smoke TEXT,
        alcohol TEXT,
        health_goals TEXT,
        supplement_use TEXT,
        current_supplements TEXT,
        medical_conditions TEXT,
        symptoms_checklist TEXT,
        symptoms_other_concerns TEXT,
        symptoms_stress_level TEXT,
        products TEXT
    )"""
    print(f"DEBUG INIT_DB: Executing SQL: {create_table_sql}") # New: print the SQL
    cur.execute(create_table_sql)
    conn.commit() # Commit the create
    conn.close()
    print("DEBUG INIT_DB: Database initialization complete.") # New

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True)
    language_code = data.get('language') # Extract language_code
    response_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat() # Updated timestamp generation

    features_json_string = data.get('features')
    survey_answers = {}
    if features_json_string:
        try:
            survey_answers = json.loads(features_json_string)
        except json.JSONDecodeError:
            # Handle error if features is not valid JSON
            # For now, we'll proceed with empty survey_answers
            pass 

    products_data = data.get('products')

    # Extract all individual answers
    age = survey_answers.get('age')
    gender = survey_answers.get('gender')
    occupation = survey_answers.get('occupation')
    location = survey_answers.get('location')
    work_hours = survey_answers.get('work_hours')
    work_env = survey_answers.get('work_env')
    posture = survey_answers.get('posture')
    transport = survey_answers.get('transport')
    commute_time = survey_answers.get('commute_time')
    physical_demand = survey_answers.get('physical_demand')
    exercise_freq = survey_answers.get('exercise_freq')
    exercise_duration = survey_answers.get('exercise_duration')
    # exercise_type = survey_answers.get('exercise_type') # Removed/Commented out
    exercise_types_list = survey_answers.get('exercise_types', [])
    exercise_types_str = json.dumps(exercise_types_list)
    exercise_type_other = survey_answers.get('exercise_type_other')
    sleep_time = survey_answers.get('sleep_time')
    wake_time = survey_answers.get('wake_time')
    avg_sleep = survey_answers.get('avg_sleep')
    food_like = survey_answers.get('food_like')
    food_dislike = survey_answers.get('food_dislike')
    diet_preference = survey_answers.get('diet_preference')
    diet_restrictions = survey_answers.get('diet_restrictions')
    meals_per_day = survey_answers.get('meals_per_day')
    # beverages = survey_answers.get('beverages') # Removed/Commented out
    beverage_choices_list = survey_answers.get('beverage_choices', [])
    beverage_choices_str = json.dumps(beverage_choices_list)
    beverages_other = survey_answers.get('beverages_other')
    smoke = survey_answers.get('smoke')
    alcohol = survey_answers.get('alcohol')
    
    health_goals_list = survey_answers.get('health_goals', [])
    health_goals_str = json.dumps(health_goals_list)
    
    supplement_use = survey_answers.get('supplement_use')
    current_supplements = survey_answers.get('current_supplements')
    medical_conditions = survey_answers.get('medical_conditions')
    
    symptoms_data = survey_answers.get('symptoms', {})
    symptoms_checklist_list = symptoms_data.get('checklist', [])
    symptoms_checklist_str = json.dumps(symptoms_checklist_list)
    symptoms_other_concerns = symptoms_data.get('other_concerns')
    symptoms_stress_level = symptoms_data.get('stress_level')

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    column_names = [
        "id", "timestamp", "language_code", "age", "gender", "occupation", "location", "work_hours",
        "work_env", "posture", "transport", "commute_time", "physical_demand",
        "exercise_freq", "exercise_duration", "exercise_types", "exercise_type_other", 
        "sleep_time", "wake_time", "avg_sleep", "food_like", "food_dislike", 
        "diet_preference", "diet_restrictions", "meals_per_day", 
        "beverage_choices", "beverages_other", "smoke", "alcohol", "health_goals",
        "supplement_use", "current_supplements", "medical_conditions",
        "symptoms_checklist", "symptoms_other_concerns", "symptoms_stress_level", "products"
    ]
    
    placeholders = ", ".join(["?"] * len(column_names))
    sql = f"INSERT INTO responses ({', '.join(column_names)}) VALUES ({placeholders})"
    
    values_tuple = (
        response_id, timestamp, language_code, age, gender, occupation, location, work_hours,
        work_env, posture, transport, commute_time, physical_demand,
        exercise_freq, exercise_duration, exercise_types_str, exercise_type_other,
        sleep_time, wake_time, avg_sleep, food_like, food_dislike,
        diet_preference, diet_restrictions, meals_per_day,
        beverage_choices_str, beverages_other, smoke, alcohol, health_goals_str,
        supplement_use, current_supplements, medical_conditions,
        symptoms_checklist_str, symptoms_other_concerns, symptoms_stress_level, products_data
    )

    cur.execute(sql, values_tuple)
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'id': response_id, 'timestamp': timestamp})

@app.route('/admin/results')
def admin_results():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    cur = conn.cursor()
    cur.execute("SELECT * FROM responses ORDER BY timestamp DESC")
    results = cur.fetchall()
    conn.close()
    # For 'health_goals' and 'symptoms_checklist', which are stored as JSON strings,
    # it might be beneficial to parse them back into Python lists here
    # before sending to the template, or handle parsing in the template itself.
    # For now, we'll pass them as raw strings and let the template handle display.
    # If parsing here:
    # processed_results = []
    # for row in results:
    #     row_dict = dict(row) # Convert sqlite3.Row to a mutable dict
    #     try:
    #         if row_dict.get('health_goals'):
    #             row_dict['health_goals'] = json.loads(row_dict['health_goals'])
    #         if row_dict.get('symptoms_checklist'):
    #             row_dict['symptoms_checklist'] = json.loads(row_dict['symptoms_checklist'])
    #     except json.JSONDecodeError:
    #         # Handle cases where the string might not be valid JSON, though it should be
    #         pass # Keep as original string if parsing fails
    #     processed_results.append(row_dict)
    # return render_template('results.html', results=processed_results)
    
    return render_template('results.html', results=results) # results is a list of Row objects

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
