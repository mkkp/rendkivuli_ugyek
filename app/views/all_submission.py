from flask import flash, render_template, request, session, Markup
from app.env import ROWS_PER_PAGE

from app.models import SubmissionModel


def view():
    page = request.args.get("page", 1, type=int)

    post_list = SubmissionModel.query.order_by(
        SubmissionModel.created_date.desc()
    ).paginate(page=page, per_page=ROWS_PER_PAGE)

    featured = SubmissionModel.query.filter_by(featured=True).all()

    if request.method == "POST":
        county = request.form["county"]
        zipcode = request.form["zipcode"]
        problem_type = request.form["type"]
        status = request.form["status"]
        search_text = Markup.escape(request.form["full_text_search"])

        county_dict = {}
        zipcode_dict = {}
        problem_type_dict = {}
        status_dict = {}

        if county != "":
            county_dict = {"county": county}

        if zipcode != "":
            zipcode_dict = {"zipcode": zipcode[:-1]}

        if problem_type != "":
            problem_type_dict = {"problem_type": problem_type}

        if status != "":
            status_dict = {"status": status}

        if search_text != "":
            search_text = search_text.lower()
            filtered_list = (
                SubmissionModel.query.filter(
                    SubmissionModel.description.ilike(f"%{search_text}%")
                )
                .order_by(SubmissionModel.created_date.desc())
                .paginate(page=page, per_page=ROWS_PER_PAGE)
            )

            # A szöveges kereső még nincs integrálva a többi keresőopcióval,
            # ezért vagy-vagy alapon lehet használni
            return render_template("all_submission.html", post_list=filtered_list)

        # merge dicts
        query_dict = county_dict | zipcode_dict | problem_type_dict | status_dict

        # store dict in session cookie
        session["filter"] = query_dict

        try:
            filtered_list = (
                SubmissionModel.query.filter_by(**query_dict)
                .order_by(SubmissionModel.created_date.desc())
                .paginate(page=1, per_page=ROWS_PER_PAGE)
            )

        except Exception:
            flash("Nincs találati eredmény", "danger")
            return render_template("all_submission.html", post_list=post_list)

        return render_template(
            "all_submission.html", post_list=filtered_list, filters=query_dict
        )

    # GET
    try:
        if "filter" in session.keys():
            query_dict = session["filter"]
            filtered_list = (
                SubmissionModel.query.filter_by(**query_dict)
                .order_by(SubmissionModel.created_date.desc())
                .paginate(page=page, per_page=ROWS_PER_PAGE)
            )
            return render_template(
                "all_submission.html",
                post_list=filtered_list,
                featured=featured,
                filters=query_dict,
            )
    except Exception:
        pass

    return render_template(
        "all_submission.html", post_list=post_list, featured=featured
    )


def setup(app):
    app.add_url_rule(
        "/all_submission",
        "all_submission",
        view,
        methods=["POST", "GET"],
    )
