from typing import cast
from flask import Flask
from flask.typing import ResponseValue
import flask_excel as excel

from app.models import SubmissionModel
from app.utils import auditlog, get_date, role_required


@role_required(("admin", "coordinator"))
def view() -> ResponseValue:
    auditlog("download all data")

    submissions = SubmissionModel.query.all()

    submission_id = [submission.id for submission in submissions]
    title = [submission.title for submission in submissions]
    problem_type = [submission.problem_type for submission in submissions]
    problem_type = [submission.problem_type for submission in submissions]
    description = [submission.description for submission in submissions]
    suggestion = [submission.suggestion for submission in submissions]
    solution = [submission.solution for submission in submissions]
    address = [submission.address for submission in submissions]
    city = [submission.city for submission in submissions]
    county = [submission.county for submission in submissions]
    lat = [submission.lat for submission in submissions]
    lng = [submission.lng for submission in submissions]
    submitter_email = [submission.submitter_email for submission in submissions]
    submitter_phone = [submission.submitter_phone for submission in submissions]
    owner_email = [submission.owner_email for submission in submissions]
    owner_user = [submission.owner_user for submission in submissions]
    created_date = [submission.created_date for submission in submissions]
    status = [submission.status for submission in submissions]
    featured = [submission.featured for submission in submissions]
    status_changed_date = [submission.status_changed_date for submission in submissions]
    status_changed_by = [submission.status_changed_by for submission in submissions]

    extension_type = "csv"
    filename = "RÜM_összes_bejelentés_" + str(get_date()) + "." + extension_type
    data = {
        "Ügyszám": submission_id,
        "Elnevezés": title,
        "Típus": problem_type,
        "Leírás": description,
        "Megoldási javaslat": suggestion,
        "Megoldás": solution,
        "Cím": address,
        "Kiemelt": featured,
        "Város": city,
        "Megye": county,
        "Szélességi fok": lat,
        "Hosszúsági fok": lng,
        "Bejelentő email": submitter_email,
        "Bejelentő telefon": submitter_phone,
        "Szervező email": owner_email,
        "Szervező felhasználó": owner_user,
        "Létrehozva": created_date,
        "Státusz": status,
        "Státusz változás dátuma": status_changed_date,
        "Státuszt változtató felhasználó": status_changed_by,
    }
    return cast(
        ResponseValue,
        excel.make_response_from_dict(
            data, file_type=extension_type, file_name=filename
        ),
    )


def setup(app: Flask):
    excel.init_excel(app)
    app.add_url_rule("/download", "download_data", view, methods=["GET"])
