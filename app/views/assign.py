from flask import request, flash, redirect, render_template
from flask_login import login_required
from app.mail_template import create_organiser_mail_SES

from app.models import SubmissionModel, db, UserModel
from app.send_email import send_email


@login_required
def view_post(id):
    submission = SubmissionModel.query.filter_by(id=id).first()

    submission.owner_email = request.form["email"]
    submission.owner_user = request.form["username"]
    submission.status = "Folyamatban"
    db.session.commit()

    # send mail
    send_email(
        "RÜM szervező lettél!",
        create_organiser_mail_SES(submission),
        request.form["email"],
    )

    flash("Szervező sikeresen hozzáadva!", "success")
    return redirect(f"/single_submission/{id}")


@login_required
def view_get(id):
    user_list = UserModel.query.all()
    submission = SubmissionModel.query.filter_by(id=id).first()
    return render_template("assign.html", user_list=user_list, submission=submission)


def setup(app):
    app.add_url_rule(
        "/assign/<id>",
        "assign_post",
        view_post,
        methods=["POST"],
    )
    app.add_url_rule(
        "/assign/<id>",
        "assign",
        view_get,
        methods=["GET"],
    )
