from random import randint
from flask import flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user
from app.auth import setup_oauth
from app.env import AUTH0_CLIENT_ID
from app.models import db, UserModel
from app.utils import get_date, get_random_name


def register():
    return redirect("https://passziv.mkkp.party/regisztracio", code=302)


def site_login(oauth):
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True, _scheme="https")
    )


def callback(oauth):
    token = oauth.auth0.authorize_access_token()
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
        )  # type: ignore
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
def logout():
    logout_user()
    flash("Sikeres kijelentkezés!", "success")
    return redirect("/")


def setup(app):
    oauth = setup_oauth(app)

    login = LoginManager()
    login.init_app(app)
    login.login_view = "login"  # type: ignore
    login.user_loader(lambda id: UserModel.query.get(int(id)))

    app.add_url_rule("/register", "register", register, methods=["POST", "GET"])
    app.add_url_rule("/login", "login", lambda: site_login(oauth))
    app.add_url_rule(
        "/callback", "callback", lambda: callback(oauth), methods=["GET", "POST"]
    )
    app.add_url_rule("/logout", "logout", logout)
