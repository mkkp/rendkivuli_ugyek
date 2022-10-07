"""
SQLAlchemy schema model definitons
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import LoginManager
from datetime import datetime as dt

login = LoginManager()
db = SQLAlchemy()

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

class UserModel(UserMixin, db.Model):
    """
    table schema for users
    UPDATE user SET role = 'coordinator' WHERE email = 'feher.aron@gmail.com';
    UPDATE user SET role = 'admin' WHERE email = 'feher.aron@gmail.com';
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    create = db.Column(db.Boolean())
    read = db.Column(db.Boolean())
    update = db.Column(db.Boolean())
    delete = db.Column(db.Boolean())
    active = db.Column(db.Boolean())
    role = db.Column(db.String(10))
    created_date = db.Column(db.String(10)) #2022-09-01
    email = db.Column(db.String(80), unique=True) #GDPR
    inactive_date = db.Column(db.String(10)) #2022-09-01
    last_login = db.Column(db.String(10)) #2022-09-01
    phone = db.Column(db.String(20), unique=True) #GDPR
    user_name = db.Column(db.String(100), unique=True)
    verified = db.Column(db.Boolean())
         
class SubmissionModel(db.Model):
    """
    table schema for submitted cases
    """
    __tablename__ = 'submission'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True)
    problem_type = db.Column(db.String(), index=True)
    description = db.Column(db.String())
    suggestion = db.Column(db.String())
    solution = db.Column(db.String())
    address = db.Column(db.String())
    city = db.Column(db.String())
    county = db.Column(db.String())
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    submitter_email = db.Column(db.String(), index=True)
    owner_email = db.Column(db.String(), index=True)
    owner_user = db.Column(db.String(), index=True)
    created_date = db.Column(db.String())
    cover_image = db.Column(db.String())
    status = db.Column(db.String())
    status_changed_date = db.Column(db.String()) #2022-09-01
    status_changed_by = db.Column(db.String(), index=True)


class CommentModel(db.Model):
    """
    table schema for comments
    """
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    commenter = db.Column(db.String(120))
    created_date = db.Column(db.String(10))
    body = db.Column(db.String())
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))
    

class ImageBeforeModel(db.Model):
    """
    table schema for images before fix
    """
    __tablename__ = 'image_before'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(80))
    thumb_file_name = db.Column(db.String(128))
    created_date = db.Column(db.String(10))
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))
    
        
class ImageAfterModel(db.Model):
    """
    table schema for images afer fix
    """
    __tablename__ = 'image_after'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(80))
    thumb_file_name = db.Column(db.String(128))
    created_date = db.Column(db.String(10))
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))
    

