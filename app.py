"""
MKKP városfelújítós alkalmazás
"""
#-------------------------------
#---------I M P O R T S---------
#-------------------------------

#BUILTINS
import json
import jwt
import os
import shutil
from random import randint
from pathlib import Path

#THIRD PARTY MODULES
#Mailjet mail provider
from mailjet_rest import Client

#Flask
from flask import Flask
from flask import flash
from flask import redirect 
from flask import render_template
from flask import request
from flask import session
from flask import url_for

#Flask Login
from flask_login import current_user
from flask_login import login_required 
from flask_login import login_user
from flask_login import logout_user

from flask_cors import CORS
from flask_paranoid import Paranoid
from werkzeug.utils import secure_filename

#AUTH0
#from os import environ as env
#from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth

#SQLAlchemy
from sqlalchemy import update
from sqlalchemy import text
from sqlalchemy import MetaData

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
from config import APP_SECRET_KEY
from config import AUT0_DB

##APP
app = Flask(__name__)

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


#BEJELENTKEZÉS
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True))
    
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    access_token = token['access_token']
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
        user = UserModel.query.filter_by(email = user_email).first()
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
def submission():
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
        tag = "before"
        
        result = save_picture(pictures=pictures, 
                              upload_folder=UPLOAD_FOLDER, 
                              tag=tag, 
                              submission_id=str(submission.id)
                             )
                             
        if result == "not allowed extension":
            flash("not allowed extension","danger")
        
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
              "HTMLPart": f"<h4>Gratulálunk!</h4><h5>Sikeres városmódosító bejelentést tettél!</h5>",
              "CustomID": "MKKP városmódosító bejelentés"
            }
          ]
        }

        mailjet.send.create(data=submission_mail)
        flash("Sikeres bejelentés! Küldtünk egy levelet is!",'success')
        return redirect(f'/single_submission/{submission.id}')

    if request.method == 'GET':
        return render_template('submission.html',
                               ACCESS_KEY=MAP_KEY,
                               lat=INIT_LAT,lng=INIT_LNG
                              )


#EGY BEJELENTÉS
@app.route('/single_submission/<id>', methods = ['POST', 'GET'])
def single_submission(id):
    
    submission_id = str(id)
    
    if request.method == 'POST':

        if "change_status" in request.form:
            new_status = request.form["status"]
            changed_by = request.form["current_user"]
            submission = SubmissionModel.query.filter_by(id=submission_id).first()
            submission.status = new_status
            submission.status_changed_date = get_date()
            submission.status_changed_by = changed_by
            db.session.commit()
            flash(f"Sikeresen módosítottad a státuszt '{new_status}' státuszra!","success")
                                    
        if "comment-submit" in request.form:
            comment = CommentModel(commenter=request.form["current_user"],
                                   created_date=get_date(),
                                   body=request.form["comment"],
                                   parent_id = submission_id)
            db.session.add(comment)                       
            db.session.commit()
            flash(f"Sikeresen hozzáadtál egy kommentet!","success")

        if "closing_solution_submit" in request.form:
            closing_solution = request.form["closing_solution"]
            changed_by = request.form["current_user"]
            submission = SubmissionModel.query.filter_by(id=submission_id).first()
            submission.solution = closing_solution
            submission.status = "Befejezve"
            submission.status_changed_date =  get_date()
            submission.status_changed_by = changed_by
            db.session.commit()
            flash(f"Sikeresen hozzáadtad a bejelentés zárószövegét! Az ügy innentől kezdve befejezettnek minősül.", "success")         
            
        if "new_address_submit" in request.form:
            submission = SubmissionModel.query.filter_by(id=submission_id).first()
            new_address = request.form["new_address"]
            city = request.form["city"],
            county = request.form["county"],
            lat = request.form["lat"],
            lng = request.form["lng"],
            
            city = city[0]
            county = county[0]
            lat = lat[0]
            lng = lng[0]
            
            submission.address = new_address
            submission.county = county
            submission.city = city
            submission.lat = lat
            submission.lng = lng
            
            db.session.commit()
            flash(f"Sikeresen módosítottad a címet!", "success")            
                                    
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
            flash(f"""A borítókép cserélési eljárás 
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
    
    page = request.args.get('page', 1, type=int)
    post_list = SubmissionModel.query\
      .order_by(SubmissionModel.created_date.desc())\
      .paginate(page=page, per_page=ROWS_PER_PAGE)

    if request.method == 'POST':
    
        county = request.form["county"]
        problem_type = request.form["type"]
        status = request.form["status"]

        county_dict = {}
        problem_type_dict = {}
        status_dict = {}
        
        if county != "":
            county_dict = {"county":county}
            
        if problem_type != "":
            problem_type_dict = {"problem_type":problem_type}
            
        if status != "":
            status_dict = {"status":status}
        
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


#BEJELENTÉS RENDEZŐ HOZZÁADÁSA                      
@app.route('/assign/<id>', methods = ['POST', 'GET'])
@login_required
def assign(id):

    user_list = UserModel.query.all()
    submission = SubmissionModel.query.filter_by(id=id).first()

    if request.method == 'POST':
        
        submission.owner_email = request.form['email']
        submission.owner_user = request.form['username']
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
              "Subject":  "MKKP rendező lettél!",
              "TextPart": "MKKP rendező lettél!",
              "HTMLPart": f"""<h2>Gratulálunk!</h2><h3>Rendezőként lettél beállítva 
              a Rendkívüli Ügyek Minisztériumának következő bejelentésénél:</h3>
              https://rendkivuliugyek.site/single_submission/{id}
              """,
              "CustomID": "MKKP rendező lettél!"
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
    post_count = SubmissionModel.query.count()
    user_count = UserModel.query.count()
    submitted_count = SubmissionModel.query.filter_by(status="Bejelentve").count()
    wip_count = SubmissionModel.query.filter_by(status="Folyamatban").count()
    completed_count = SubmissionModel.query.filter_by(status="Befejezve").count()
    #upload_stat = os.stat(UPLOAD_FOLDER)
    #upload_size = os.stat(UPLOAD_FOLDER).st_size / 1000
    
    return render_template('statistics.html',
                            post_count=post_count,
                            user_count=user_count,
                            submitted_count = submitted_count,
                            wip_count=wip_count,
                            completed_count=completed_count,
                            #upload_size=upload_size
                          )  
 
 
#TÉRKÉP
@app.route('/full_map', methods = ['POST', 'GET'])
def full_map():

    post_list = SubmissionModel.query.all()
    
    return render_template('map.html',
                           ACCESS_KEY=MAP_KEY,
                           lat=INIT_LAT,
                           lng=INIT_LNG,
                           post_list=post_list
                          )
    
#REGISZTRÁCIÓ
@app.route('/register', methods=['POST', 'GET'])
def register():
    return redirect('https://passziv.mkkp.party/regisztracio', code=302)
    
 
   
#FELHASZNÁLÓI FIÓK
@app.route('/user_account', methods = ['POST', 'GET'])
@login_required
def user_account():

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


#FELHASZNÁLÓK ÁTTEKINTÉSE
@app.route('/user_administration', methods = ['POST', 'GET'])
@login_required
def user_management():
    if request.method == 'POST':
        pass
    user_list = UserModel.query.all()
    return render_template("user_management.html", user_list=user_list)


#FELHASZNÁLÓ KEZELÉSE
@app.route('/user_manage/<id>', methods = ['POST', 'GET'])
@login_required
def user_manage(id):

    user = UserModel.query.filter_by(id=id).first() 

    if request.method == 'POST':
        user_role = request.form['role']
        user.role = user_role
        db.session.commit()
        flash("Sikeres Módosítás",'success')
        return render_template("single_user.html",user=user)
    
    return render_template("single_user.html",user=user)

#ADATVÉDELMI TÁJÉKOZTATÓ
@app.route('/user_data_info', methods = ['GET'])
def user_data_info():
    return render_template("user_data_info.html")

#KIJELENTKEZÉS
@app.route('/logout')
def logout():
    logout_user()
    flash("Sikeres kijelentkezés!",'success')
    return redirect('/')
    

@app.errorhandler(404) 
def page_not_found(e): 
    return render_template('404.html')

#APP RUN
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
