# ADATVÉDELMI TÁJÉKOZTATÓ
from flask import Flask, render_template


def view():
    return render_template("user_data_info.html")


def setup(app: Flask):
    app.add_url_rule("/user_data_info", "user_data_info", view, methods=["GET"])
