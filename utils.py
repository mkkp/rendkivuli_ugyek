"""
General utility functions for MKKP városfelújítós
"""
import os
import re
import uuid

from datetime import datetime as dt
from PIL import Image
from pathlib import Path


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
    from models import db
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
        
        #SAVE     
        picture.save(upload_path)

        #THUMBNAIL
        thumbnail_pic = resize(THUMBNAIL_SIZE, upload_path)
        
        thumbnail_name = f"{submission_id}_{unique_id}_{tag}_thumbnail_{img_count}.{original_suffix}"
        
        thumbnail_path = os.path.join(picture_dir, thumbnail_name)
        thumbnail_pic.save(thumbnail_path)

        #UPDATE DB MODELS
        if tag == "before":
            from models import ImageBeforeModel
            image = ImageBeforeModel(parent_id = submission_id,
		                     file_name = new_filename,
		                     thumb_file_name = thumbnail_name,
		                     created_date=get_date()
		                    )
        if tag == "after":
            from models import ImageAfterModel
            image = ImageAfterModel(parent_id = submission_id,
		                    file_name = new_filename,
		                    thumb_file_name = thumbnail_name,
		                    created_date=get_date()
		                   )

        from models import SubmissionModel	                   
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
