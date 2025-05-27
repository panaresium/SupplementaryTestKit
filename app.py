import os
import sqlite3
import json # Added json import
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'responses.db')

# Serve the survey front-end
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Drop the old table if it exists
    cur.execute("DROP TABLE IF EXISTS responses")
    # Create the new table with the detailed schema
    cur.execute(
        """CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
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
            exercise_type TEXT,
            sleep_time TEXT,
            wake_time TEXT,
            avg_sleep TEXT,
            food_like TEXT,
            food_dislike TEXT,
            diet_preference TEXT,
            diet_restrictions TEXT,
            meals_per_day TEXT,
            beverages TEXT,
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
    )
    conn.commit()
    conn.close()

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True)
    response_id = str(uuid4())
    timestamp = datetime.utcnow().isoformat()

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
    exercise_type = survey_answers.get('exercise_type')
    sleep_time = survey_answers.get('sleep_time')
    wake_time = survey_answers.get('wake_time')
    avg_sleep = survey_answers.get('avg_sleep')
    food_like = survey_answers.get('food_like')
    food_dislike = survey_answers.get('food_dislike')
    diet_preference = survey_answers.get('diet_preference')
    diet_restrictions = survey_answers.get('diet_restrictions')
    meals_per_day = survey_answers.get('meals_per_day')
    beverages = survey_answers.get('beverages')
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
        "id", "timestamp", "age", "gender", "occupation", "location", "work_hours",
        "work_env", "posture", "transport", "commute_time", "physical_demand",
        "exercise_freq", "exercise_duration", "exercise_type", "sleep_time", "wake_time",
        "avg_sleep", "food_like", "food_dislike", "diet_preference", "diet_restrictions",
        "meals_per_day", "beverages", "smoke", "alcohol", "health_goals",
        "supplement_use", "current_supplements", "medical_conditions",
        "symptoms_checklist", "symptoms_other_concerns", "symptoms_stress_level", "products"
    ]
    
    placeholders = ", ".join(["?"] * len(column_names))
    sql = f"INSERT INTO responses ({', '.join(column_names)}) VALUES ({placeholders})"
    
    values_tuple = (
        response_id, timestamp, age, gender, occupation, location, work_hours,
        work_env, posture, transport, commute_time, physical_demand,
        exercise_freq, exercise_duration, exercise_type, sleep_time, wake_time,
        avg_sleep, food_like, food_dislike, diet_preference, diet_restrictions,
        meals_per_day, beverages, smoke, alcohol, health_goals_str,
        supplement_use, current_supplements, medical_conditions,
        symptoms_checklist_str, symptoms_other_concerns, symptoms_stress_level, products_data
    )

    cur.execute(sql, values_tuple)
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'id': response_id, 'timestamp': timestamp})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
