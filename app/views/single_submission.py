from flask import flash, render_template, request, url_for, Markup
from flask_login.login_manager import redirect
from app.utils import valid_image
from app.env import MAP_KEY, UPLOAD_FOLDER
from app.mail_template import create_solution_mail_SES

from app.models import (
    ImageAfterModel,
    ImageBeforeModel,
    SubmissionModel,
    db,
    CommentModel,
)
from app.send_email import send_email
from app.utils import get_date, save_picture


def view_post(submission_id):
    if "comment-submit" in request.form:
        form_comment = Markup.escape(request.form["comment"])

        if CommentModel.query.filter_by(
            body=form_comment, parent_id=submission_id
        ).first():
            # comment is duplicate
            pass

        else:
            comment = CommentModel(
                commenter=Markup.escepe(request.form["current_user"]),
                created_date=get_date(),
                body=form_comment,
                parent_id=submission_id,
            )
            db.session.add(comment)
            db.session.commit()
            flash("Sikeresen hozzáadtál egy kommentet!", "success")

    if "comment-edit" in request.form:
        body_change = Markup.escape(request.form["comment"])
        comment_id = request.form["comment_id"]
        comment = CommentModel.query.filter_by(id=comment_id).first()
        comment.body = body_change
        comment.created_date = get_date()
        db.session.commit()
        flash("Komment szerkesztve", "success")

    if "upload_before_images" in request.form:
        tag = "before"
        pictures = request.files.getlist("files")

        for picture in pictures:
            if picture and not valid_image(picture.filename):
                flash("Nem megengedett fájlkiterjesztés!", "danger")
                return redirect(
                    url_for("single_submission", submission_id=submission_id)
                )

        save_picture(pictures, UPLOAD_FOLDER, tag, submission_id)
        flash("Kép sikeresen hozzáadva!", "success")

    if "upload_after_images" in request.form:
        tag = "after"
        pictures = request.files.getlist("files")

        for picture in pictures:
            if picture and not valid_image(picture.filename):
                flash("Nem megengedett fájlkiterjesztés!", "danger")
                return redirect(
                    url_for("single_submission", submission_id=submission_id)
                )

        save_picture(pictures, UPLOAD_FOLDER, tag, submission_id)

        changed_by = request.form["current_user"]
        submission = SubmissionModel.query.filter_by(id=submission_id).first()
        submission.status = "Megoldva"
        submission.status_changed_date = get_date()
        submission.status_changed_by = changed_by
        db.session.commit()

        send_email(
            f"RÜM befejezett ügy: {submission.title}",
            create_solution_mail_SES(submission),
            submission.submitter_email,
        )

    return redirect(url_for("single_submission", submission_id=submission_id))


def view_get(submission_id):
    submission = SubmissionModel.query.filter_by(id=submission_id)
    before_img_list = ImageBeforeModel.query.filter_by(parent_id=submission_id)
    after_img_list = ImageAfterModel.query.filter_by(parent_id=submission_id)
    comment_list = CommentModel.query.filter_by(parent_id=submission_id)

    return render_template(
        "single_submission.html",
        submission=submission,
        before_img_list=before_img_list,
        after_img_list=after_img_list,
        comment_list=comment_list,
        ACCESS_KEY=MAP_KEY,
    )


def setup(app):
    app.add_url_rule(
        "/single_submission/<submission_id>",
        "single_submission_post",
        view_post,
        methods=["POST"],
    )
    app.add_url_rule(
        "/single_submission/<submission_id>",
        "single_submission",
        view_get,
        methods=["GET"],
    )
