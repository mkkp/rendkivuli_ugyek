from flask import flash, redirect
from flask_login import LoginManager, login_user, logout_user
from app.env import REDIRECT_REGISTER, REDIRECT_LOGIN, REDIRECT_LOGOUT, KC_SERVER_URL
from app.models import db, UserModel
from app.utils import get_date, get_random_name


# REGISZTRÁCIÓ
def register():
    return redirect(
        f"{KC_SERVER_URL}/realms/passivist/protocol/openid-connect/registrations?client_id=rendkivuliugyek&scope=openid email&response_type=code&redirect_uri={REDIRECT_REGISTER}",
        code=302,
    )


# BEJELENTKEZÉS
def site_login():
    return redirect(
        f"{KC_SERVER_URL}/realms/passivist/protocol/openid-connect/auth?client_id=rendkivuliugyek&scope=openid email&response_type=code&redirect_uri={REDIRECT_LOGIN}"
    )


# KIJELENTKEZÉS
def logout():
    logout_user()
    flash("Sikeres kijelentkezés!", "success")
    return redirect(
        f"{KC_SERVER_URL}/realms/passivist/protocol/openid-connect/logout?client_id=rendkivuliugyek&post_logout_redirect_uri={REDIRECT_LOGOUT}"
    )


def setup(app):
    login = LoginManager()
    login.init_app(app)
    login.login_view = "login"  # type: ignore
    login.user_loader(lambda id: UserModel.query.get(int(id)))

    app.add_url_rule("/register", "register", register, methods=["GET"])
    app.add_url_rule("/login", "login", lambda: site_login())
    app.add_url_rule("/logout", "logout", logout)
