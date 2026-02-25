from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
CORS(app)

# --- FIREBASE SETUP ---
# Timro JSON file ko path yaha milaunu hos
cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- API ROUTES ---

@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    try:
        # 1. Firebase bata Data Fetch garne (GET)
        if request.method == 'GET':
            courses_ref = db.collection('courses') # Firebase collection name
            docs = courses_ref.stream()
            
            course_list = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Frontend le khojne formats haru milaideko
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
            # Firebase ma auto-id generate garera save hunchha
            db.collection('courses').add(new_course)
            return jsonify({"status": "success", "message": "Course saved to Firebase!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"status": "Backend connected to Firebase successfully!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)