"""
General utility functions for MKKP városfelújítós
"""
import os
import re
import uuid
import logging
import json

from dotenv import load_dotenv
from datetime import datetime as dt
from functools import wraps
from pathlib import Path
from random import randint

from flask import redirect
from flask import flash
from flask_login import current_user
from flask_login import login_required

from PIL import Image
from PIL import ImageOps

from models import db
from models import SubmissionModel
from models import ImageBeforeModel
from models import ImageAfterModel

logger = logging.getLogger("rum.utils")

THUMBNAIL_SIZE = (1000, 1000)
FULL_SIZE = (1200, 2400)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def valid_email(email: str) -> bool:
    """
    #
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
    if re.fullmatch(pattern, email):
        return True


def get_date():
    """
    ISO 8601
    """
    return dt.now().strftime("%Y-%m-%d")


def save_picture(pictures, upload_folder, tag, submission_id):
    """
    #
    """
    img_count = 1
    picture_dir = os.path.join(upload_folder, submission_id)

    for picture in pictures:
        """Az adatlapon keresztül utólagosan feltöltött képek is a save_picture API-t használják,
        ami nem veszi figyelembe hogy eddig hány kép lett elmentve milyen sorszámmal.
        Ez azt eredményezi, hogy lehet két ugyanolyan nevű de más tartalmú képünk is.
        Tehát img 1_1.jpg ami az első bejelentés első képének a neve
        és a 1_1.jpg ami egy az adatlapról utólagosan hozzáadott másik kép.
        A keveredés elkerülésére egy 8 számjegyű random szám is beleíródik a kép címébe.
        A unique_id-ra való támaszkodás megszűntethető lenne, ha a save_picture API
        figyelembe venné a legnagyobb kiosztott kép sorszámot és onnan folytaná a sorszám kiosztást (img_count).
        """
        unique_id = str(uuid.uuid4()).split("-")[:1][0]

        # CREATE FOLDER
        if not os.path.exists(picture_dir):
            os.mkdir(picture_dir)

        # GET ORIGINAL EXTENSION
        original_suffix = picture.filename.split(".")[-1:][0]

        # CREATE FILE NAME
        new_filename = (
            f"{submission_id}_{unique_id}_{tag}_{img_count}.{original_suffix}"
        )

        upload_path = os.path.join(picture_dir, new_filename)

        # SAVE ORIGINAL
        picture = Image.open(picture)
        fixed_image = ImageOps.exif_transpose(picture)
        fixed_image.save(upload_path)

        # SAVE THUMBNAIL
        thumbnail_pic = resize(THUMBNAIL_SIZE, upload_path)
        thumbnail_name = (
            f"{submission_id}_{unique_id}_{tag}_thumbnail_{img_count}.{original_suffix}"
        )
        thumbnail_path = os.path.join(picture_dir, thumbnail_name)
        fixed_thumbnail = ImageOps.exif_transpose(thumbnail_pic)
        fixed_thumbnail.save(thumbnail_path)

        # UPDATE DB MODELS
        if tag == "before":
            image = ImageBeforeModel(
                parent_id=submission_id,
                file_name=new_filename,
                thumb_file_name=thumbnail_name,
                created_date=get_date(),
            )
        if tag == "after":
            image = ImageAfterModel(
                parent_id=submission_id,
                file_name=new_filename,
                thumb_file_name=thumbnail_name,
                created_date=get_date(),
            )

        # UPDATE SUBMISSION
        submission = SubmissionModel.query.filter_by(id=submission_id).first()
        submission.cover_image = thumbnail_name
        submission.cover_image_full = new_filename

        db.session.add(image)
        db.session.commit()

        img_count += 1

    return


def mk_upload_dir(upload_dir: str):
    "#"
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)


def resize(size: tuple, file_path: str):
    """
    resizes picture
    """
    file_path = Path(file_path)
    original = Image.open(file_path)
    resized = original.copy()
    resized.thumbnail(size)
    return resized


def get_random_name():
    "#"
    in_dir = Path(os.path.dirname(__file__))
    file_name = "random_name_list.txt"
    with open(in_dir / file_name, "r", encoding="UTF-8") as file:
        name_list = [name.strip() for name in file.readlines()]
    return name_list[randint(1, len(name_list))]


def auditlog(event):
    ts = dt.now().strftime("%Y-%m-%d %H:%M")
    with open(Path(BASE_DIR) / f"sec_log.txt", "a") as f:
        f.write(f"\n{ts},{current_user.email},{event}")
    return


class MockBoto3Client:
    def send_email(self, **kwargs):
        logger.info(
            "Mail would have been sent: {}".format(
                json.dumps(kwargs, indent=4, sort_keys=True, ensure_ascii=False)
            )
        )


class MockOauth2Client:
    def __init__(self, client_id):
        self.client_id = client_id

    @property
    def auth0(self):
        return self

    def register(self, name, client_id, **kwargs):
        self.client_id = client_id

    def authorize_redirect(self, redirect_uri):
        # XXX: Not using redirect_url, since it is forced to be https
        # and we want to test on simple http too on localhost.
        return redirect("/callback")

    def authorize_access_token(self):
        return {
            "userinfo": {
                "email": "ketfarku@kutyi.kuty",
                "aud": self.client_id,
                "name": "Teszt Elek",
            }
        }


def role_required(required_roles):
    if isinstance(required_roles, str):
        required_roles = (required_roles,)

    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if current_user.role not in required_roles:
                flash("Ez a funkcionalitás nagykutyáknak van fenntartva.", "danger")
                return redirect("/")
            return func(*args, **kwargs)

        return login_required(wrapped_func)

    return decorator
