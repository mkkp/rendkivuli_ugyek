from flask import Flask, render_template


def setup(app: Flask):
    app.register_error_handler(404, lambda e: render_template("404.html"))
    app.register_error_handler(502, lambda e: render_template("502.html"))
