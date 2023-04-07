import json
from flask import Flask, request, render_template, redirect, make_response
from main import evaluate
from interpreter.evaluator._environment import Environment

app = Flask(__name__)


@app.route("/")
def hello_world():
    source_code = request.cookies.get("source_code", "")
    results = request.cookies.get("results", "")
    if results:
        results = json.loads(results)
    else:
        results = []

    return render_template("index.html", source_code=source_code, results=results)


@app.route("/interpret", methods=["POST"])
def interpret():
    source_code = request.form["source"]

    results = evaluate(source_code, Environment())

    resp = make_response(redirect("/"))
    resp.set_cookie("source_code", source_code)
    resp.set_cookie("results", json.dumps(list(map(str, results))))
    return resp


@app.route("/clear", methods=["POST"])
def clear():
    resp = make_response(redirect("/"))
    resp.delete_cookie("source_code")
    resp.delete_cookie("results")
    return resp


@app.route("/guide")
def guide():

    language_spec_data = {
        "data_types": {
            "title": "Data Types",
            "headers": ("Data Type", "Examples"),
            "rows": [
                ("Integer", "1, 2, 3, 10, 13, 100, 1234567890"),
                ("Float", "1.1, 2.5, 3.14159")
            ]
        },
        "operators": {
            "title": "Operators",
            "headers": ("Name", "Literal"),
            "rows": [
                ("Add", "+"),
                ("Subtract", "-"),
                ("Multiply", "*"),
                ("Divide", "/"),
                ("Assignment", "="),
                ("Unary: Negative", "-"),
                ("Unary: Positive", "+")
            ]
        }
    }

    return render_template("guide.html", **language_spec_data)
