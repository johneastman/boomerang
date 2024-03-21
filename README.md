# Boomerang
Boomerang is a programming language written in Python. The syntax was inspired by Haskell and Python (see [the language specs](#language-specs) for more information on the language).

Some defining characteristics of Boomerang are:

-   **Interpreted:** code executes in the runtime of another language (in this case, Python).
-   **Procedural:** commands are executed in the order they are defined.
-   **Dynamically Typed:** types are not declared explicitly (unlike languages like C++ or Java); rather, types are inferred from values (for example, `1` and `3.14159` are numbers, `"hello world!"` is a string, `true` and `false` are booleans, etc.).
-   **Strongly Typed:** there are strict rules for how different types interact (e.g. `1 + 1` or `1 + 1.5` are valid, but `1 + "hello world!"` is invalid).
-   **Immutable:** data is immutable, and operations return new data instead of modifying existing data.

# Install
1. Download and install [Python 3.11+](https://www.python.org/downloads/)
2. `pip install -r requirements.txt`
    - May need to run `python -m pip install -r requirements.txt`
3. Install [graphviz](https://graphviz.org/download/)
4. Optional: this project uses lefthook for pre-commit verification. Follow the installation and setup process [here](https://github.com/evilmartians/lefthook/blob/master/docs/full_guide.md).

**NOTE:** you may need to replace `python` with `python3`, though throughout the rest of the setup guide, I simply use `python`.

# Running the Project

## Command Line
2. To run the REPL, run `python main.py`
3. To run a Boomerang file, run `python main.py [path to file]`. Boomerang files end with `.bng`.
4. When running a Boomerang file, create an AST visualization with the `-v`/`--visualize` flag, which will save a graphical representation of the AST to a pdf file. AST visualization is not supported for the REPL.

## Flask App
Boomerang has a web interface that will allow for executing code directly in the browser!

1. From this project's root directory, run the following code to create a `.env` file with `SECRET_KEY`:
    ```python
     import secrets

     key = secrets.token_hex()
     with open(".env", "w") as file:
         file.write(f"export SECRET_KEY={key}")
    ```

2. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
3. With Docker Desktop running, run the following command from the root directory:
    ```
    docker compose up --build
    ```
4. The app should now be running at http://localhost:8000/.

### Docker

#### Building and running your application
When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:8000.

#### Deploying your application to the cloud
First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

#### References
* [Docker's Python guide](https://docs.docker.com/language/python/)

## Deploying to Pythonanywhere

1. Make sure you have signed up for a free PythonAnywhere account, and you’re logged in.
2. Go to the Web menu item and then press the Add new web app button.
3. Click Next, then click on Flask and click on the latest version of Python that you see there. Then click Next again to accept the project path.
4. In the Code section of the Web menu page click on Go to Directory next to Source Code.
5. Click "Open Bash console here" at top of page.
6. Replaced the content of `mysite` with this repo: `git clone https://github.com/johneastman/boomerang.git mysite`
    - You may need to delete (`rm -rf mysite`) or rename (`cp -r mysite/ mysite2/`) existing `mysite` directory.
7. Edit last line of `jeastman_pythonanywhere_com_wsgi.py` file, replacing `from flask_app import app as application` with `from flask_app.app import app as application` (add `.app` after `flast_app`).
8. Back on the web app configuration page, I clicked `Reload jeastman.pythonanywhere.com`

### Additional Resources
-   Steps 1 - 4 source: https://pythonhow.com/python-tutorial/flask/deploy-flask-web-app-pythonanywhere/
-   Additional resources: https://help.pythonanywhere.com/pages/UploadingAndDownloadingFiles

# Development Guide
The following information is for contributing to this project.

## Leftlook
To disable lefthook, add `LEFTHOOK=0` before your command. More information, as well as other usage information, can be found [here](https://github.com/evilmartians/lefthook/blob/master/docs/usage.md).

## Exceptions
There are two types of exceptions: [Language Exceptions](#language-exceptions) and [Program Exceptions](#program-exceptions).

### Language Exceptions
These are errors introduced by users into Boomerang code (syntax errors, index out of range, invalid token, etc). The interpreter will catch these errors and display them to the user.

To raise a language exception, call the `raise_error` method in `utils.py`, which raises a `LanguageRuntimeException` exception.

### Program Exceptions
These are errors with the Python code itself and exist to aid the development process. To raise a program exception, raise any valid Python exception (e.g., `raise ValueError`, `raise Exception`, `raise RuntimeError`, etc.).

# Language Specs
The language specs can be found [here](./docs/README.md).

# License
This project is licenced under the [MIT License](LICENSE).
