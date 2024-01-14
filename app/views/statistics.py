from flask import Flask, render_template
from geojson import dumps as gj_dump

from app.models import SubmissionModel, UserModel


def view():
    post_count = SubmissionModel.query.count()
    user_count = UserModel.query.count()
    submitted_count = SubmissionModel.query.filter_by(status="Bejelentve").count()
    wip_count = SubmissionModel.query.filter_by(status="Folyamatban").count()
    progress_count = SubmissionModel.query.filter_by(status="Készül").count()
    completed_count = SubmissionModel.query.filter_by(status="Megoldva").count()
    awareness_count = SubmissionModel.query.filter_by(status="Figyelemfelhívás").count()

    grouped = SubmissionModel.query.group_by("county").all()
    county_count_dict = {}
    for i in grouped:
        county_count_dict[i.county] = SubmissionModel.query.filter_by(
            county=i.county
        ).count()
    county_dump = gj_dump(county_count_dict, sort_keys=True)

    return render_template(
        "statistics.html",
        post_count=post_count,
        user_count=user_count,
        submitted_count=submitted_count,
        wip_count=wip_count,
        progress_count=progress_count,
        completed_count=completed_count,
        awareness_count=awareness_count,
        county_count_dict=county_dump,
    )


def setup(app: Flask):
    app.add_url_rule("/statistics", "statistics", view, methods=["GET"])
