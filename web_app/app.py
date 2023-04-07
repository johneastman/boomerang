import json
import typing

from flask import Flask, request, render_template, redirect, make_response

from main import evaluate

from _parser._parser import Parser
from _parser.ast_objects import Base, NoReturn
from evaluator._environment import Environment
from evaluator.evaluator import Evaluator
from tokens.token_queue import TokenQueue
from tokens.tokenizer import Tokenizer
from utils.utils import LanguageRuntimeException

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


@app.route("/interpreter", methods=["POST"])
def button():
    source_code = request.form["source"]

    results = evaluate(source_code, Environment())
    results = list(filter(lambda b: not isinstance(b, NoReturn), results))

    resp = make_response(redirect("/"))
    resp.set_cookie("source_code", source_code)
    resp.set_cookie("results", json.dumps(list(map(str, results))))
    return resp
