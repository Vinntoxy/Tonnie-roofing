"""Flask extensions module"""
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
session = Session()
migrate = Migrate()
