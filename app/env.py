import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

if load_dotenv():
    logger.info("loading env...")
else:
    logger.warning("---internal .env was not found---")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# APP
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/upload")

DEBUG_MODE = os.environ["DEBUG_MODE"]
PORT = os.environ["PORT"]
APP_SECRET_KEY = os.environ["APP_SECRET_KEY"]
ROWS_PER_PAGE = int(os.environ["ROWS_PER_PAGE"])

# MAP
MAP_KEY = os.environ["MAP_KEY"]
INIT_LAT = os.environ["INIT_LAT"]
INIT_LNG = os.environ["INIT_LNG"]

# AWS
SENDER = os.environ["SENDER"]
CHARSET = os.environ["CHARSET"]
AWS_REGION = os.environ["AWS_REGION"]
AWS_ACC_ID = os.environ["AWS_ACC_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]

# DB
DB_NAME = os.environ["DB_NAME"]
DB_PATH = os.path.join(BASE_DIR, "db", DB_NAME)

# KEYCLOAK
KC_SERVER_URL = os.environ["KC_SERVER_URL"]
KC_CLIENT_ID = os.environ["KC_CLIENT_ID"]
REALM_NAME = os.environ["REALM_NAME"]

REDIRECT_LOGIN = os.environ["REDIRECT_LOGIN"]
REDIRECT_LOGOUT = os.environ["REDIRECT_LOGOUT"]
REDIRECT_REGISTER = os.environ["REDIRECT_REGISTER"]
