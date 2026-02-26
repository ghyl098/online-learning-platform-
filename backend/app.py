from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = Flask(__name__)
# Vercel ma deploy garda CORS le dherai tension dincha, tesaile full allow gareko chhu
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    # 1. Pahila Environment Variable check garne (Vercel/Production ko lagi)
    if os.environ.get('FIREBASE_SERVICE_ACCOUNT'):
        service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
        cred = credentials.Certificate(service_account_info)
    else:
        # 2. Local ma huda file batai credentials line
        cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            print("Error: serviceAccountKey.json bhetiyena!")
            cred = None

    if cred:
        firebase_admin.initialize_app(cred)

db = firestore.client()

# --- API ROUTES ---

# missing register-user route thapeko (Dashboard login ko lagi chaincha)
@app.route('/api/register-user', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        uid = data.get('uid')
        if not uid:
            return jsonify({"error": "No UID provided"}), 400
        
        # User details lai Firestore ko 'users' collection ma save garne
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            "username": data.get('username'),
            "email": data.get('email'),
            "uid": uid,
            "last_login": firestore.SERVER_TIMESTAMP
        }, merge=True) # merge=True le purano data delete gardaina, update matra garchha

        return jsonify({"status": "success", "message": "User registered in Firestore"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    try:
        # 1. Firebase bata Data Fetch garne (GET)
        if request.method == 'GET':
            courses_ref = db.collection('courses') 
            docs = courses_ref.stream()
            
            course_list = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                course_list.append({
                    "id": doc.id,
                    "title": data.get('title', 'No Title'),
                    "desc": data.get('description') or data.get('desc', ''),
                    "url": data.get('video_url') or data.get('url', '#')
                })
            return jsonify(course_list)

        # 2. Firebase ma Data Save garne (POST)
        if request.method == 'POST':
            data = request.get_json()
            new_course = {
                "title": data.get('title'),
                "description": data.get('description') or data.get('desc'),
                "video_url": data.get('video_url') or data.get('url')
            }
            db.collection('courses').add(new_course)
            return jsonify({"status": "success", "message": "Course saved to Firebase!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"status": "Backend connected to Firebase successfully!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)