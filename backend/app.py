from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
CORS(app)

# --- FOLDER PATH SETTINGS ---
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

# Instance folder chaina vane banaune
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- FIREBASE SETUP ---
# Vercel ma folder structure ali farak huna sakcha, tesailai yo logic thapिएको cha
cred_path = os.path.join(basedir, 'serviceAccountKey.json')

if not firebase_admin._apps:
    try:
        # File exist garchha ki nai check garne
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Yedi backend folder vitra khojda bhetena vane, sidhai base path use garne
            alt_path = "serviceAccountKey.json" 
            cred = credentials.Certificate(alt_path)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase Key Error: {e}")

db = firestore.client()

# --- ADMIN FIX ROUTE ---
@app.route('/api/make-me-admin')
def make_me_admin():
    target_email = "ghyalpolama62@gmail.com"
    try:
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', target_email).stream()
        
        found = False
        for doc in query:
            doc.reference.update({'role': 'admin'})
            found = True
            
        if found:
            return jsonify({"status": "success", "message": f"{target_email} is now an Admin!"})
        else:
            return jsonify({"status": "error", "message": "User not found in Firestore."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- API ROUTES ---

@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    try:
        if request.method == 'GET':
            courses_ref = db.collection('courses')
            docs = courses_ref.stream()
            
            course_list = []
            for doc in docs:
                data = doc.to_dict()
                course_list.append({
                    "id": doc.id,
                    "title": data.get('title', 'Untitled'),
                    "desc": data.get('description') or data.get('desc', ''),
                    "url": data.get('video_url') or data.get('url', '#')
                })
            return jsonify(course_list)

        if request.method == 'POST':
            data = request.get_json()
            db.collection('courses').add(data)
            return jsonify({"status": "success"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "Server running perfectly!", "database": "Checked"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)