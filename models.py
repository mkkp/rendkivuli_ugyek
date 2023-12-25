"""
SQLAlchemy schema model definitons

Migration steps:
1. pip install Flask-migrate
2. cd to Flask project library
3. flask db init
4. flask db migrate -m "-some commit text-"
5. flask db upgrade
"""
from flask_login import UserMixin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

login = LoginManager()
db = SQLAlchemy()

@login.user_loader
def load_user(id):
    "#"
    return UserModel.query.get(int(id))


class UserModel(UserMixin, db.Model):
    """
    table schema for users
    """

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    create = db.Column(db.Boolean())
    read = db.Column(db.Boolean())
    update = db.Column(db.Boolean())
    delete = db.Column(db.Boolean())
    active = db.Column(db.Boolean())
    role = db.Column(db.String(10))
    created_date = db.Column(db.String(10))  # 2022-09-01
    email = db.Column(db.String(80), unique=True)  # GDPR
    inactive_date = db.Column(db.String(10))  # 2022-09-01
    last_login = db.Column(db.String(10))  # 2022-09-01
    phone = db.Column(db.String(20))  # GDPR
    user_name = db.Column(db.String(100), unique=True)
    verified = db.Column(db.Boolean())


class SubmissionModel(db.Model):
    """
    table schema for submitted cases
    """

    __tablename__ = "submission"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    problem_type = db.Column(db.String())
    description = db.Column(db.String())
    suggestion = db.Column(db.String())
    solution = db.Column(db.String())
    address = db.Column(db.String())
    zipcode = db.Column(db.Integer)
    city = db.Column(db.String())
    county = db.Column(db.String())
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    submitter_email = db.Column(db.String())
    submitter_phone = db.Column(db.String())
    owner_email = db.Column(db.String())
    owner_user = db.Column(db.String())
    created_date = db.Column(db.String())
    cover_image = db.Column(db.String())
    cover_image_full = db.Column(db.String())
    featured = db.Column(db.Boolean())
    status = db.Column(db.String())
    status_changed_date = db.Column(db.String())  # 2022-09-01
    status_changed_by = db.Column(db.String())


class featuredModel(db.Model):
    """
    table schema for featured submissions
    """

    __tablename__ = "featured"
    
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.String(10))
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))


class CommentModel(db.Model):
    """
    table schema for comments
    """

    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    commenter = db.Column(db.String(120))
    created_date = db.Column(db.String(10))
    body = db.Column(db.String())
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))


class ImageBeforeModel(db.Model):
    """
    table schema for images before fix
    """

    __tablename__ = "image_before"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(80))
    thumb_file_name = db.Column(db.String(128))
    created_date = db.Column(db.String(10))
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))


class ImageAfterModel(db.Model):
    """
    table schema for images afer fix
    """

    __tablename__ = "image_after"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(80))
    thumb_file_name = db.Column(db.String(128))
    created_date = db.Column(db.String(10))
    parent_id = db.Column(db.Integer, db.ForeignKey("submission.id"))

