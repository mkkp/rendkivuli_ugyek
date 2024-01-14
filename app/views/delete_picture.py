from flask import redirect, flash
from flask_login import login_required
from app.models import ImageAfterModel, ImageBeforeModel, db


@login_required
def view(status_type, id):
    if status_type == "before":
        picture = ImageBeforeModel.query.filter_by(id=id)
    elif status_type == "after":
        picture = ImageAfterModel.query.filter_by(id=id)
    else:
        return redirect("/")

    submission_id = picture.first().parent_id
    picture.delete()
    db.session.commit()
    flash("A képet sikeresen töröltük!", "success")
    return redirect(f"/single_submission/{submission_id}")


def setup(app):
    app.add_url_rule(
        "/delete_picture/<status_type>/<id>",
        "delete_picture",
        view,
        methods=["GET"],
    )
