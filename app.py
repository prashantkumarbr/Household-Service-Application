from flask import Flask
from backend.models import db

app=None

def setup_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///household_service.sqlite3" #having db file
    db.init_app(app) #Flask app connected to db(sql alchemy)
    app.app_context().push() #direct access to other modules
    app.debug=True
    print("app is started...")

setup_app()

from backend.controllers import *

if __name__=="__main__":
    app.run()