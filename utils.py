"""
General utility functions for MKKP városfelújítós
"""
import os
import re
import uuid

from datetime import datetime as dt
from PIL import Image
from PIL import ImageOps
from pathlib import Path
from random import randint

from models import db
from models import SubmissionModel
from models import ImageBeforeModel
from models import ImageAfterModel

def valid_email(email: str) -> bool:
    """
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
    if re.fullmatch(pattern, email):
        return True
    else:
        return False
        

def get_date():
    """
    ISO 8601
    """
    return dt.now().strftime("%Y-%m-%d")
 

def save_picture(pictures, upload_folder, tag, submission_id):
    """
    """
    from config import THUMBNAIL_SIZE
    img_count = 1
    
    picture_dir = os.path.join(upload_folder, submission_id)
    
    for picture in pictures:
    
        unique_id = str(uuid.uuid4()).split("-")[:1][0]

        #CREATE FOLDER
        if not os.path.exists(picture_dir):
            os.mkdir(picture_dir)

        #GET ORIGINAL EXTENSION
        original_suffix = picture.filename.split(".")[-1:][0]
        
        #CREATE FILE NAME
        new_filename = f"{submission_id}_{unique_id}_{tag}__{img_count}.{original_suffix}"
        
        upload_path = os.path.join(picture_dir, new_filename)
        
        #SAVE ORIGINAL
        picture = Image.open(picture)
        fixed_image = ImageOps.exif_transpose(picture)
        fixed_image.save(upload_path)

        #SAVE THUMBNAIL
        thumbnail_pic = resize(THUMBNAIL_SIZE, upload_path)
        thumbnail_name = f"{submission_id}_{unique_id}_{tag}_thumbnail_{img_count}.{original_suffix}"
        thumbnail_path = os.path.join(picture_dir, thumbnail_name)
        fixed_thumbnail = ImageOps.exif_transpose(thumbnail_pic)
        fixed_thumbnail.save(thumbnail_path)

        #UPDATE DB MODELS
        if tag == "before":
            
            image = ImageBeforeModel(parent_id = submission_id,
		                     file_name = new_filename,
		                     thumb_file_name = thumbnail_name,
		                     created_date=get_date()
		                    )
        if tag == "after":
            
            image = ImageAfterModel(parent_id = submission_id,
		                    file_name = new_filename,
		                    thumb_file_name = thumbnail_name,
		                    created_date=get_date()
		                   )

	#UPDATE SUBMISSION          
        submission = SubmissionModel.query.filter_by(id=submission_id).first()
        submission.cover_image = thumbnail_name
	
        db.session.add(image)
        db.session.commit()

        img_count += 1
        
    return


def mk_upload_dir(upload_dir: str):
    """
    """
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)
    return
    
    
def resize(size: tuple, file_path:str):
    """
    resizes picture
    """
    file_path = Path(file_path)
    original = Image.open(file_path)
    resized = original.copy()
    resized.thumbnail(size)
    return resized
    

def get_random_name():
    in_dir = Path(os.path.dirname(__file__))
    file_name = "random_name_list.txt"
    with open(in_dir/file_name, "r", encoding="UTF-8") as file:
        name_list = [name.strip() for name in file.readlines()]
    return name_list[randint(1, len(name_list))]

