import json
from flask import Flask, request, render_template, redirect, make_response

from interpreter.parser_.ast_objects import Output, Error
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.token_queue import TokenQueue
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.utils.ast_visualizer import ASTVisualizer
from main import evaluate
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

    t = Tokenizer(source_code)
    tq = TokenQueue(t)
    p = Parser(tq)
    ast = p.parse()

    ast_v = ASTVisualizer(ast, "./static/graph.gv")
    ast_v.visualize()

    return redirect(f"/static/graph.gv.pdf")
