# Boomerang
Boomerang is a programming language written in Python. The syntax was inspired by Haskell and Python (see [the language specs](#language-specs) for more information on the language).

Some defining characteristics of Boomerang are:
* **Interpreted:** code executes in the runtime of another language (in this case, Python).
* **Procedural:** commands are executed in the order they are defined.
* **Dynamically Typed:** types are not declared explicitly (unlike languages like C++ or Java); rather, types are inferred from values (for example, `1` and `3.14159` are numbers, `"hello world!"` is a string, `true` and `false` are booleans, etc.).
* **Strongly Typed:** there are strict rules for how different types interact (e.g. `1 + 1` or `1 + 1.5` are valid, but `1 + "hello world!"` is invalid).
* **Immutable:** data is immutable, and operations return new data instead of modifying existing data.

# Install
1. Download and install [Python](https://www.python.org/downloads/)
2. `pip install -r requirements.txt`
    * May need to run `python3 -m pip install -r requirements.txt`
3. Install [graphviz](https://graphviz.org/download/)
4. Optional: this project uses lefthook for pre-commit verification. Follow the installation and setup process [here](https://github.com/evilmartians/lefthook/blob/master/docs/full_guide.md)

# Running
Boomerang files end with the `.bng` extension (e.g., `main.bng`).

To run a Boomerang file:
`python3 main.py --path [PATH TO FILE]`

To run the repl:
`python3 main.py --repl`

**NOTE:** `python3` may not be how python files are run on your machine.

## Flask App
Boomerang has a web interface that will allow you to run it from the browser!

To run the Flask app, run `flask --app flask_app run`.

### Deploying to Pythonanywhere
1. Make sure you have signed up for a free PythonAnywhere account, and you’re logged in. 
2. Go to the Web menu item and then press the Add new web app button. 
3. Click Next, then click on Flask and click on the latest version of Python that you see there. Then click Next again to accept the project path.
4. In the Code section of the Web menu page click on Go to Directory next to Source Code.
5. Click "Open Bash console here" at top of page.
6. Replaced the content of `mysite` with this repo: `git clone https://github.com/johneastman/boomerang.git mysite`
    * You may need to delete (`rm -rf mysite`) or rename (`cp -r mysite/ mysite2/`) existing `mysite` directory.
7. Back on the web app configuration page, I clicked `Reload jeastman.pythonanywhere.com`

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

## Line Endings
All expressions end with a semicolon `;`.

## Core Data Types

|Data Type|Examples|
|---|---|
|Number|1, 2, 3, 10, 13, 100, 1234567890, 1.1, 2.5, 3.14159|
|String|"Hello, world!", "1234567890"|
|Boolean|true, false|
|List|(), (1,), (1, "hello, world!"), (1, "hello, world!", true)|

## Operators

### Binary Operators
Operators that appear between two expressions.

|Operator Name|Literal|
|---|---|
|Add|+|
|Subtract|-|
|Multiply|*|
|Divide|/|
|Assignment|=|
|Pointer|<-|
|Equals|==|
|Not Equals|!=|
|Or|\||
|And|&|
|Less Than|<|
|Less Than or Equal|<=|
|Greater Than|>|
|Greater Than or Equal|>=|

### Unary Operators
Operators that appear before an expression

|Operator Name|Literal|
|---|---|
|Negate|-|
|Absolute Value|+|
|Boolean Opposite (Not)|!|

### Suffix Operators
Operators that appear after an expression

|Operator Name|Literal|
|---|---|
|Factorial|!|

## Expressions

### Variable Assignment and Reassignment
```
number = 10;
float = 3.14;
```

### Math Expressions
```
1 + 1;
1 + 2 + 3 + 4;
5 - 3;
6 * 4;
10 / 2;
3 + (10 - 9 - 8);
-3;
-(5 + 4 + 3 + 2 + 1);
+6;
```

### Builtin Functions
|Name|Description|
|----|-----------|
|print|output data to output stream|

### Functions
Boomerang has first-class functions, meaning they are treated like any other type of data (number, boolean, string, etc.). They are defined by being assigned to variables.

The syntax for functions is very similar to lambda expressions in Python, except Boomerang uses `func` instead of `lambda`, starting with the `func` keyword, followed by a comma-separated list parameters, a colon, and an expression. Be aware that functions only have one expression for the body, and the result of that expression is returned by the function. Below are some examples:
```
add = func a, b: a + b;

negative = func n: -n;

greeting = func: print <- ("hello, world!",);
```

Use the Send (`<-`) operator to call functions:
```
add <- (1, 2);
negative <- (1,);
greeting <- ();
```

### When Expressions
When expressions are a hybrid of `if-else` and `switch` statements in other languages. Unlike many other languages, though, `when` expressions are expressions and return a value.

Below is an example of the `if-else` implementation:
```
a = 5;
when:
   a == 1: "1"
   a == 2: "2"
   a == 3: "3"
   a == 4: "4"
   else: "0";
```

For the `switch` implementation, an expression comes after `when` and each case starts with the `is` keyword.
```
a = 3;
when a:
   is 1: "1"
   is 2: "2"
   is 3: "3"
   is 4: "4"
   else: "0";
```

Note the `else` at the end of both. This handles the default case (when none of the above cases match or return true) and is required.
