"""
For saving files locally, use "app.root_path"
"""
import json
import base64
import secrets

from flask import Flask, Response, request, render_template, redirect, make_response, session

from interpreter.parser_.ast_objects import Output, Error
from interpreter.utils.utils import LanguageRuntimeException
from main import evaluate, visualize_ast
from interpreter.evaluator.environment_ import Environment

app = Flask(__name__)
app.secret_key = secrets.token_hex(64)


# Cookie keys
SOURCE_CODE = "source_code"
RESULTS = "results"


@app.route("/")
def index():
    source_code = session.get(SOURCE_CODE, "")
    code_output = session.get(RESULTS, None)

    parsed_results = [] if code_output is None else json.loads(code_output)

    return render_template("index.html", source_code=source_code, results=parsed_results)


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

    return create_response("/", source_code, json.dumps(list(map(str, output_data))))


@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return redirect("/")


@app.route("/visualize", methods=["POST"])
def visualize():
    source_code = request.form["source"]

    try:
        vis_data = visualize_ast(source_code)
        vis_data = base64.b64encode(vis_data)  # convert to base64 as bytes
        vis_data = vis_data.decode()  # convert bytes to string
        return render_template("visualize.html", data=vis_data)

    except LanguageRuntimeException as e:
        output_data = [Error(e.line_num, str(e))]

    except Exception as e:
        message = str(e)
        output_data = [Output(-1, f"Unexpected internal error: {message}")]

    return create_response("/", source_code, json.dumps(list(map(str, output_data))))


def create_response(path: str, source_code: str, return_results: str) -> Response:
    session[SOURCE_CODE] = source_code
    session[RESULTS] = return_results
    return redirect(path)


if __name__ == "__main__":
    app.run()
