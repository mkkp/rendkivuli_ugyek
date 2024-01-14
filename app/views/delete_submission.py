import shutil
from flask import redirect, flash
from flask_sqlalchemy import os
from app.env import UPLOAD_FOLDER
from app.models import (
    CommentModel,
    ImageAfterModel,
    ImageBeforeModel,
    SubmissionModel,
    db,
)
from app.utils import auditlog, role_required


@role_required(("admin", "coordinator"))
def view(id):
    auditlog(f"delete submission_{id}")

    submission = SubmissionModel.query.filter_by(id=id)
    submission.delete()

    images_before = ImageBeforeModel.query.filter_by(parent_id=id)
    images_after = ImageAfterModel.query.filter_by(parent_id=id)
    comments = CommentModel.query.filter_by(parent_id=id)

    shutil.rmtree(os.path.join(UPLOAD_FOLDER, str(id)))

    images_before.delete()
    images_after.delete()
    submission.delete()
    comments.delete()

    db.session.commit()
    flash("A bejegyzést sikeresen töröltük!", "success")
    return redirect("/")


def setup(app):
    app.add_url_rule(
        "/delete_submission/<id>",
        "delete_submission",
        view,
        methods=["GET"],
    )
