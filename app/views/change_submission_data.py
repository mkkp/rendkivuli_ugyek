from flask import redirect, render_template, request, flash
from flask_login import login_required
from app.env import MAP_KEY
from app.mail_template import create_solution_mail_SES, create_status_change_mail_SES
from app.models import db, SubmissionModel
from app.send_email import send_email
from app.utils import get_date


@login_required
def view_post(submission_id):
    submission = SubmissionModel.query.filter_by(id=submission_id).first()

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

    if "featured" in request.form and not submission.featured:
        submission.featured = True
        db.session.commit()
        flash("Sikeresen kiemelted az ügyet!", "success")

    if "featured" not in request.form and submission.featured:
        submission.featured = False
        db.session.commit()

    if request.form["status"] != submission.status:
        new_status = request.form["status"]
        changed_by = request.form["current_user"]

        submission.status = new_status
        submission.status_changed_date = get_date()
        submission.status_changed_by = changed_by
        db.session.commit()

        mail_sent_text = ""
        # MAIL TO SZERVEZŐ
        if submission.owner_email != "":
            send_email(
                f"Státusz változás: {submission.title}",
                create_status_change_mail_SES(submission),
                submission.owner_email,
            )
            mail_sent_text = " A szervezőnek ment levél."
        if new_status == "Megoldva":
            send_email(
                f"RÜM befejezett ügy: {submission.title}",
                create_solution_mail_SES(submission),
                submission.submitter_email,
            )

        flash(
            f"Sikeresen módosítottad az ügy státuszát erre: {new_status}. {mail_sent_text}",
            "success",
        )

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


@login_required
def view_get(submission_id):
    submission = SubmissionModel.query.filter_by(id=submission_id).first()
    return render_template(
        "change_submission_data.html", submission=submission, ACCESS_KEY=MAP_KEY
    )


def setup(app):
    app.add_url_rule(
        "/change_submission_data/<submission_id>",
        "change_submission_data_post",
        view_post,
        methods=["POST"],
    )
    app.add_url_rule(
        "/change_submission_data/<submission_id>",
        "change_submission_data",
        view_get,
        methods=["GET"],
    )
