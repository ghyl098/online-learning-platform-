from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- DATABASE SETUP ---
# This forces database.db to be in the backend folder, NOT inside 'instance'
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='student')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(500))

with app.app_context():
    db.create_all()

# --- API ROUTES ---

@app.route('/api/register-user', methods=['POST'])
def register_user():
    data = request.get_json()
    admin_email = "ghyalpolama62@gmail.com".lower()
    user_email = data.get('email', '').lower()
    
    user = User.query.filter_by(uid=data['uid']).first()
    
    if not user:
        # Create new user
        role = 'admin' if user_email == admin_email else 'student'
        user = User(uid=data['uid'], username=data['username'], email=user_email, role=role)
        db.session.add(user)
    else:
        # UPGRADE TO ADMIN: If user exists but role is student, update it
        if user_email == admin_email:
            user.role = 'admin'
            
    db.session.commit()
    return jsonify({"role": user.role, "username": user.username})

@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    if request.method == 'POST':
        data = request.get_json()
        new_course = Course(title=data['title'], description=data['description'], video_url=data.get('video_url'))
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": "Success"}), 201
    
    courses = Course.query.all()
    return jsonify([{"id": c.id, "title": c.title, "desc": c.description, "url": c.video_url} for c in courses])

@app.route('/api/students', methods=['GET'])
def get_students():
    users = User.query.all()
    return jsonify([{"username": u.username, "email": u.email, "role": u.role} for u in users])

if __name__ == '__main__':
    app.run(debug=True, port=5000)