"""
MKKP városfelújítós alkalmazás
"""
#-------------------------------
#---------I M P O R T S---------
#-------------------------------

#BUILTINS
import os
import shutil
from random import randint

#THIRD PARTY MODULES
#Mailjet mail provider
from mailjet_rest import Client
from geojson import Feature
from geojson import Point
from geojson import FeatureCollection
from geojson import dumps as gj_dump
import flask_excel as excel

#Flask
from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

#Flask-Migrate
from flask_migrate import Migrate

#Flask Login
#from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from flask_cors import CORS
from flask_paranoid import Paranoid

#AUTH0
from authlib.integrations.flask_client import OAuth

#DATABASE MODELS
from models import UserModel
from models import db
from models import login
from models import SubmissionModel
from models import ImageBeforeModel
from models import ImageAfterModel
from models import CommentModel

#UTILS
from utils import valid_email
from utils import get_date
from utils import save_picture
from utils import get_random_name

#-------------------------------
#---------C O N F I G-----------
#-------------------------------

##MAP
from config import MAP_KEY
from config import INIT_LAT
from config import INIT_LNG
##MAIL
from config import M_KEY
from config import M_SECRET
from config import FROM_MAIL
##MISC
from config import DB_NAME
from config import BASE_DIR
from config import UPLOAD_FOLDER
from config import APP_SECRET_KEY
from config import ROWS_PER_PAGE

#AUTH0
from config import AUTH0_CLIENT_ID
from config import AUTH0_CLIENT_SECRET
from config import AUTH0_DOMAIN

##APP
app = Flask(__name__)
migrate = Migrate(app, db)

##OAUTH
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id = AUTH0_CLIENT_ID,
    client_secret= AUTH0_CLIENT_SECRET,
    client_kwargs = {
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
)

##DATABASE
db.init_app(app)

#APP CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = APP_SECRET_KEY

#CORS
#https://flask-cors.readthedocs.io/en/latest/
CORS(app, resources={r'/*': {'origins': '*'}})

#Paranoid
#https://pypi.org/project/Flask-Paranoid/
paranoid = Paranoid(app)
paranoid.redirect_view = '/'

#FLASK-LOGIN Config
login.init_app(app)
login.login_view = 'login'

#MAIL
mailjet = Client(auth=(M_KEY, M_SECRET), version='v3.1')


#-------------------------------
#---------V I E W S-------------
#-------------------------------

@app.before_first_request
def create_all():
    """
    If no app.db is present, it creates app.db
    based on schema that is defined in models.py
    """
    db.create_all()


#TÉRKÉP
@app.route('/full_map', methods = ['POST', 'GET'])
def full_map():
    "#"
    
    if request.method == 'POST':
    
        submission_type = request.form["type"],
        
        filtered_list = SubmissionModel.query.filter_by(problem_type=submission_type[0]).all()
        
        if submission_type[0] == "Összes":
            filtered_list = SubmissionModel.query.all()
            
        if submission_type[0] == "":
            filtered_list = SubmissionModel.query.all()            
        
        point_list=[]
        for i, post in enumerate(filtered_list):
            i = Feature(geometry=Point((post.lng, post.lat)))
            i.properties['id'] = post.id
            i.properties['title'] = post.title
            i.properties['status'] = post.status
            i.properties['type'] = post.problem_type
            i.properties['cover_image'] = post.cover_image
            point_list.append(i)

        feature_collection = FeatureCollection(point_list)
        dump = gj_dump(feature_collection, sort_keys=True)

        return render_template('map.html',
                           ACCESS_KEY=MAP_KEY,
                           lat=INIT_LAT,
                           lng=INIT_LNG,
                           post_list=filtered_list,
                           feature_collection = dump,
                           submission_type = submission_type[0]
                           )
    
    post_list = SubmissionModel.query.all()
    point_list=[]
    for i, post in enumerate(post_list):
        i = Feature(geometry=Point((post.lng, post.lat)))
        i.properties['id'] = post.id
        i.properties['title'] = post.title
        i.properties['status'] = post.status
        i.properties['type'] = post.problem_type
        i.properties['cover_image'] = post.cover_image
        point_list.append(i)

    feature_collection = FeatureCollection(point_list)
    dump = gj_dump(feature_collection, sort_keys=True)

    return render_template('map.html',
                           ACCESS_KEY=MAP_KEY,
                           lat=INIT_LAT,
                           lng=INIT_LNG,
                           post_list=post_list,
                           feature_collection = dump
                          )

#BEJELENTKEZÉS
@app.route("/login")
def site_login():
    "#"
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True))


@app.route("/callback", methods=["GET", "POST"])
def callback():
    "#"
    token = oauth.auth0.authorize_access_token()
    #access_token = token['access_token']
    session["user"] = token
    user_email = token['userinfo']['email']
    aud = token['userinfo']['aud']
    user_name = token['userinfo']['name']
    user = UserModel.query.filter_by(email = user_email).first()

    if aud != AUTH0_CLIENT_ID:
        flash("sikertelen bejelentkezés","danger")
        return redirect("/")

    if not user:
        user_name = get_random_name() + " " + str(randint(1,1000))
        reg_user = UserModel(email=user_email,
                             created_date=get_date(),
                             role="registered",
                             user_name = user_name,
                             active=True)
        db.session.add(reg_user)
        db.session.commit()
        user = UserModel.query.filter_by(email=user_email).first()
        login_user(user)
        user.last_login = get_date()

    if user:
        login_user(user)
        user.last_login = get_date()
        db.session.commit()

    flash("Sikeres bejelentkezés!","success")
    return redirect("/")


#INDEX
@app.route('/', methods = ['GET'])
def index():
    """
    Kezdőoldal
    Bejelentkezés nem szükséges
    """
    return render_template('index.html')


#BEJELENTÉS
@app.route('/submission', methods = ['POST', 'GET'])
def add_submission():
    """
    Bejelentkezés nem szükséges
    """
    if request.method == 'POST':
        #email validaiton
        if not valid_email(request.form["email"]):
            flash('A Kutya mindenit de fura ez az email cím!','danger')
            return render_template('submission.html',
                                   ACCESS_KEY=MAP_KEY,
                                   lat=INIT_LAT,lng=INIT_LNG
                                  )

        #validate text for embedded links
        if "http" in request.form["title"]:
            flash('A szöveg nem tartalmazhat linket!','danger')
            return render_template('submission.html',
                                   ACCESS_KEY=MAP_KEY,
                                   lat=INIT_LAT,lng=INIT_LNG
                                  )

        submission = SubmissionModel(title=request.form["title"],
                     problem_type=request.form["type"],
		     description=request.form["description"],
		     suggestion=request.form["suggestion"],
		     city=request.form["city"],
		     county=request.form["county"],
		     address=request.form["address"],
		     lat=request.form["lat"],
		     lng=request.form["lng"],
		     submitter_email=request.form["email"],
		     owner_email="",
		     status="Bejelentve",
		     status_changed_date=get_date(),
		     status_changed_by = request.form["email"],
		     created_date=get_date()
		     )
		     
        db.session.add(submission)
        db.session.commit()
		     
        #SAVE PICTURES
        pictures = request.files.getlist('files')
        additional_pictures = request.files.getlist('additional_files')
        
        if additional_pictures[0].filename != "":
            pictures = pictures + additional_pictures
            
        for p in pictures:
            print(type(p))
            
        tag = "before"
        
        result = save_picture(pictures=pictures,
                              upload_folder=UPLOAD_FOLDER,
                              tag=tag,
                              submission_id=str(submission.id)
                             )
                             
        if result == "not allowed extension":
            flash("Nem megengedett file kiterjesztés.","danger")
            return render_template('submission.html',
                               ACCESS_KEY=MAP_KEY,
                               lat=INIT_LAT,lng=INIT_LNG
                              )

        submission_mail = {'Messages': [
            {
            "From": {
            "Email": f"{FROM_MAIL}",
            "Name":  "MKKP"
              },
              "To": [
            {
              "Email": f"{request.form['email']}",
              "Name":  "MKKP"
            }
              ],
              "Subject":  "Sikeres városmódosító bejelentés!",
              "TextPart": "Sikeres városmódosító bejelentés!",
              "HTMLPart": f"""<h3>Szia!</h3>
                              <p>Köszi, hogy jelezted nekünk az alábbi problémát: {submission.title}<br>
                              4000 mérnökünk és 3600 menyétünk elkezdett dolgozni rajta.<br>Hamarosan megoldjuk vagy nem.
                              </p>
                              <p>Keresünk majd, amint kitaláltuk, hogy mit csináljunk a dologgal.<br>
                              Addig is itt tudod nyomon követni, hogyan állunk vele: https://rendkivuliugyek.site/single_submission/{submission.id}</p>
		              <p><b>Rendkívüli Ügyek Minisztériuma</b></p>                            
                              """,
              "CustomID": "MKKP városmódosító bejelentés"
            }
          ]
        }

        result = mailjet.send.create(data=submission_mail)
        flash("Sikeres bejelentés! Küldtünk egy levelet is!",'success')
        return redirect(f'/single_submission/{submission.id}')
        
    if request.method == 'GET':
        return render_template('submission.html',
                               ACCESS_KEY=MAP_KEY,
                               lat=INIT_LAT,lng=INIT_LNG
                              )

#ÜGY ADATAINAK MÓDOSÍTÁSA
@app.route('/change_submission_data/<submission_id>', methods = ['POST', 'GET'])
@login_required
def change_submission_data(submission_id):
    """
    Pylint R0915: Too many statements (53/50) (too-many-statements)
    #TODO: szétszedni több függvényre
    """
    submission = SubmissionModel.query.filter_by(id=submission_id).first()

    if request.method == 'POST':

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

        if request.form["status"] != submission.status:
            new_status = request.form["status"]
            changed_by = request.form["current_user"]

            submission.status = new_status
            submission.status_changed_date = get_date()
            submission.status_changed_by = changed_by
            db.session.commit()
            
            if submission.owner_email != "":
                status_change_mail = {'Messages': [
		    {
		    "From": {
		    "Email": f"{FROM_MAIL}",
		    "Name":  "MKKP"
		      },
		      "To": [
		    {
		      "Email": f"{submission.owner_email}",
		      "Name":  "MKKP"
		    }
		      ],
		      "Subject":  f"Státusz változás: {submission.title}",
		      "TextPart": "Városfelújítós ügy státusz változás",
		      "HTMLPart": f"""<h3>Kedves {submission.owner_user}!</h3>
		                      <p>A {submission.title} ügy státusza megváltozott a következőre: {submission.status}
		                      </p>
		                      <p>Az ügy adatlapját itt találod:</p>
		                      <p>https://rendkivuliugyek.site/single_submission/{submission.id}</p>
			              <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
		                      """,
		      "CustomID": "MKKP városmódosító bejelentés"
		    }
		  ]
		}

                mailjet.send.create(data=status_change_mail)
                flash(f"Sikeresen módosítottad az ügy státuszát erre: {new_status}. A szervezőnek ment levél.", "success")          
            
            else:
                flash(f"Sikeresen módosítottad az ügy státuszát erre: {new_status}", "success")
                

            if new_status == "Befejezve":

                solution_mail_to_submitter = {'Messages': [
		    {
		    "From": {
		    "Email": f"{FROM_MAIL}",
		    "Name":  "MKKP"
		      },
		      "To": [
		    {
		      "Email": f"{submission.submitter_email}",
		      "Name":  "MKKP"
		    }
		      ],
		      "Subject":  f"Befejezett ügy: {submission.title}",
		      "TextPart": "Befejezett ügy",
		      "HTMLPart": f"""<h3>Szia!</h3>
			              <p>Jó hír: sikerült megoldanunk a problémát, amit bejelentettél: {submission.title}</p>
			              <p>Itt tudod megnézni, hogy mire jutottunk: https://rendkivuliugyek.site/single_submission/{submission.id}</p>
				      <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
			              """,
		      "CustomID": "MKKP városmódosító bejelentés"
		      }
		    ]
		   }

                mailjet.send.create(data=solution_mail_to_submitter) 

        if request.form["closing_solution"] != "":
            closing_solution = request.form["closing_solution"]
            changed_by = request.form["current_user"]

            submission.solution = closing_solution
            submission.status = "Befejezve"
            submission.status_changed_date =  get_date()
            submission.status_changed_by = changed_by
            db.session.commit()

            flash("""Sikeresen hozzáadtad a bejelentés zárószövegét!
            Az ügy innentől kezdve befejezettnek minősül.""", 
            "success")

        if request.form["new_address"] != "":
            new_address = request.form["new_address"]
            city = request.form["city"]
            county = request.form["county"]
            lat = request.form["lat"]
            lng = request.form["lng"]

            submission.address = new_address
            submission.county = county
            submission.city = city
            submission.lat = lat
            submission.lng = lng

            db.session.commit()
            flash("Sikeresen módosítottad a címet!", "success")

        return redirect(f'/single_submission/{submission_id}')

    return render_template ("change_submission_data.html",
                            submission=submission,
                            ACCESS_KEY=MAP_KEY
                            )

#EGY BEJELENTÉS
@app.route('/single_submission/<id>', methods = ['POST', 'GET'])
def single_submission(id):
    "#"
    submission_id = str(id)

    if request.method == 'POST':

        if "comment-submit" in request.form:
            comment = CommentModel(commenter=request.form["current_user"],
                                   created_date=get_date(),
                                   body=request.form["comment"],
                                   parent_id = submission_id)
            db.session.add(comment)
            db.session.commit()
            flash(f"Sikeresen hozzáadtál egy kommentet!","success")

        if "comment-edit" in request.form:
            body_change = request.form["comment"]
            comment_id = request.form["comment_id"]
            comment = CommentModel.query.filter_by(id=comment_id).first()
            comment.body = body_change
            comment.created_date = get_date()
            db.session.commit()
            flash(f"Komment szerkesztve","success")

        if "change_tumbnail" in request.form:
            new_thumbnail = request.form["new_thumb"]
            submission = SubmissionModel.query.filter_by(id=submission_id).first()
            submission.cover_image = new_thumbnail
            db.session.commit()
            flash("""A borítókép cserélési eljárás
                      előkészítését elindítottuk.
                      Ügyintézőnk egy héten belül jelentkezik.
                      Kérjük, addig ne mozduljon a készüléke mellől!
                      ""","success")

        if "upload_before_images" in request.form:
            tag = "before"
            pictures = request.files.getlist('files')
            save_picture(pictures, UPLOAD_FOLDER, tag, submission_id)

        if "upload_after_images" in request.form:
            tag = "after"
            pictures = request.files.getlist('files')
            save_picture(pictures, UPLOAD_FOLDER, tag, submission_id)

    submission = SubmissionModel.query.filter_by(id=submission_id)
    before_img_list = ImageBeforeModel.query.filter_by(parent_id=submission_id)
    after_img_list = ImageAfterModel.query.filter_by(parent_id=submission_id)
    comment_list = CommentModel.query.filter_by(parent_id=submission_id)

    return render_template ("single_submission.html",
                            submission=submission,
                            before_img_list=before_img_list,
                            after_img_list=after_img_list,
                            comment_list = comment_list,
                            ACCESS_KEY=MAP_KEY
                           )


#ÖSSZES BEJELENTÉS
@app.route('/all_submission/', methods = ['POST', 'GET'])
def all_submission():
    "#"
    page = request.args.get('page', 1, type=int)
    post_list = SubmissionModel.query\
      .order_by(SubmissionModel.created_date.desc())\
      .paginate(page=page, per_page=ROWS_PER_PAGE)

    if request.method == 'POST':
    
        county = request.form["county"]
        problem_type = request.form["type"]
        status = request.form["status"]
        search_text = request.form["full_text_search"]
        #result = SubmissionModel.query.filter(SubmissionModel.description.like(f"%{search_text}%")).all()
        #result = SubmissionModel.query.filter_by(description = f"%{search_text}%").all()

        county_dict = {}
        problem_type_dict = {}
        status_dict = {}
        text_dict = {}

        if county != "":
            county_dict = {"county":county}

        if problem_type != "":
            problem_type_dict = {"problem_type":problem_type}

        if status != "":
            status_dict = {"status":status}
            
        if search_text != "":
            search_text = search_text.lower()
            filtered_list = SubmissionModel.query.filter(SubmissionModel.description.ilike(f"%{search_text}%"))\
            .order_by(SubmissionModel.created_date.desc())\
            .paginate(page=page, per_page=ROWS_PER_PAGE)
            return render_template ("all_submission.html",
                                     post_list=filtered_list
                                   )

        #merge dicts
        query_dict = county_dict | problem_type_dict | status_dict


        filtered_list = SubmissionModel.query.filter_by(**query_dict)\
        .order_by(SubmissionModel.created_date.desc())\
        .paginate(page=page, per_page=ROWS_PER_PAGE)
 
        return render_template ("all_submission.html",
                                 post_list=filtered_list,
                               )

    return render_template ("all_submission.html",
                            post_list=post_list,
                           )


#BEJELENTÉS SZERVEZŐ HOZZÁADÁSA
@app.route('/assign/<id>', methods = ['POST', 'GET'])
@login_required
def assign(id):
    "#"
    user_list = UserModel.query.all()
    submission = SubmissionModel.query.filter_by(id=id).first()

    if request.method == 'POST':

        submission.owner_email = request.form['email']
        submission.owner_user = request.form['username']
        submission.status = "Folyamatban"
        db.session.commit()

        organiser_mail = {'Messages': [
            {
            "From": {
            "Email": f"{FROM_MAIL}",
            "Name":  "MKKP"
              },
              "To": [
            {
              "Email": f"{request.form['email']}",
              "Name":  "MKKP"
            }
              ],
              "Subject":  "MKKP szervező lettél!",
              "TextPart": "MKKP szervező lettél!",
              "HTMLPart": f"""<h2>Gratulálunk!</h2>
              <h3>Szervezőként lettél beállítva
               a Rendkívüli Ügyek Minisztériumának következő bejelentésénél:
              </h3>
              <br>
              <p>{{submission.title}}</p>
              <p>https://rendkivuliugyek.site/single_submission/{id}</p>
              <p>Üdvözlettel:<br>
              Rendkívüli Ügyek Minisztériuma
              </p>             
              """,
              "CustomID": "MKKP szervező lettél!"
            }
          ]
        }

        mailjet.send.create(data=organiser_mail)

        flash("Szervező sikeresen hozzárendelve!","success")
        return redirect(f'/single_submission/{id}')

    return render_template('assign.html', user_list=user_list, submission=submission)


#KOMMENT TÖRLÉS
@app.route('/delete_comment/<id>')
@login_required
def delete_comment(id):
    "#"
    comment = CommentModel.query.filter_by(id=id)
    submission_id = comment.first().parent_id
    comment.delete()
    db.session.commit()
    flash("A kommentet sikeresen töröltük!","success")
    return redirect(f'/single_submission/{submission_id}')


#KÉP TÖRLÉS
@app.route('/delete_picture/<status_type>/<id>')
@login_required
def delete_picture(status_type, id):
    "#"
    if status_type == "before":
        picture = ImageBeforeModel.query.filter_by(id=id)
        submission_id = picture.first().parent_id
        picture_total = ImageBeforeModel.query.filter_by(parent_id=submission_id).count()
        if picture_total == 1:
            flash(f"Egy képnek maradnia kell","danger")
            return redirect(f'/single_submission/{submission_id}')

    if status_type == "after":
        picture = ImageAfterModel.query.filter_by(id=id)
        submission_id = picture.first().parent_id
        picture_total = ImageAfterModel.query.filter_by(parent_id=submission_id).count()
        if picture_total == 1:
            flash(f"Egy képnek maradnia kell","danger")
            return redirect(f'/single_submission/{submission_id}')

    submission_id = picture.first().parent_id
    picture.delete()
    db.session.commit()
    flash("A képet sikeresen töröltük!","success")
    return redirect(f'/single_submission/{submission_id}')


#BEJELENTÉS TÖRLÉS
@app.route('/delete_submission/<id>')
@login_required
def delete_submission(id):
    "#"
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
    flash("A bejegyzést sikeresen töröltük!","success")
    return redirect('/')


#STATISZTIKA
@app.route('/statistics', methods = ['POST', 'GET'])
def statistics():
    "#"
    post_count = SubmissionModel.query.count()
    user_count = UserModel.query.count()
    submitted_count = SubmissionModel.query.filter_by(status="Bejelentve").count()
    wip_count = SubmissionModel.query.filter_by(status="Folyamatban").count()
    progress_count = SubmissionModel.query.filter_by(status="Készül").count()
    completed_count = SubmissionModel.query.filter_by(status="Befejezve").count()
    
    from sqlalchemy import func
    grouped = SubmissionModel.query.group_by('county').all()
    for i in grouped:
        print(i.county)
        print(i)
    print(grouped)
    
    #upload_stat = os.stat(UPLOAD_FOLDER)
    #upload_size = os.stat(UPLOAD_FOLDER).st_size / 1000
    
    return render_template('statistics.html',
                            post_count=post_count,
                            user_count=user_count,
                            submitted_count = submitted_count,
                            wip_count=wip_count,
                            progress_count=progress_count,
                            completed_count=completed_count,
                            #upload_size=upload_size
                          )

#REGISZTRÁCIÓ
@app.route('/register', methods=['POST', 'GET'])
def register():
    "#"
    return redirect('https://passziv.mkkp.party/regisztracio', code=302)

#FELHASZNÁLÓI FIÓK
@app.route('/user_account', methods = ['POST', 'GET'])
@login_required
def user_account():
    "#"
    if request.method == 'POST':

        if "new_user_name" in request.form:
            user_id = int(request.form["user_id"])
            new_user_name = request.form["new_user_name"]
            user = UserModel.query.filter_by(id=user_id).first()
            user.user_name = new_user_name
            db.session.commit()
            flash("Mostantól így hívunk.","success")

        if "own_submissions" in request.form:

            user_id = int(request.form["user_id"])
            user = UserModel.query.filter_by(id=user_id).first()
            post_list = SubmissionModel.query.filter_by(submitter_email = user.email)
            owner_list = SubmissionModel.query.filter_by(owner_email = user.email)
            return render_template("user_account.html",
                               post_list=post_list,
                               owner_list=owner_list)

    return render_template("user_account.html")


#FELHASZNÁLÓ ADATOK MÓDOSÍTÁSA
@app.route('/change_user_data/<user_id>', methods = ['POST', 'GET'])
@login_required
def change_user_data(user_id):
    "#"
    user = UserModel.query.filter_by(id=user_id).first()

    if request.method == 'POST':

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

    return render_template ("change_user_data.html",
    user = user)

#FELHASZNÁLÓK ÁTTEKINTÉSE (ADMIN FELÜLET)
@app.route('/user_administration', methods = ['POST', 'GET'])
@login_required
def user_management():
    "#"
    if request.method == 'POST':
        pass
    user_list = UserModel.query.all()
    return render_template("user_management.html", user_list=user_list)


#FELHASZNÁLÓ KEZELÉSE
@app.route('/user_manage/<id>', methods = ['POST', 'GET'])
@login_required
def user_manage(id):
    "#"
    user = UserModel.query.filter_by(id=id).first()

    if request.method == 'POST':
        user_role = request.form['role']
        user.role = user_role
        db.session.commit()
        flash("Sikeres Módosítás",'success')
        return render_template("single_user.html",user=user)

    return render_template("single_user.html",user=user)

#ÜGYEK TÁBLÁZATOS LETÖLTÉSE
@login_required
@app.route('/download', methods=['GET'])
def download_data():
    submissions = SubmissionModel.query.all()
    
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
    owner_email = [submission.owner_email for submission in submissions]
    owner_user = [submission.owner_user for submission in submissions]
    created_date = [submission.created_date for submission in submissions]
    status = [submission.status for submission in submissions]
    status_changed_date = [submission.status_changed_date for submission in submissions]
    status_changed_by = [submission.status_changed_by for submission in submissions]
    
    excel.init_excel(app)
    extension_type = "csv"
    filename = "RÜM_összes_bejelentés_" + str(get_date()) + "." + extension_type
    data = {'Elnevezés': title,
    	    'Típus': problem_type,
    	    'Leírás': description,
    	    'Megoldási javaslat': suggestion,
    	    'Megoldás': solution,
    	    'Cím': address,
    	    'Város': city,
    	    'Megye': county,
    	    'Szélességi fok': lat,
    	    'Hosszúsági fok': lng,
    	    'Bejelentő email': submitter_email,
    	    'Szervező email': owner_email,
    	    'Szervező felhasználó': owner_user,
    	    'Létrehozva': created_date,
    	    'Státusz': status,
    	    'Státusz változás dátuma': status_changed_date,
    	    'Státuszt változtató felhasználó': status_changed_by
    }
    return excel.make_response_from_dict(data, 
                                         file_type=extension_type, 
                                         file_name=filename
                                        )

#ADATVÉDELMI TÁJÉKOZTATÓ
@app.route('/user_data_info', methods = ['GET'])
def user_data_info():
    "#"
    return render_template("user_data_info.html")

#KIJELENTKEZÉS
@app.route('/logout')
def logout():
    "#"
    logout_user()
    flash("Sikeres kijelentkezés!",'success')
    return redirect('/')

@app.errorhandler(404)
def page_not_found():
    "#"
    return render_template('404.html')
    
@app.errorhandler(502)
def page_not_found():
    "#"
    return render_template('404.html')

#APP RUN
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
