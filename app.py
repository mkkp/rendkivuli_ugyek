"""
MKKP városfelújítós alkalmazás
"""
# -------------------------------
# ---------I M P O R T S---------
# -------------------------------

# BUILTINS
import os
import shutil
from random import randint
import logging

# THIRD PARTY MODULES
import boto3  # AWS
from botocore.exceptions import ClientError

from dotenv import load_dotenv
import flask_excel as excel
import flask_monitoringdashboard as dashboard

# Geojson
from geojson import Feature
from geojson import Point
from geojson import FeatureCollection
from geojson import dumps as gj_dump

# Flask
from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

# Flask-Migrate
from flask_migrate import Migrate

# Flask Login
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from flask_cors import CORS
from flask_paranoid import Paranoid

# AUTH0
from authlib.integrations.flask_client import OAuth

# DATABASE MODELS
from models import UserModel
from models import db
from models import login
from models import SubmissionModel
from models import ImageBeforeModel
from models import ImageAfterModel
from models import CommentModel

# UTILS
from utils import valid_email
from utils import get_date
from utils import save_picture
from utils import get_random_name
from utils import write_log
from utils import MockBoto3Client
from utils import MockOauth2Client

# MAIL TEMPLATES

from mail_template import create_submission_mail_SES
from mail_template import create_status_change_mail_SES
from mail_template import create_solution_mail_SES
from mail_template import create_organiser_mail_SES

# -------------------------------
# ---------C O N F I G-----------
# -------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rum.app")

if load_dotenv():
    logger.info("loading env...")
else:
    logger.warn("---internal .env was not found---")

# APP
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/upload")

DEBUG_MODE = os.environ["DEBUG_MODE"]
PORT = os.environ["PORT"]
APP_SECRET_KEY = os.environ["APP_SECRET_KEY"]
ROWS_PER_PAGE = int(os.environ["ROWS_PER_PAGE"])

##MAP
MAP_KEY = os.environ["MAP_KEY"]
INIT_LAT = os.environ["INIT_LAT"]
INIT_LNG = os.environ["INIT_LNG"]

# AWS
SENDER = os.environ["SENDER"]
CHARSET = os.environ["CHARSET"]
AWS_REGION = os.environ["AWS_REGION"]
AWS_ACC_ID = os.environ["AWS_ACC_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]

##DB
DB_NAME = os.environ["DB_NAME"]
DB_PATH = os.path.join(BASE_DIR, "db", DB_NAME)

# AUTH0
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]

##APP
app = Flask(__name__)
migrate = Migrate(app, db)

##OAUTH
if AUTH0_CLIENT_ID == "MOCK":
    oauth = MockOauth2Client(AUTH0_CLIENT_ID)
else:
    oauth = OAuth(app)

    oauth.register(
        "auth0",
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    )

# APP CONFIG
app.secret_key = APP_SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH

##DATABASE
db.init_app(app)


# DASHBOARD
dashboard.bind(app)

# CORS
# https://flask-cors.readthedocs.io/en/latest/
CORS(app)

# Paranoid
# https://pypi.org/project/Flask-Paranoid/
paranoid = Paranoid(app)
paranoid.redirect_view = "/"

# FLASK-LOGIN Config
login.init_app(app)
login.login_view = "login"

# AWS SES
if AWS_REGION == "MOCK":
    client = MockBoto3Client()
else:
    client = boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACC_ID,
        aws_secret_access_key=AWS_SECRET,
    )


# -------------------------------
# ---------V I E W S-------------
# -------------------------------


# ADATBÁZIS LÉTREHOZÁSA
@app.before_first_request
def create_all():
    """
    If no app.db is present, it creates app.db
    based on schema that is defined in models.py
    """
    db.create_all()


# INDEX
@app.route("/", methods=["GET"])
def index():
    """
    Kezdőoldal
    Bejelentkezés nem szükséges
    """
    return render_template("index.html")


# ÜGY BEJELENTÉS
@app.route("/submission", methods=["POST", "GET"])
def add_submission():
    """
    Bejelentkezés nem szükséges
    """
    if request.method == "POST":
        # Email validaiton
        if not valid_email(request.form["email"]):
            flash("A Kutya mindenit de fura ez az email cím!", "danger")
            return render_template(
                "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
            )

        # Embedded link validation
        if "http" in request.form["title"]:
            flash("A szöveg nem tartalmazhat linket!", "danger")
            return render_template(
                "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
            )

        # Naive XSS validation
        if "<" in request.form["title"] or ">" in request.form["title"]:
            flash("Nem megengedett karakter.", "danger")
            return render_template(
                "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
            )

        if "<" in request.form["type"] or ">" in request.form["type"]:
            flash("Nem megengedett karakter.", "danger")
            return render_template(
                "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
            )

        if "<" in request.form["address"] or ">" in request.form["address"]:
            flash("Nem megengedett karakter.", "danger")
            return render_template(
                "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
            )

        submission = SubmissionModel(
            title=request.form["title"],
            problem_type=request.form["type"],
            description=request.form["description"],
            suggestion=request.form["suggestion"],
            city=request.form["city"],
            zipcode=request.form["zipcode"],
            county=request.form["county"],
            address=request.form["address"],
            lat=request.form["lat"],
            lng=request.form["lng"],
            submitter_email=request.form["email"],
            submitter_phone=request.form["phone"],
            owner_email="",
            status="Bejelentve",
            featured=False,
            status_changed_date=get_date(),
            status_changed_by=request.form["email"],
            created_date=get_date(),
        )

        db.session.add(submission)
        db.session.commit()

        # SAVE PICTURES
        pictures = request.files.getlist("files")
        additional_pictures = request.files.getlist("additional_files")

        if additional_pictures[0].filename != "":
            pictures = pictures + additional_pictures

        tag = "before"

        result = save_picture(
            pictures=pictures,
            upload_folder=UPLOAD_FOLDER,
            tag=tag,
            submission_id=str(submission.id),
        )

        # SEND EMAIL
        SUBJECT = "Sikeres városmódosító bejelentés!"
        BODY_HTML = create_submission_mail_SES(submission)
        RECIPIENT = request.form["email"]

        try:
            response = client.send_email(
                Destination={"ToAddresses": [RECIPIENT]},
                Message={
                    "Subject": {"Charset": CHARSET, "Data": SUBJECT},
                    "Body": {"Html": {"Charset": CHARSET, "Data": BODY_HTML}},
                },
                Source=SENDER,
            )
        except Exception as err:
            logger.error("Error sending email", err)

        flash("Sikeres bejelentés! Küldtünk egy levelet is!", "success")
        return redirect(f"/single_submission/{submission.id}")

    if request.method == "GET":
        return render_template(
            "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
        )


# ÜGY ADATAINAK MÓDOSÍTÁSA
@app.route("/change_submission_data/<submission_id>", methods=["POST", "GET"])
@login_required
def change_submission_data(submission_id):
    """
    Pylint R0915: Too many statements (53/50) (too-many-statements)
    #TODO: szétszedni több függvényre
    """
    submission = SubmissionModel.query.filter_by(id=submission_id).first()

    if request.method == "POST":
        if request.form["new_title"] != "":
            new_title = request.form["new_title"]
            submission.title = new_title
            db.session.commit()
            flash("Sikeresen módosítottad az ügy megnevezését!", "success")

        if request.form["new_email"] != "":
            new_email = request.form["new_email"]
            submission.submitter_email = new_email
            db.session.commit()
            flash("Sikeresen módosítottad az ügy bejelentő email címét!", "success")

        if request.form["new_phone"] != "":
            new_phone = request.form["new_phone"]
            submission.submitter_phone = new_phone
            db.session.commit()
            flash("Sikeresen módosítottad az ügy bejelentő telefonszámát!", "success")

        if request.form["new_type"] != submission.problem_type:
            new_type = request.form["new_type"]
            submission.problem_type = new_type
            db.session.commit()
            flash("Sikeresen módosítottad az ügy típusát!", "success")

        if request.form["new_description"] != "":
            new_description = request.form["new_description"]
            submission.description = new_description
            db.session.commit()
            flash("Sikeresen módosítottad az ügy leírását!", "success")

        if request.form["new_suggestion"] != "":
            new_suggestion = request.form["new_suggestion"]
            submission.suggestion = new_suggestion
            db.session.commit()
            flash("Sikeresen módosítottad az ügy megoldási javaslatát!", "success")

        if request.form["new_created_date"] != "":
            new_created_date = request.form["new_created_date"]
            submission.created_date = new_created_date
            db.session.commit()
            flash("Sikeresen módosítottad az ügy bejelentési dátumát!", "success")

        try:
            featured = request.form["featured"]
            if submission.featured != True:
                submission.featured = True
                db.session.commit()
                flash("Sikeresen kiemelted az ügyet!", "success")

        except Exception as e:
            submission.featured = False
            db.session.commit()

        if request.form["status"] != submission.status:
            new_status = request.form["status"]
            changed_by = request.form["current_user"]

            submission.status = new_status
            submission.status_changed_date = get_date()
            submission.status_changed_by = changed_by
            db.session.commit()

            # MAIL TO SZERVEZŐ
            if submission.owner_email != "":
                SUBJECT = f"Státusz változás: {submission.title}"
                BODY_HTML = create_status_change_mail_SES(submission)
                RECIPIENT = submission.owner_email
                try:
                    client.send_email(
                        Destination={"ToAddresses": [RECIPIENT]},
                        Message={
                            "Subject": {"Charset": CHARSET, "Data": SUBJECT},
                            "Body": {"Html": {"Charset": CHARSET, "Data": BODY_HTML}},
                        },
                        Source=SENDER,
                    )
                except Exception as err:
                    pass

                flash(
                    f"Sikeresen módosítottad az ügy státuszát erre: {new_status}. A szervezőnek ment levél.",
                    "success",
                )

            else:
                flash(
                    f"Sikeresen módosítottad az ügy státuszát erre: {new_status}",
                    "success",
                )

            if new_status == "Megoldva":
                SUBJECT = f"RÜM befejezett ügy: {submission.title}"
                BODY_HTML = create_solution_mail_SES(submission)
                RECIPIENT = submission.submitter_email

                try:
                    client.send_email(
                        Destination={"ToAddresses": [RECIPIENT]},
                        Message={
                            "Subject": {"Charset": CHARSET, "Data": SUBJECT},
                            "Body": {"Html": {"Charset": CHARSET, "Data": BODY_HTML}},
                        },
                        Source=SENDER,
                    )
                except Exception as err:
                    pass

        if request.form["closing_solution"].strip() != "":
            closing_solution = request.form["closing_solution"]
            changed_by = request.form["current_user"]
            submission.solution = closing_solution
            submission.status_changed_date = get_date()
            submission.status_changed_by = changed_by
            db.session.commit()

            flash(
                "Sikeresen hozzáadtad a bejelentés zárószövegét!",
                "success",
            )

        if request.form["new_address"] != "":
            new_address = request.form["new_address"]
            city = request.form["city"]
            zipcode = request.form["zipcode"]
            county = request.form["county"]
            lat = request.form["lat"]
            lng = request.form["lng"]

            submission.address = new_address
            submission.county = county
            submission.zipcode = zipcode
            submission.city = city
            submission.lat = lat
            submission.lng = lng

            db.session.commit()
            flash("Sikeresen módosítottad a címet!", "success")

        return redirect(f"/single_submission/{submission_id}")

    return render_template(
        "change_submission_data.html", submission=submission, ACCESS_KEY=MAP_KEY
    )


# BEJELENTÉS ADATLAP
@app.route("/single_submission/<id>", methods=["POST", "GET"])
def single_submission(id):
    "#"
    submission_id = str(id)

    if request.method == "POST":
        if "comment-submit" in request.form:
            form_comment = request.form["comment"]

            if CommentModel.query.filter_by(
                body=form_comment, parent_id=submission_id
            ).first():
                # comment is a duplicate
                pass

            else:
                comment = CommentModel(
                    commenter=request.form["current_user"],
                    created_date=get_date(),
                    body=form_comment,
                    parent_id=submission_id,
                )
                db.session.add(comment)
                db.session.commit()
                flash(f"Sikeresen hozzáadtál egy kommentet!", "success")

        if "comment-edit" in request.form:
            body_change = request.form["comment"]
            comment_id = request.form["comment_id"]
            comment = CommentModel.query.filter_by(id=comment_id).first()
            comment.body = body_change
            comment.created_date = get_date()
            db.session.commit()
            flash(f"Komment szerkesztve", "success")

        if "upload_before_images" in request.form:
            tag = "before"
            pictures = request.files.getlist("files")
            save_picture(pictures, UPLOAD_FOLDER, tag, submission_id)
            flash(f"Kép sikeresen hozzáadva!", "success")

        if "upload_after_images" in request.form:
            tag = "after"
            pictures = request.files.getlist("files")
            save_picture(pictures, UPLOAD_FOLDER, tag, submission_id)

            # Ha kerül fel egy bejelentéshez utána kép, akkor szerintem átállhatna magától a bejelentés státusza befejezettre
            changed_by = request.form["current_user"]
            submission = SubmissionModel.query.filter_by(id=submission_id).first()
            submission.status = "Megoldva"
            submission.status_changed_date = get_date()
            submission.status_changed_by = changed_by
            db.session.commit()
            # send mail
            SUBJECT = f"RÜM befejezett ügy: {submission.title}"
            BODY_HTML = create_solution_mail_SES(submission)
            RECIPIENT = submission.submitter_email

            try:
                client.send_email(
                    Destination={"ToAddresses": [RECIPIENT]},
                    Message={
                        "Subject": {"Charset": CHARSET, "Data": SUBJECT},
                        "Body": {"Html": {"Charset": CHARSET, "Data": BODY_HTML}},
                    },
                    Source=SENDER,
                )
            except Exception as err:
                pass

    submission = SubmissionModel.query.filter_by(id=submission_id)
    before_img_list = ImageBeforeModel.query.filter_by(parent_id=submission_id)
    after_img_list = ImageAfterModel.query.filter_by(parent_id=submission_id)
    comment_list = CommentModel.query.filter_by(parent_id=submission_id)

    return render_template(
        "single_submission.html",
        submission=submission,
        before_img_list=before_img_list,
        after_img_list=after_img_list,
        comment_list=comment_list,
        ACCESS_KEY=MAP_KEY,
    )


# ÖSSZES BEJELENTÉS KÁRTYÁI
@app.route("/all_submission/", methods=["POST", "GET"])
def all_submission():
    "#"
    page = request.args.get("page", 1, type=int)

    post_list = SubmissionModel.query.order_by(
        SubmissionModel.created_date.desc()
    ).paginate(page=page, per_page=ROWS_PER_PAGE)

    featured = SubmissionModel.query.filter_by(featured=True).all()

    if request.method == "POST":
        county = request.form["county"]
        zipcode = request.form["zipcode"]
        problem_type = request.form["type"]
        status = request.form["status"]
        search_text = request.form["full_text_search"]

        county_dict = {}
        zipcode_dict = {}
        problem_type_dict = {}
        status_dict = {}
        text_dict = {}

        if county != "":
            county_dict = {"county": county}

        if zipcode != "":
            zipcode_dict = {"zipcode": zipcode[:-1]}

        if problem_type != "":
            problem_type_dict = {"problem_type": problem_type}

        if status != "":
            status_dict = {"status": status}

        if search_text != "":
            search_text = search_text.lower()
            filtered_list = (
                SubmissionModel.query.filter(
                    SubmissionModel.description.ilike(f"%{search_text}%")
                )
                .order_by(SubmissionModel.created_date.desc())
                .paginate(page=page, per_page=ROWS_PER_PAGE)
            )

            # A szöveges kereső még nincs integrálva a többi keresőopcióval,
            # ezért vagy-vagy alapon lehet használni
            return render_template("all_submission.html", post_list=filtered_list)

        # merge dicts
        query_dict = county_dict | zipcode_dict | problem_type_dict | status_dict

        # store dict in session cookie
        session["filter"] = query_dict

        try:
            filtered_list = (
                SubmissionModel.query.filter_by(**query_dict)
                .order_by(SubmissionModel.created_date.desc())
                .paginate(page=1, per_page=ROWS_PER_PAGE)
            )

        except Exception as e:
            flash("Nincs találati eredmény", "danger")
            return render_template("all_submission.html", post_list=post_list)

        return render_template(
            "all_submission.html", post_list=filtered_list, filters=query_dict
        )

    # GET
    try:
        if "filter" in session.keys():
            query_dict = session["filter"]
            filtered_list = (
                SubmissionModel.query.filter_by(**query_dict)
                .order_by(SubmissionModel.created_date.desc())
                .paginate(page=page, per_page=ROWS_PER_PAGE)
            )
            return render_template(
                "all_submission.html",
                post_list=filtered_list,
                featured=featured,
                filters=query_dict,
            )
    except Exception as err:
        pass

    return render_template(
        "all_submission.html", post_list=post_list, featured=featured
    )


# BEJELENTÉS SZERVEZŐ HOZZÁADÁSA
@app.route("/assign/<id>", methods=["POST", "GET"])
@login_required
def assign(id):
    "#"
    user_list = UserModel.query.all()
    submission = SubmissionModel.query.filter_by(id=id).first()

    if request.method == "POST":
        submission.owner_email = request.form["email"]
        submission.owner_user = request.form["username"]
        submission.status = "Folyamatban"
        db.session.commit()

        # send mail
        SUBJECT = f"RÜM szervező lettél!"
        BODY_HTML = create_organiser_mail_SES(submission)
        RECIPIENT = request.form["email"]

        try:
            client.send_email(
                Destination={"ToAddresses": [RECIPIENT]},
                Message={
                    "Subject": {"Charset": CHARSET, "Data": SUBJECT},
                    "Body": {"Html": {"Charset": CHARSET, "Data": BODY_HTML}},
                },
                Source=SENDER,
            )
        except Exception as err:
            pass

        flash("Szervező sikeresen hozzáadva!", "success")
        return redirect(f"/single_submission/{id}")

    return render_template("assign.html", user_list=user_list, submission=submission)


# KOMMENT TÖRLÉS
@app.route("/delete_comment/<id>", methods=["GET"])
@login_required
def delete_comment(id):
    "#"

    comment = CommentModel.query.filter_by(id=id)
    submission_id = comment.first().parent_id
    comment.delete()
    db.session.commit()
    flash("A kommentet sikeresen töröltük!", "success")
    return redirect(f"/single_submission/{submission_id}")


# KÉP TÖRLÉS
@app.route("/delete_picture/<status_type>/<id>", methods=["GET"])
@login_required
def delete_picture(status_type, id):
    "#"
    if status_type == "before":
        picture = ImageBeforeModel.query.filter_by(id=id)
    if status_type == "after":
        picture = ImageAfterModel.query.filter_by(id=id)

    submission_id = picture.first().parent_id
    picture.delete()
    db.session.commit()
    flash("A képet sikeresen töröltük!", "success")
    return redirect(f"/single_submission/{submission_id}")


# BORÍTÓKÉP MÓDOSÍTÁSA
@app.route("/change_cover/<status_type>/<id>", methods=["GET"])
@login_required
def change_cover(status_type, id):
    "#"
    if status_type == "before":
        picture = ImageBeforeModel.query.filter_by(id=id)
    if status_type == "after":
        picture = ImageAfterModel.query.filter_by(id=id)

    submission_id = picture.first().parent_id
    submission = SubmissionModel.query.filter_by(id=submission_id).first()
    submission.cover_image = picture.first().thumb_file_name
    submission.cover_image_full = picture.first().file_name

    db.session.commit()

    flash(
        """A borítókép cserélési eljárás
             előkészítését elindítottuk.
             Ügyintézőnk egy héten belül jelentkezik.
             Kérjük, addig ne mozduljon a készüléke mellől!
         """,
        "success",
    )
    return redirect(f"/single_submission/{submission_id}")


# BEJELENTÉS TÖRLÉS
@app.route("/delete_submission/<id>", methods=["GET"])
@login_required
def delete_submission(id):
    "#"

    write_log(BASE_DIR, current_user, f"delete submission_{id}")

    if current_user.role != "admin" and current_user.role != "coordinator":
        flash("Bejelentést csak admin vagy kordinátor törölhet!", "danger")
        return render_template("index.html")

    submission = SubmissionModel.query.filter_by(id=id)
    submission.delete()

    images_before = ImageBeforeModel.query.filter_by(parent_id=id)
    images_after = ImageAfterModel.query.filter_by(parent_id=id)
    comments = CommentModel.query.filter_by(parent_id=id)

    shutil.rmtree(os.path.join(UPLOAD_FOLDER, str(id)))

    images_before.delete()
    images_after.delete()
    submission.delete()
    comments.delete()

    db.session.commit()
    flash("A bejegyzést sikeresen töröltük!", "success")
    return redirect("/")


# STATISZTIKA
@app.route("/statistics", methods=["POST", "GET"])
def statistics():
    "#"

    post_count = SubmissionModel.query.count()
    user_count = UserModel.query.count()
    submitted_count = SubmissionModel.query.filter_by(status="Bejelentve").count()
    wip_count = SubmissionModel.query.filter_by(status="Folyamatban").count()
    progress_count = SubmissionModel.query.filter_by(status="Készül").count()
    completed_count = SubmissionModel.query.filter_by(status="Megoldva").count()
    awareness_count = SubmissionModel.query.filter_by(status="Figyelemfelhívás").count()

    grouped = SubmissionModel.query.group_by("county").all()
    county_count_dict = {}
    for i in grouped:
        county_count_dict[i.county] = SubmissionModel.query.filter_by(
            county=i.county
        ).count()
    county_dump = gj_dump(county_count_dict, sort_keys=True)

    return render_template(
        "statistics.html",
        post_count=post_count,
        user_count=user_count,
        submitted_count=submitted_count,
        wip_count=wip_count,
        progress_count=progress_count,
        completed_count=completed_count,
        awareness_count=awareness_count,
        county_count_dict=county_dump,
    )


# TÉRKÉP
@app.route("/full_map", methods=["POST", "GET"])
def full_map():
    "#"
    emtpy_result = False

    if request.method == "POST":
        submission_type = request.form["type"]
        submission_status = request.form["status"]

        problem_type_dict = {}
        status_dict = {}

        if submission_type != "":
            problem_type_dict = {"problem_type": submission_type}

        if submission_status != "":
            status_dict = {"status": submission_status}

        query_dict = problem_type_dict | status_dict

        filtered_list = SubmissionModel.query.filter_by(**query_dict).all()

        if len(filtered_list) == 0:
            filtered_list = SubmissionModel.query.all()
            emtpy_result = True

        point_list = []
        for i, post in enumerate(filtered_list):
            i = Feature(geometry=Point((post.lng, post.lat)))
            i.properties["id"] = post.id
            i.properties["title"] = post.title
            i.properties["status"] = post.status
            i.properties["type"] = post.problem_type
            i.properties["cover_image"] = post.cover_image
            point_list.append(i)

        feature_collection = FeatureCollection(point_list)
        dump = gj_dump(feature_collection, sort_keys=True)

        if emtpy_result:
            flash(
                f"Sajnos nem találtuk a {submission_type} és {submission_status} keresztmetszetét.",
                "warning",
            )
            submission_type = None
            submission_status = None

        return render_template(
            "map.html",
            ACCESS_KEY=MAP_KEY,
            lat=INIT_LAT,
            lng=INIT_LNG,
            post_list=filtered_list,
            feature_collection=dump,
            submission_type=submission_type,
            submission_status=submission_status,
        )

    post_list = SubmissionModel.query.all()
    point_list = []
    for i, post in enumerate(post_list):
        i = Feature(geometry=Point((post.lng, post.lat)))
        i.properties["id"] = post.id
        i.properties["title"] = post.title
        i.properties["status"] = post.status
        i.properties["type"] = post.problem_type
        i.properties["cover_image"] = post.cover_image
        point_list.append(i)

    feature_collection = FeatureCollection(point_list)
    dump = gj_dump(feature_collection, sort_keys=True)

    return render_template(
        "map.html",
        ACCESS_KEY=MAP_KEY,
        lat=INIT_LAT,
        lng=INIT_LNG,
        post_list=post_list,
        feature_collection=dump,
    )


# FELHASZNÁLÓI FIÓK
@app.route("/user_account", methods=["POST", "GET"])
@login_required
def user_account():
    "#"
    if request.method == "POST":
        if "own_submissions" in request.form:
            user_id = int(request.form["user_id"])
            user = UserModel.query.filter_by(id=user_id).first()
            post_list = SubmissionModel.query.filter_by(submitter_email=user.email)
            owner_list = SubmissionModel.query.filter_by(owner_email=user.email)
            return render_template(
                "user_account.html", post_list=post_list, owner_list=owner_list
            )

    return render_template("user_account.html")


# FELHASZNÁLÓ ADATOK MÓDOSÍTÁSA
@app.route("/change_user_data/<user_id>", methods=["POST", "GET"])
@login_required
def change_user_data(user_id):
    "#"
    user = UserModel.query.filter_by(id=user_id).first()

    if request.method == "POST":
        if request.form["new_user_name"] != "":
            new_user_name = request.form["new_user_name"]
            user.user_name = new_user_name
            db.session.commit()
            flash(f"Sikeresen módosítottad a felhasználónevedet!", "success")

        if request.form["new_email"] != "":
            new_email = request.form["new_email"]
            user.email = new_email
            db.session.commit()
            flash(f"Sikeresen módosítottad az email címedet!", "success")

        if request.form["new_phone"] != "":
            new_phone = request.form["new_phone"]
            user.phone = new_phone
            db.session.commit()
            flash(f"Sikeresen módosítottad a telefonszámodat!", "success")

    return render_template("change_user_data.html", user=user)


# FELHASZNÁLÓK ÁTTEKINTÉSE (ADMIN FELÜLET)
@app.route("/user_administration", methods=["POST", "GET"])
@login_required
def user_management():
    "#"

    if not current_user.role == "admin":
        flash("Ide csak admin léphet!", "danger")
        return render_template("index.html")

    if request.method == "POST":
        pass
    user_list = UserModel.query.all()
    return render_template("user_management.html", user_list=user_list)


# FELHASZNÁLÓ KEZELÉSE
@app.route("/user_manage/<id>", methods=["POST", "GET"])
@login_required
def user_manage(id):
    "#"
    if not current_user.role == "admin":
        flash("Ide csak admin léphet!", "danger")
        return render_template("index.html")

    user = UserModel.query.filter_by(id=id).first()

    if request.method == "POST":
        user_role = request.form["role"]
        user.role = user_role
        db.session.commit()
        flash("Sikeres módosítás!", "success")
        return render_template("single_user.html", user=user)

    return render_template("single_user.html", user=user)


# ÜGYEK TÁBLÁZATOS LETÖLTÉSE
@app.route("/download", methods=["GET"])
@login_required
def download_data():
    if current_user.role != "admin" and current_user.role != "coordinator":
        flash("Csak admin vagy kordinátor tölthet le!", "danger")
        return render_template("index.html")

    write_log(BASE_DIR, current_user, "download all data")

    submissions = SubmissionModel.query.all()

    submission_id = [submission.id for submission in submissions]
    title = [submission.title for submission in submissions]
    problem_type = [submission.problem_type for submission in submissions]
    problem_type = [submission.problem_type for submission in submissions]
    description = [submission.description for submission in submissions]
    suggestion = [submission.suggestion for submission in submissions]
    solution = [submission.solution for submission in submissions]
    address = [submission.address for submission in submissions]
    city = [submission.city for submission in submissions]
    county = [submission.county for submission in submissions]
    lat = [submission.lat for submission in submissions]
    lng = [submission.lng for submission in submissions]
    submitter_email = [submission.submitter_email for submission in submissions]
    submitter_phone = [submission.submitter_phone for submission in submissions]
    owner_email = [submission.owner_email for submission in submissions]
    owner_user = [submission.owner_user for submission in submissions]
    created_date = [submission.created_date for submission in submissions]
    status = [submission.status for submission in submissions]
    featured = [submission.featured for submission in submissions]
    status_changed_date = [submission.status_changed_date for submission in submissions]
    status_changed_by = [submission.status_changed_by for submission in submissions]

    excel.init_excel(app)
    extension_type = "csv"
    filename = "RÜM_összes_bejelentés_" + str(get_date()) + "." + extension_type
    data = {
        "Ügyszám": submission_id,
        "Elnevezés": title,
        "Típus": problem_type,
        "Leírás": description,
        "Megoldási javaslat": suggestion,
        "Megoldás": solution,
        "Cím": address,
        "Kiemelt": featured,
        "Város": city,
        "Megye": county,
        "Szélességi fok": lat,
        "Hosszúsági fok": lng,
        "Bejelentő email": submitter_email,
        "Bejelentő telefon": submitter_phone,
        "Szervező email": owner_email,
        "Szervező felhasználó": owner_user,
        "Létrehozva": created_date,
        "Státusz": status,
        "Státusz változás dátuma": status_changed_date,
        "Státuszt változtató felhasználó": status_changed_by,
    }
    return excel.make_response_from_dict(
        data, file_type=extension_type, file_name=filename
    )


# REGISZTRÁCIÓ
@app.route("/register", methods=["POST", "GET"])
def register():
    "#"
    return redirect("https://passziv.mkkp.party/regisztracio", code=302)


# BEJELENTKEZÉS
@app.route("/login")
def site_login():
    "#"
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True, _scheme="https")
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    "#"
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    user_email = token["userinfo"]["email"]
    aud = token["userinfo"]["aud"]
    user_name = token["userinfo"]["name"]
    user = UserModel.query.filter_by(email=user_email).first()

    if aud != AUTH0_CLIENT_ID:
        flash("sikertelen bejelentkezés", "danger")
        return redirect("/")

    if not user:
        user_name = get_random_name() + " " + str(randint(1, 1000))
        reg_user = UserModel(
            email=user_email,
            created_date=get_date(),
            role="registered",
            user_name=user_name,
            active=True,
        )
        db.session.add(reg_user)
        db.session.commit()
        user = UserModel.query.filter_by(email=user_email).first()
        login_user(user)
        user.last_login = get_date()

    if user:
        login_user(user)
        user.last_login = get_date()
        db.session.commit()

    flash("Sikeres bejelentkezés!", "success")
    return redirect("/")


# KIJELENTKEZÉS
@app.route("/logout")
def logout():
    "#"
    logout_user()
    flash("Sikeres kijelentkezés!", "success")
    return redirect("/")


# EASTER EGG
@app.route("/kutyi", methods=["GET"])
def easter_egg():
    "#"
    try:
        import requests

        response = requests.get("https://dog.ceo/api/breeds/image/random")
        resp_json = response.json()
        kutyi_pic = resp_json["message"]
        return render_template("easter_egg.html", kutyi_pic=kutyi_pic)
    except Exception as e:
        pass


# ADATVÉDELMI TÁJÉKOZTATÓ
@app.route("/user_data_info", methods=["GET"])
def user_data_info():
    "#"
    return render_template("user_data_info.html")


# ERROR HANDLER 404
@app.errorhandler(404)
def page_not_found(e):
    "#"
    return render_template("404.html")


# ERROR HANDLER 502
@app.errorhandler(502)
def page_not_found(e):
    "#"
    return render_template("502.html")


# APP RUN
if __name__ == "__main__":
    app.run(host="localhost", port=PORT, debug=DEBUG_MODE)
