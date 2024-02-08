import logging

from flask import Flask, request, flash, render_template, redirect, Markup

from app.utils import valid_email, get_date, save_picture, valid_image
from app.env import MAP_KEY, INIT_LAT, INIT_LNG, UPLOAD_FOLDER
from app.models import db, SubmissionModel
from app.mail_template import create_submission_mail_SES
from app.send_email import send_email

logger = logging.getLogger(__name__)


def view_post():
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

    pictures = request.files.getlist("files")
    additional_pictures = request.files.getlist("additional_files")

    if additional_pictures[0].filename != "":
        pictures = pictures + additional_pictures

    for picture in pictures:
        if picture and not valid_image(picture.filename):
            flash("Nem megengedett fájlkiterjesztés!", "danger")
            return render_template(
                "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
            )

    submission = SubmissionModel(
        title=Markup.escape(request.form["title"]),
        problem_type=Markup.escape(request.form["type"]),
        description=Markup.escape(request.form["description"]),
        suggestion=Markup.escape(request.form["suggestion"]),
        city=Markup.escape(request.form["city"]),
        zipcode=request.form["zipcode"],
        county=Markup.escape(request.form["county"]),
        address=Markup.escape(request.form["address"]),
        lat=request.form["lat"],
        lng=request.form["lng"],
        submitter_email=Markup.escape(request.form["email"]),
        submitter_phone=Markup.escape(request.form["phone"]),
        owner_email="",
        status="Bejelentve",
        featured=False,
        status_changed_date=get_date(),
        status_changed_by=Markup.escape(request.form["email"]),
        created_date=get_date(),
    )

    db.session.add(submission)
    db.session.commit()

    # SAVE PICTURES
    save_picture(
        pictures=pictures,
        upload_folder=UPLOAD_FOLDER,
        tag="before",
        submission_id=str(submission.id),
    )

    send_email(
        "Sikeres városmódosító bejelentés!",
        create_submission_mail_SES(submission),
        request.form["email"],
    )

    flash("Sikeres bejelentés! Küldtünk egy levelet is!", "success")
    return redirect(f"/single_submission/{submission.id}")


def view_get():
    return render_template(
        "submission.html", ACCESS_KEY=MAP_KEY, lat=INIT_LAT, lng=INIT_LNG
    )


def setup(app: Flask):
    app.add_url_rule("/submission", "add_submission_post", view_post, methods=["POST"])
    app.add_url_rule("/submission", "add_submission", view_get, methods=["GET"])
