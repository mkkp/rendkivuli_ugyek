from flask import Flask, redirect, render_template


def view():
    try:
        import requests

        response = requests.get("https://dog.ceo/api/breeds/image/random", timeout=1)
        resp_json = response.json()
        kutyi_pic = resp_json["message"]
        return render_template("easter_egg.html", kutyi_pic=kutyi_pic)
    except Exception:
        pass
    return redirect("/")


def setup(app: Flask):
    app.add_url_rule("/kutyi", "easter_egg", view, methods=["GET"])
