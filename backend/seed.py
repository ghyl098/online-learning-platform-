from app import app, db, Course

with app.app_context():
    # Khali data thapne
    c1 = Course(title="Web Development", description="Learn HTML, CSS, JS", video_url="https://link.com/1")
    c2 = Course(title="Python Basics", description="Learn Python from scratch", video_url="https://link.com/2")
    
    db.session.add(c1)
    db.session.add(c2)
    db.session.commit()
    
    print("Database ma sample data thapiyo! Aba browser refresh gara.")