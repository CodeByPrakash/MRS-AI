import speech_recognition as sr
from flask import Flask, request, render_template, jsonify, send_file
import numpy as np
import pandas as pd
import pickle
import io
import csv
from flask_socketio import SocketIO, emit

# Initialize Flask app and SocketIO
app = Flask(__name__, template_folder='.', static_folder='static')
socketio = SocketIO(app)

# Load data
sym_des = pd.read_csv("symtoms_df.csv")
precautions = pd.read_csv("precautions_df.csv")
workout = pd.read_csv("workout_df.csv")
description = pd.read_csv("description.csv")
medications = pd.read_csv('medications.csv')
diets = pd.read_csv("diets.csv")

# Load model
svc = pickle.load(open('svc.pkl','rb'))

# Helper function (unchanged)
def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]

    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]

    wrkout = workout[workout['disease'] == dis]['workout']

    return desc, pre, med, die, wrkout

# Function to process speech input
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for speech...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return None

# SocketIO event to handle speech recognition and send results back to the frontend
@socketio.on('start_speech_recognition')
def handle_speech_recognition(message):
    recognized_text = recognize_speech()
    if recognized_text:
        emit('speech_recognition_result', {'text': recognized_text})
    else:
        emit('speech_recognition_result', {'text': 'Sorry, I couldn\'t recognize any speech.'})

# Route for home page
@app.route("/")
def index():
    return render_template('index.html')

# Route for disease prediction (unchanged)
@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        if symptoms == "Symptoms":
            message = "Please either write symptoms or you have written misspelled symptoms"
            return render_template('index.html', message=message)
        else:
            user_symptoms = [s.strip() for s in symptoms.split(',')]
            user_symptoms = [symptom.strip("[]' ") for symptom in user_symptoms]
            predicted_disease = get_predicted_value(user_symptoms)
            dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)

            my_precautions = [i for i in precautions[0]]
            return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                                   my_precautions=my_precautions, medications=medications, my_diet=rec_diet,
                                   workout=workout)
    return render_template('index.html')

# Download data route (unchanged)
@app.route("/download", methods=['GET', 'POST'])
def download_data():
    if request.method == 'POST':
        disease = request.form['predicted_disease']
        dis_des, precautions, medications, rec_diet, workout = helper(disease)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Disease Description', dis_des])
        writer.writerow(['Precautions', ', '.join(precautions[0])])
        writer.writerow(['Medications', ', '.join(medications)])
        writer.writerow(['Recommended Diet', ', '.join(rec_diet)])
        writer.writerow(['Workout Suggestions', ', '.join(workout)])

        output.seek(0)
        return send_file(output, as_attachment=True, download_name=f"{disease}_details.csv", mimetype="text/csv")
    return render_template("index.html")

if __name__ == '__main__':
    socketio.run(app, debug=True)
