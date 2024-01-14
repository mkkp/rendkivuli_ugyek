from flask import redirect, flash
from flask_login import login_required
from app.models import CommentModel, db


@login_required
def view(id):
    comment = CommentModel.query.filter_by(id=id)
    submission_id = comment.first().parent_id
    comment.delete()
    db.session.commit()
    flash("A kommentet sikeresen töröltük!", "success")
    return redirect(f"/single_submission/{submission_id}")


def setup(app):
    app.add_url_rule(
        "/delete_comment/<id>",
        "delete_comment",
        view,
        methods=["GET"],
    )
