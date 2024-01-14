from flask import Flask, flash, render_template, request
from flask_login import login_required

from app.models import db, SubmissionModel, UserModel
from app.utils import role_required


@role_required("admin")
def user_manage_post(id):
    user = UserModel.query.filter_by(id=id).first()

    user_role = request.form["role"]
    user.role = user_role
    db.session.commit()
    flash("Sikeres módosítás!", "success")
    return render_template("single_user.html", user=user)


@role_required("admin")
def user_manage_get(id):
    user = UserModel.query.filter_by(id=id).first()
    return render_template("single_user.html", user=user)


@login_required
def user_account():
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


@role_required("admin")
def user_management():
    user_list = UserModel.query.all()
    return render_template("user_management.html", user_list=user_list)


@login_required
def change_user_data(user_id):
    user = UserModel.query.filter_by(id=user_id).first()

    if request.method == "POST":
        if request.form["new_user_name"] != "":
            new_user_name = request.form["new_user_name"]
            user.user_name = new_user_name
            db.session.commit()
            flash("Sikeresen módosítottad a felhasználónevedet!", "success")

        if request.form["new_email"] != "":
            new_email = request.form["new_email"]
            user.email = new_email
            db.session.commit()
            flash("Sikeresen módosítottad az email címedet!", "success")

        if request.form["new_phone"] != "":
            new_phone = request.form["new_phone"]
            user.phone = new_phone
            db.session.commit()
            flash("Sikeresen módosítottad a telefonszámodat!", "success")

    return render_template("change_user_data.html", user=user)


def setup(app: Flask):
    app.add_url_rule(
        "/user_account", "user_account", user_account, methods=["POST", "GET"]
    )
    app.add_url_rule(
        "/user_manage/<id>", "user_manage_post", user_manage_post, methods=["POST"]
    )
    app.add_url_rule(
        "/user_manage/<id>", "user_manage", user_manage_get, methods=["GET"]
    )
    app.add_url_rule(
        "/user_administration",
        "user_management",
        user_management,
        methods=["POST", "GET"],
    )
    app.add_url_rule(
        "/change_user_data/<user_id>",
        "change_user_data",
        change_user_data,
        methods=["POST", "GET"],
    )
