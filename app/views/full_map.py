from flask import flash, render_template, request

from geojson import Feature
from geojson import Point
from geojson import FeatureCollection
from geojson import dumps as gj_dump

from app.env import INIT_LAT, INIT_LNG, MAP_KEY
from app.models import SubmissionModel


def view_post():
    emtpy_result = False

    submission_type = request.form["type"]
    submission_status = request.form["status"]

    problem_type_dict = {}
    status_dict = {}

    if submission_type != "":
        problem_type_dict = {"problem_type": submission_type}

    if submission_status != "":
        status_dict = {"status": submission_status}

    query_dict = problem_type_dict | status_dict

    filtered_list = SubmissionModel.query.filter_by(**query_dict).all()

    if len(filtered_list) == 0:
        filtered_list = SubmissionModel.query.all()
        emtpy_result = True

    point_list = []
    for i, post in enumerate(filtered_list):
        i = Feature(geometry=Point((post.lng, post.lat)))
        i.properties["id"] = post.id
        i.properties["title"] = post.title
        i.properties["status"] = post.status
        i.properties["type"] = post.problem_type
        i.properties["cover_image"] = post.cover_image
        point_list.append(i)

    feature_collection = FeatureCollection(point_list)
    dump = gj_dump(feature_collection, sort_keys=True)

    if emtpy_result:
        flash(
            f"Sajnos nem találtuk a {submission_type} és {submission_status} keresztmetszetét.",
            "warning",
        )
        submission_type = None
        submission_status = None

    return render_template(
        "map.html",
        ACCESS_KEY=MAP_KEY,
        lat=INIT_LAT,
        lng=INIT_LNG,
        post_list=filtered_list,
        feature_collection=dump,
        submission_type=submission_type,
        submission_status=submission_status,
    )


def view_get():
    post_list = SubmissionModel.query.all()
    point_list = []
    for i, post in enumerate(post_list):
        i = Feature(geometry=Point((post.lng, post.lat)))
        i.properties["id"] = post.id
        i.properties["title"] = post.title
        i.properties["status"] = post.status
        i.properties["type"] = post.problem_type
        i.properties["cover_image"] = post.cover_image
        point_list.append(i)

    feature_collection = FeatureCollection(point_list)
    dump = gj_dump(feature_collection, sort_keys=True)

    return render_template(
        "map.html",
        ACCESS_KEY=MAP_KEY,
        lat=INIT_LAT,
        lng=INIT_LNG,
        post_list=post_list,
        feature_collection=dump,
    )


def setup(app):
    app.add_url_rule("/full_map", "full_map_post", view_post, methods=["POST"])
    app.add_url_rule("/full_map", "full_map", view_get, methods=["GET"])
