# Ensure the `assemblyai` and `flask` packages are installed:
# pip install -U assemblyai flask waitress requests

import assemblyai as aai
from flask import Flask, request, jsonify
import requests
import os
from waitress import serve
from flask_cors import CORS


# AssemblyAI API key
aai.settings.api_key = "62acec891bb04c339ec059b738bedac6"

# Hugging Face model API details
API_URL = ""
HEADERS = {"Authorization": ""}

questions = [
    "Which grade is the patient studying?",
    "How old is the patient?",
    "What is the gender?",
    "Can you provide the name and location of the patient's school?",
    "What are the names of the patient's guardians or parents?",
    "What is the chief complaint regarding the patient's oral health? If there is none, just say the word 'none', else elaborate only on medication history",
    "Can you provide any relevant medical history for the patient? If there is none, just say the word 'none', else elaborate",
    "Does the patient take any medications regularly? If there is none, just say the word 'none'. If yes, please specify.",
    "When was the patient's previous dental visit? If no visits before, just say the word 'first' or mention the visit number and nothing else",
    "Does the patient have any habits such as thumb sucking, tongue thrusting, nail biting, or lip biting? If yes, just list them and don't provide any further details",
    "Does the patient brush their teeth? Just use the words 'once daily', 'twice daily', or 'thrice daily' to answer, nothing else",
    "Does the patient experience bleeding gums? Just say 'yes' or 'no' for this and nothing else",
    "Has the patient experienced early childhood caries? Just say 'yes' or 'no' and nothing else",
    "Please mention if tooth decay is present with tooth number(s), else just say the word 'none' and nothing else",
    "Have any teeth been fractured? If yes, please mention the tooth number(s), else just say 'none' and nothing else",
    "Is there any pre-shedding mobility of teeth? If yes, please specify, else just say 'none' and nothing else",
    "Does the patient have malocclusion? If yes, please provide details, else just say the word 'none' and nothing else",
    "Does the patient experience pain, swelling, or abscess? If yes, please provide details, else just say 'none' and nothing else",
    "Are there any other findings you would like to note?",
    "What treatment plan do you recommend? Choose only from Options: (Scaling, Filling, Pulp therapy/RCT, Extraction, Medication, Referral) and nothing else"
]

app = Flask(__name__)
CORS(app)

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

@app.route('/answer', methods=['POST'])
def answer_question():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['file']
    
    if not audio_file.filename.endswith('.wav'):
        return jsonify({'error': 'Only WAV audio files are supported'}), 400
    
    temp_dir = '/tmp'
    temp_audio_path = os.path.join(temp_dir, 'audio_file.wav')

    # Ensure the temporary directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        audio_file.save(temp_audio_path)

        # Transcribe the audio file using AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_audio_path)

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(transcript.error)

        context = transcript.text
        results = []

        for question in questions:
            payload = {
                "inputs": {
                    "question": question,
                    "context": context
                }
            }

            try:
                answer = query(payload)
                results.append(answer['answer'])
            except Exception as e:
                results.append(str(e))

        return jsonify({
            'answers': results,
            'transcript': context
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
