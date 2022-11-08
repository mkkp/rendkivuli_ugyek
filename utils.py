"""
General utility functions for MKKP városfelújítós
"""
import os
import re
import uuid

from datetime import datetime as dt
from pathlib import Path
from random import randint

from PIL import Image
from PIL import ImageOps
from PIL import UnidentifiedImageError

from config import THUMBNAIL_SIZE
from config import FULL_SIZE

from models import db
from models import SubmissionModel
from models import ImageBeforeModel
from models import ImageAfterModel


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
        try:
            picture = Image.open(picture)
        except UnidentifiedImageError:
            return "not allowed extension"
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

