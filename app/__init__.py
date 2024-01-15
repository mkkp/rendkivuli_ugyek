import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_paranoid import Paranoid
import flask_monitoringdashboard as dashboard
from app import views

from app.models import db
from app.env import APP_SECRET_KEY, BASE_DIR, DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates"),
)
app.secret_key = APP_SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH

migrate = Migrate(app, db)
db.init_app(app)

dashboard.bind(app)

# CORS
# https://flask-cors.readthedocs.io/en/latest/
CORS(app)

# Paranoid
# https://pypi.org/project/Flask-Paranoid/
paranoid = Paranoid(app)
paranoid.redirect_view = "/"

views.setup(app)


@app.before_first_request
def create_all():
    """
    If no app.db is present, it creates app.db
    based on schema that is defined in models.py
    """
    db.create_all()
