from app import app
import os

with app.app_context():
    # यसले जबरजस्ती instance फोल्डर भित्र database.db बनाउँछ
    print("Database path:", app.config['SQLALCHEMY_DATABASE_URI'])
    # यदि तपाईंले Models प्रयोग गर्नुभएको छ भने यहाँ db.create_all() चाहिन्छ