import json
from flask import Flask, request, render_template, redirect, make_response

from interpreter.parser_.ast_objects import Output, Error
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

    # Filter out results that do not produce an output. These will be sent to the page for display
    output_data = filter(lambda obj: isinstance(obj, Output) or isinstance(obj, Error), results)

    resp = make_response(redirect("/"))
    resp.set_cookie("source_code", source_code)
    resp.set_cookie("results", json.dumps(list(map(str, output_data))))
    return resp


@app.route("/clear", methods=["POST"])
def clear():
    resp = make_response(redirect("/"))
    resp.delete_cookie("source_code")
    resp.delete_cookie("results")
    return resp
