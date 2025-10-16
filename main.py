import os
from functools import wraps

from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import numpy as np
import pandas as pd
import pickle
from sklearn.svm import SVC  # Importing Support Vector Classifier from sklearn
import json
import wikipediaapi
from pathlib import Path
from datetime import datetime
# flask app
app = Flask(__name__, template_folder='.',static_folder="static") 
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')


# load databasedataset===================================
sym_des = pd.read_csv("symtoms_df.csv")
precautions = pd.read_csv("precautions_df.csv")
workout = pd.read_csv("workout_df.csv")
description = pd.read_csv("description.csv")
medications = pd.read_csv('medications.csv')
diets = pd.read_csv("diets.csv")


# load model===========================================
svc = pickle.load(open('svc.pkl','rb'))


# Quiz data storage paths
DATA_DIR = Path("data")
QUESTIONS_PATH = DATA_DIR / "quiz_questions.json"
FEEDBACK_PATH = DATA_DIR / "quiz_feedback.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return default


def _write_json(path, payload):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _resolve_redirect_target(candidate, fallback='admin_quiz'):
    target = candidate or ''
    if target.startswith('/'):
        return target
    return url_for(fallback)


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(**kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login', next=request.path))
        return view_func(**kwargs)
    return wrapped_view


#============================================================
# custome and helping functions
#========================== helper funtions ================
def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]

    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]

    wrkout = workout[workout['disease'] == dis] ['workout']


    return desc,pre,med,die,wrkout

symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

# Model Prediction function
def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))
    for item in patient_symptoms:
        input_vector[symptoms_dict[item]] = 1
    return diseases_list[svc.predict([input_vector])[0]]


    

@app.route("/")
def index():
    return render_template('index.html')

def get_wikipedia_summary(disease_name):
    # Fetch the Wikipedia page for the disease
    wiki_wiki = wikipediaapi.Wikipedia('en-US, en-IN')
    page = wiki_wiki.page(disease_name)
    if page.exists():
        return page.summary
    else:
        return "Sorry, no Wikipedia page found for this disease."

@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':     
        symptoms = request.form.get('symptoms')
        mysysms = request.form.get('mysysms')
        
        if symptoms == "Symptoms":
            message = "Please either write symptoms or you have written misspelled symptoms"
            return render_template('index.html', message=message)
        else:
            # Split the user's input into a list of symptoms (assuming they are comma-separated)
            user_symptoms = [s.strip() for s in symptoms.split(',')]
            user_symptoms = [symptom.strip("[]' ") for symptom in user_symptoms]

            predicted_disease = get_predicted_value(user_symptoms)

            # Get the disease details
            dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)
            
            # Get the Wikipedia summary for the predicted disease
            wiki_summary = get_wikipedia_summary(predicted_disease)

            # Prepare precautions list
            my_precautions = []
            for i in precautions[0]:
                my_precautions.append(i)

            return render_template('index.html', 
                                   predicted_disease=predicted_disease, 
                                   dis_des=dis_des,
                                   my_precautions=my_precautions, 
                                   medications=medications, 
                                   my_diet=rec_diet,
                                   workout=workout,
                                   wiki_summary=wiki_summary)  # Passing the summary to template

    return render_template('index.html')


# about view funtion and path
@app.route('/about')
def about():
    return render_template("about.html")
# contact view funtion and path
@app.route('/contact')
def contact():
    return render_template("contact.html")

# developer view funtion and path
@app.route('/developer')
def developer():
    return render_template("dev.html")

# about view funtion and path
@app.route('/blog')
def blog():
    return render_template("blog.html")

@app.route('/quiz')
def quiz():
    return render_template("quiz.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_admin'):
        return redirect(_resolve_redirect_target(request.args.get('next')))

    error = None
    next_url = request.args.get('next') or request.form.get('next') or ''

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()

        expected_username = app.config.get('ADMIN_USERNAME', 'admin')
        expected_password = app.config.get('ADMIN_PASSWORD', 'admin123')

        if username == expected_username and password == expected_password:
            session['is_admin'] = True
            session['admin_username'] = username
            return redirect(_resolve_redirect_target(next_url))

        error = 'Invalid username or password. Please try again.'

    return render_template('login.html', error=error, next_url=next_url)


@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    session.pop('admin_username', None)
    return redirect(url_for('login'))


@app.route('/admin_quiz')
def admin_quiz_page():
    return redirect(url_for('admin_quiz'))

@app.route('/api/quiz/questions')
def api_quiz_questions():
    questions = _load_json(QUESTIONS_PATH, [])
    return jsonify(questions)


@app.route('/api/quiz/feedback', methods=['POST'])
def api_quiz_feedback():
    payload = request.get_json(silent=True) or {}
    correction = (payload.get('correction') or '').strip()

    if not correction:
        return jsonify({'status': 'error', 'message': 'Correction details are required.'}), 400

    entry = {
        'correction': correction,
        'question_reference': (payload.get('questionReference') or '').strip(),
        'contact': (payload.get('contact') or '').strip(),
        'submitted_at': datetime.utcnow().isoformat() + 'Z'
    }

    feedback = _load_json(FEEDBACK_PATH, [])
    feedback.append(entry)
    _write_json(FEEDBACK_PATH, feedback)

    return jsonify({'status': 'ok'})


@app.route('/admin/quiz', methods=['GET', 'POST'])
@login_required
def admin_quiz():
    message = None
    error = None

    if request.method == 'POST':
        question = (request.form.get('question') or '').strip()
        option_fields = [request.form.get(f'option{i}', '').strip() for i in range(1, 5)]
        answer = (request.form.get('answer') or '').strip()
        category = (request.form.get('category') or 'General').strip() or 'General'
        difficulty = (request.form.get('difficulty') or 'Starter').strip() or 'Starter'
        fact = (request.form.get('fact') or '').strip()

        if not question:
            error = 'Question text is required.'
        elif any(not opt for opt in option_fields):
            error = 'All option fields must be filled in.'
        else:
            try:
                answer_index = int(answer)
            except ValueError:
                error = 'Answer must be provided as a numeric option index.'
            else:
                if answer_index < 0 or answer_index >= len(option_fields):
                    error = 'Answer index must correspond to one of the options (0-3).'

        if not error:
            questions = _load_json(QUESTIONS_PATH, [])
            questions.append({
                'question': question,
                'options': option_fields,
                'answer': answer_index,
                'category': category,
                'difficulty': difficulty,
                'fact': fact
            })
            _write_json(QUESTIONS_PATH, questions)
            message = 'Question saved successfully.'

    questions_preview = _load_json(QUESTIONS_PATH, [])[-5:]
    return render_template('admin_quiz.html', message=message, error=error, recent_questions=questions_preview)

@app.route('/wiki', methods=['GET', 'POST'])
def wiki():
    summary = None
    if request.method == 'POST':
        page_name = request.form.get('page_name')
        wiki_wiki = wikipediaapi.Wikipedia('en-US, en-IN')
        page = wiki_wiki.page(page_name)
        if page.exists():
            summary = page.summary
        else:
            summary = f"Page '{page_name}' not found."

    return render_template("wiki.html", summary=summary)

# # Function to fetch Wikipedia summary
# def get_wikipedia_page_summary(page_name):
#     wiki_wiki = wikipediaapi.Wikipedia('en-US, en-IN')
#     page = wiki_wiki.page(page_name)
    
#     if page.exists():
#         return page.summary
#     else:
#         return f"Page '{page_name}' not found."
    
    

if __name__ == '__main__':

    app.run(debug=True)