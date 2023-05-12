"""
For saving files locally, use "app.root_path"
"""
import json
import base64
from io import BytesIO
import os

from flask import Flask, Response, request, render_template, redirect, session, send_file, flash
from dotenv import load_dotenv

from interpreter.parser_.ast_objects import Error
from utils.utils import LanguageRuntimeException, Platform
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

BOOMERANG_FILE_EXT = "bng"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Uploading Boomerang code
        redirect_response, content = upload_files()
        if redirect_response:
            return redirect_response

        source_code = content.decode("utf-8")
        code_output = None  # clear output from previous code when uploading a file

    else:
        # Request method == GET
        source_code = session.get(SOURCE_CODE, "")
        code_output = session.get(RESULTS, None)

    parsed_output = [] if code_output is None else json.loads(code_output)

    return render_template("index.html", source_code=source_code, results=parsed_output)


def upload_files() -> tuple[Response | None, bytes]:
    """Handle uploading Boomerang code.
    """
    # Check if the post request has the file part
    if "file" not in request.files:
        flash("No file in request")
        return redirect(request.url), b""

    file = request.files["file"]

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url), b""

    # Check that the file uploaded is a valid type
    valid_types = [BOOMERANG_FILE_EXT]
    file_type, is_allowed = allowed_file(file.filename, valid_types)
    if not file or not is_allowed:
        flash(f"Invalid file type: {file_type}. Valid file types: {', '.join(valid_types)}")
        return redirect(request.url), b""

    return None, file.read()


@app.route("/interpret", methods=["POST"])
def interpret():
    source_code = request.form["source"]

    try:
        output: list[str] = evaluate(source_code, Environment(), platform=Platform.WEB.name)
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
        download_name=f"main.{BOOMERANG_FILE_EXT}",
        mimetype="text"
    )


def create_response(path: str, source_code: str, return_results: str) -> Response:
    session[SOURCE_CODE] = source_code
    session[RESULTS] = return_results
    return redirect(path)


def allowed_file(filename: str, valid_types: list[str]) -> tuple[str, bool]:
    if "." not in filename:
        return "no extension", False

    file_type = filename.rsplit(".", 1)[1].lower()
    return file_type, file_type in valid_types
