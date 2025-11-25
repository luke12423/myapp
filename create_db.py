from app import app,db
from models import populate_database

with app.app_context():
    db.create_all()
    populate_database()

