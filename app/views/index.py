from flask import Flask, render_template


def view():
    """
    Kezdőoldal
    Bejelentkezés nem szükséges
    """
    return render_template("index.html")


def setup(app: Flask):
    app.add_url_rule("/", "index", view, methods=["GET"])
