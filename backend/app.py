from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
# Vercel ko lagi CORS setup
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- PATH DETECTION ---
# Vercel ra Local dubai ma key file bhetna yo dynamic path use hunchha
basedir = os.path.dirname(os.path.abspath(__file__))

# --- SAFE FIREBASE INITIALIZATION ---
db = None
try:
    if not firebase_admin._apps:
        # Multiple environment paths check garne
        paths_to_check = [
            os.path.join(basedir, 'serviceAccountKey.json'),
            os.path.join(os.getcwd(), 'backend', 'serviceAccountKey.json'),
            '/var/task/backend/serviceAccountKey.json'
        ]
        
        cred = None
        for p in paths_to_check:
            if os.path.exists(p):
                cred = credentials.Certificate(p)
                print(f"Firebase key found at: {p}")
                break
        
        if cred:
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        else:
            print("CRITICAL: serviceAccountKey.json not found in any path!")
    else:
        db = firestore.client()
except Exception as e:
    print(f"Firebase Critical Error: {e}")

# --- API ROUTES ---

@app.route('/')
def home():
    # Database connected cha ki chaina check garne
    return jsonify({
        "status": "Online",
        "database": "Connected" if db else "Disconnected (Check serviceAccountKey.json)",
        "message": "Server running perfectly on Vercel!"
    })

@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    try:
        if db is None:
            return jsonify({"error": "Database connection failed."}), 500
            
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

@app.route('/api/make-me-admin')
def make_me_admin():
    target_email = "ghyalpolama62@gmail.com"
    try:
        if db is None: return jsonify({"error": "DB not connected"}), 500
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

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5000)