"""
For saving files locally, use "app.root_path"
"""
import json
import base64
from flask import Flask, request, render_template, redirect, make_response

from interpreter.parser_.ast_objects import Output, Error
from main import evaluate, visualize_ast
from interpreter.evaluator.environment_ import Environment

app = Flask(__name__)


@app.route("/")
def index():
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

    try:
        results = evaluate(source_code, Environment())

        # Filter out results that do not produce an output. These will be sent to the page for display
        output_data = filter(lambda obj: isinstance(obj, Output) or isinstance(obj, Error), results)
    except Exception as e:
        message = str(e)
        output_data = [Output(-1, f"Unexpected internal error: {message}")]

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


@app.route("/visualize", methods=["POST"])
def visualize():
    source_code = request.form["source"]

    vis_data = visualize_ast(source_code)

    vis_data = base64.b64encode(vis_data)  # convert to base64 as bytes
    vis_data = vis_data.decode()  # convert bytes to string

    return render_template("visualize.html", data=vis_data)
