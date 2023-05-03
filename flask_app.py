"""
For saving files locally, use "app.root_path"
"""
import json
import base64
from io import BytesIO
import os

from flask import Flask, Response, request, render_template, redirect, session, send_file
from dotenv import load_dotenv

from interpreter.parser_.ast_objects import Error
from interpreter.utils.utils import LanguageRuntimeException
from main import evaluate, visualize_ast
from interpreter.evaluator.environment_ import Environment


app = Flask(__name__)

# Set secret key
project_folder = os.path.expanduser(app.root_path)
load_dotenv(os.path.join(project_folder, ".env"))
app.secret_key = os.getenv("SECRET_KEY")

# Cookie/Session keys
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
        output: list[str] = evaluate(source_code, Environment())
    except Exception as e:
        output = [f"Unexpected internal error: {str(e)}"]

    return create_response("/", source_code, json.dumps(output))


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
        error_object = Error(e.line_num, str(e))
        output_data = [str(error_object)]

    except Exception as e:
        output_data = [f"Unexpected internal error: {str(e)}"]

    return create_response("/", source_code, json.dumps(output_data))


@app.route("/download", methods=["POST"])
def download():
    source_code = request.form["source"]

    buffer = BytesIO()
    buffer.write(source_code.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="main.bng",
        mimetype="text"
    )


def create_response(path: str, source_code: str, return_results: str) -> Response:
    session[SOURCE_CODE] = source_code
    session[RESULTS] = return_results
    return redirect(path)


if __name__ == "__main__":
    app.run()
