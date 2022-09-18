"""
MKKP városfelújítós alkalmazás
"""
#-------------------------------
#---------I M P O R T S---------
#-------------------------------

#BUILTINS
import os
import shutil
from random import random
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

from flask_login import current_user
from flask_login import login_required 
from flask_login import login_user
from flask_login import logout_user

from flask_cors import CORS
from flask_paranoid import Paranoid
from werkzeug.utils import secure_filename

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

##APP
app = Flask(__name__)

##DATABASE
db.init_app(app)

#CORS
#https://flask-cors.readthedocs.io/en/latest/
CORS(app, resources={r'/*': {'origins': '*'}})

#Paranoid 
#https://pypi.org/project/Flask-Paranoid/
paranoid = Paranoid(app)
paranoid.redirect_view = '/'

#APP CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = APP_SECRET_KEY

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


 
 
#CONTEXT PROCESSOR
@app.context_processor
def utility_processor():
    def hello():
        return "hello"
    
    return dict(hello=hello)


#STATISZTIKA
@app.route('/statistics', methods = ['POST', 'GET'])
def statistics():
    post_count = SubmissionModel.query.count()
    user_count = UserModel.query.count()
    submitted_count = SubmissionModel.query.filter_by(status="Bejelentve").count()
    wip_count = SubmissionModel.query.filter_by(status="Folyamatban").count()
    completed_count = SubmissionModel.query.filter_by(status="Befejezve").count()
    return render_template('statistics.html',
                            post_count=post_count,
                            user_count=user_count,
                            submitted_count = submitted_count,
                            wip_count=wip_count,
                            completed_count=completed_count
                          )  
    

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
        if "http" in request.form["title"]\
         or "http" in request.form["description"]\
         or "http" in request.form["suggestion"]:
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
		     #cover_image="",
		     status="Bejelentve",
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
              "Subject":  "Sikeres várofmódosító bejelentés!",
              "TextPart": "Sikeres várofmódosító bejelentés!",
              "HTMLPart": f"<h4>Gratulálunk!</h4><h5>Sikeres városmódosító bejelentést tettél!</h5>",
              "CustomID": "MKKP városmódosító bejelentés"
            }
          ]
        }

        
        mailjet.send.create(data=submission_mail)
        flash("Sikeres bejelentés! Küldtünk egy levelet is!",'success')
        return render_template('index.html')

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
                                    
        if "comment-edit" in request.form:
            body_change = request.form["comment"]
            comment_id = request.form["comment_id"]
            comment = CommentModel.query.filter_by(id=comment_id).first()
            comment.body = body_change
            comment.created_date = get_date()
            db.session.commit()
            flash(f"Komment szerkesztve","success")

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
    img_list = ImageBeforeModel.query.all()

    if request.method == 'POST':
    
        county = request.form["county"]
        
        if county == "Válassz a megyék közül!":
            img_list = ImageBeforeModel.query.all()
            post_list = SubmissionModel.query\
            .order_by(SubmissionModel.created_date.desc())\
            .paginate(page=page, per_page=ROWS_PER_PAGE)
        else:              
            post_list = SubmissionModel.query\
            .filter_by(county=county)\
            .order_by(SubmissionModel.created_date.desc())\
            .paginate(page=page, per_page=ROWS_PER_PAGE)            
        
        return render_template ("all_submission.html", 
                                 post_list=post_list, 
                                 img_list=img_list
                               )

    return render_template ("all_submission.html", 
                            post_list=post_list, 
                            img_list=img_list
                           ) 


#BEJELENTÉS ÖRÖKBEFOGADÁS                      
@app.route('/adopt/<id>', methods = ['POST', 'GET'])
@login_required
def adopt(id):

    if request.method == 'POST':
        email = request.form["email"]
        phone = request.form["phone"]
        user = UserModel.query.filter_by(email=email).first()
        user.phone = phone
        try:
            db.session.commit()
        except Exception as err:
            flash("Ez a telefonszám már használatban van!","danger")
            return redirect(f'/adopt/{id}')
        
        submission = SubmissionModel.query.filter_by(id=id).first()
        submission.owner_email = email
        submission.owner_user = user.username
        db.session.commit()
        
        adoption_mail = {'Messages': [
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
              "Subject":  "Sikeres örökbefogadás!",
              "TextPart": "Sikeres örökbefogadás!",
              "HTMLPart": f"""<h3>Gratulálunk!</h3>
                              <hr>
                              <h5>Sikeresen örökbefogadtad az ügyet!</h5>
                              <p>https://rendkivuliugyek.site/single_submission/{id}</p>
                           """,
              "CustomID": "MKKP Sikeres örökbefogadás!"
            }
          ]
        }

        mailjet.send.create(data=adoption_mail)         

        flash("Sikeresen örökbefogadva!","success")
        return redirect(f'/single_submission/{id}')

    return render_template('adopt.html')   
    

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




#FELHASZNÁLÓI FIÓK
@app.route('/user_account', methods = ['POST', 'GET'])
@login_required
def user_account():
    if request.method == 'POST':
        post_list = SubmissionModel.query.all()
        return render_template("user_account.html",
                               post_list=post_list
                              )
    return render_template("user_account.html")


#BEJELENTKEZÉS
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash("Már be vagy jelentkezve",'info')
        return redirect('/')

    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()

        if user is not None \
           and user.check_password(request.form['password'])\
           and user.verified == True:
            login_user(user)
            user.last_login = get_date()
            db.session.commit()            
            flash("Sikeres bejelentkezés!",'success')
            return redirect('/')
        else:
            flash("Sikertelen bejelentkezés!",'danger')
            render_template('login.html')

    return render_template('login.html')
 
    
#KIJELENTKEZÉS
@app.route('/logout')
def logout():
    logout_user()
    flash("Sikeres kijelentkezés!",'success')
    return redirect('/')


#REGISZTRÁCIÓ
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        #if authenticated do not show register again
        flash("Már regisztráltál.",'info')
        return redirect('/')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        if UserModel.query.filter_by(email=email).first():
            flash('Ez az email már használatban van.','warning')
            return render_template('register.html')
            
        if UserModel.query.filter_by(username=username).first():
            flash('Ez a felhasználónév már használatban van.','warning')
            return render_template('register.html')
            
        v_code = str(random())[2:]
        user = UserModel(email=email, 
                         username=username,
                         verified=False,
                         verification_code=v_code,
                         created_date=get_date()
                         )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        registration_email = {
	  'Messages': [
	    {
	      "From": {
		"Email": f"{FROM_MAIL}",
		"Name":  "Teszt Regisztráció"
	      },
	      "To": [
		{
		  "Email": f"{email}",
		  "Name":  f"{username}"
		}
	      ],
	      "Subject":  "Teszt regisztráció",
	      "TextPart": "Regisztrációs email",
	      "HTMLPart": f"<h3>{v_code}</h3>",
	      "CustomID": "Regisztráció"
	    }
	  ]
	}

        result = mailjet.send.create(data=registration_email)
        
        return redirect('/confirm_registration')
        
    return render_template('register.html')


#REGISZTRÁCIÓ MEGERŐSÍTÉSE
@app.route('/confirm_registration', methods=['POST', 'GET'])
def confirm_registration():
    if current_user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        email = request.form['email']
        verification_code = request.form['verification_code']
        user = UserModel.query.filter_by(email=email).first()
        
        if verification_code == user.verification_code:
            user.verified = True
            db.session.commit()
            
            sql = text("SELECT * from user")
            result = db.session.execute(sql).fetchall()      
            
            flash("Sikeres regisztráció!",'success')
            return redirect('/login')
            
        else:
            flash("Sikertelen regisztráció!",'danger')
            return redirect('/confirm_registration')

    return render_template('confirm_registration.html')


#ÚJ JELSZÓ
@app.route('/reset_password', methods = ['POST', 'GET'])
def reset_password():
    if request.method == 'POST':
    
        email = request.form['email']
        password = request.form['password']
        
        user = UserModel.query.filter_by(email=email).first()
        
        v_code = str(random())[2:]
        user_name = user.username
        
        registration_email = {
	  'Messages': [
	    {
	      "From": {
		"Email": f"{FROM_MAIL}",
		"Name":  "Jelszó vissazállítása"
	      },
	      "To": [
		{
		  "Email": f"{email}",
		  "Name":  f"{user_name}"
		}
	      ],
	      "Subject":  "Jelszó vissazállítása",
	      "TextPart": "Jelszó vissazállítása",
	      "HTMLPart": f"<h3>{v_code}</h3>",
	      "CustomID": "Jelszó vissazállítása"
	    }
	  ]
	}

        result = mailjet.send.create(data=registration_email)
        
        user.verification_code = v_code
        user.verified = False
        user.set_password(password)
        db.session.commit()        
        
        return redirect('/confirm_registration')
    return render_template('reset_password.html')


#FELHASZNÁLÓ TÖRLÉSE
@app.route('/delete_account', methods = ['POST', 'GET'])
@login_required
def delete_account():
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email=email).first()
        db.session.delete(user)
        db.session.commit()
        flash("Sikeres kijelentkezés",'success')
        return redirect('/logout')
        
    return render_template('delete_account.html')
    
@app.errorhandler(404) 
def page_not_found(e): 
    return render_template('404.html')

#APP RUN
if __name__ == '__main__':
    app.run(debug=True)
