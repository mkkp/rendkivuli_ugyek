from flask import redirect, flash
from flask_login import login_required
from app.models import ImageAfterModel, ImageBeforeModel, SubmissionModel, db


@login_required
def view(status_type, id):
    if status_type == "before":
        picture = ImageBeforeModel.query.filter_by(id=id)
    elif status_type == "after":
        picture = ImageAfterModel.query.filter_by(id=id)
    else:
        return redirect("/")

    submission_id = picture.first().parent_id
    submission = SubmissionModel.query.filter_by(id=submission_id).first()
    submission.cover_image = picture.first().thumb_file_name
    submission.cover_image_full = picture.first().file_name

    db.session.commit()

    flash(
        """A borítókép cserélési eljárás
             előkészítését elindítottuk.
             Ügyintézőnk egy héten belül jelentkezik.
             Kérjük, addig ne mozduljon a készüléke mellől!
         """,
        "success",
    )
    return redirect(f"/single_submission/{submission_id}")


def setup(app):
    app.add_url_rule(
        "/change_cover/<status_type>/<id>",
        "change_cover",
        view,
        methods=["GET"],
    )
