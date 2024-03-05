from random import randint
from flask import Flask, request, flash, redirect, url_for
from keycloak import KeycloakOpenID
from app.models import db, UserModel
from flask_login import LoginManager, login_user, logout_user
from app.utils import get_date, get_random_name
from app.env import REDIRECT_LOGIN, KC_SERVER_URL, REALM_NAME, KC_CLIENT_ID

keycloak_openid = KeycloakOpenID(
    server_url=KC_SERVER_URL,
    client_id=KC_CLIENT_ID,
    realm_name=REALM_NAME,
)


def view():
    code = request.args.get("code")

    token = keycloak_openid.token(
        grant_type="authorization_code", code=code, redirect_uri=REDIRECT_LOGIN
    )

    userinfo = keycloak_openid.userinfo(token["access_token"])
    user_email = userinfo["email"]
    user = UserModel.query.filter_by(email=user_email).first()

    if user:
        login_user(user)
        user.last_login = get_date()
        db.session.commit()

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

    return redirect(url_for("index"))


def setup(app: Flask):
    app.add_url_rule("/szimat", "szimat", view, methods=["GET"])
