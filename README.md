# Boomerang
Boomerang is a programming language written in Python. The syntax was inspired by Haskell and Python (see [the language specs](#language-specs) for more information on the language).

Some defining characteristics of Boomerang are:
* **Interpreted:** code executes in the runtime of another language (in this case, Python).
* **Procedural:** commands are executed in the order they are defined.
* **Dynamically Typed:** types are not declared explicitly (unlike languages like C++ or Java); rather, types are inferred from values (for example, `1` and `3.14159` are numbers, `"hello world!"` is a string, `true` and `false` are booleans, etc.).
* **Strongly Typed:** there are strict rules for how different types interact (e.g. `1 + 1` or `1 + 1.5` are valid, but `1 + "hello world!"` is invalid).
* **Immutable:** data is immutable, and operations return new data instead of modifying existing data.

# Install
1. Download and install [Python 3.11+](https://www.python.org/downloads/)
2. `pip install -r requirements.txt`
    * May need to run `python -m pip install -r requirements.txt`
3. Install [graphviz](https://graphviz.org/download/)
4. Optional: this project uses lefthook for pre-commit verification. Follow the installation and setup process [here](https://github.com/evilmartians/lefthook/blob/master/docs/full_guide.md).

**NOTE:** you may need to replace `python` with `python3`, though throughout the rest of the setup guide, I simply use `python`.

# Running
Boomerang files end with the `.bng` extension (e.g., `main.bng`).

To run a Boomerang file:
`python main.py --path [PATH TO FILE]`

Include the `-v`/`--visualize` flag to save a graph representation of the Abstract Syntax Tree as a PDF.

To run the repl:
`python main.py --repl`

AST visualization is not available for the REPL.

## Run the Flask App
Boomerang has a web interface that will allow you to run it from the browser!

1. From this project's root directory, run the following code to create a `.env` file with `SECRET_KEY`:
   ```python
    import secrets

    key = secrets.token_hex()
    with open("flask_app/.env", "w") as file:
        file.write(f"export SECRET_KEY={key}")
   ```
2. Run the app with `python flask_main.py`.

### Deploying to Pythonanywhere
1. Make sure you have signed up for a free PythonAnywhere account, and you’re logged in. 
2. Go to the Web menu item and then press the Add new web app button. 
3. Click Next, then click on Flask and click on the latest version of Python that you see there. Then click Next again to accept the project path.
4. In the Code section of the Web menu page click on Go to Directory next to Source Code.
5. Click "Open Bash console here" at top of page.
6. Replaced the content of `mysite` with this repo: `git clone https://github.com/johneastman/boomerang.git mysite`
    * You may need to delete (`rm -rf mysite`) or rename (`cp -r mysite/ mysite2/`) existing `mysite` directory.
7. Edit last line of `jeastman_pythonanywhere_com_wsgi.py` file, replacing `from flask_app import app as application` with `from flask_app.app import app as application` (add `.app` after `flast_app`).
8. Back on the web app configuration page, I clicked `Reload jeastman.pythonanywhere.com`

### Additional Resources
* Steps 1 - 4 source: https://pythonhow.com/python-tutorial/flask/deploy-flask-web-app-pythonanywhere/
* Additional resources: https://help.pythonanywhere.com/pages/UploadingAndDownloadingFiles

# Development Guide
The following information is for contributing to this project.

## Exceptions
There are two types of exceptions: [Language Exceptions](#language-exceptions) and [Program Exceptions](#program-exceptions).

### Language Exceptions
These are errors introduced by users into Boomerang code (syntax errors, index out of range, invalid token, etc). The interpreter will catch these errors and display them to the user.

To raise a language exception, call the `raise_error` method in `utils.py`, which raises a `LanguageRuntimeException` exception.

### Program Exceptions
These are errors with the Python code itself and exist to aid the development process. To raise a program exception, raise any valid Python exception (e.g., `raise ValueError`, `raise Exception`, `raise RuntimeError`, etc.).

# Language Specs
The language specs can be found [here](./docs/docs.md).

# License
This project is licenced under the [MIT License](LICENSE).
