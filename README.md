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

1. Generate a `.env` file with `SECRET_KEY` key using the following Python script:
   ```python
    import secrets

    key = secrets.token_hex()
    with open(".env", "w") as file:
        file.write(f"export SECRET_KEY={key}")
   ```
2. Run the app with `python flask_app.py`.

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

### Prefix Operators and Operations
|Operator Symbol|Right Type|Result Type|Result Description|
|---|---|---|---|
|`-`|Number|Number|Make number negative.|
|`-`|List|List|Reverse list.|
|`+`|Number|Number|Absolute value. Make number positive.|
|`!`|Boolean|Boolean|Not operator. Return opposite boolean value (`true` becomes `false` and `false` becomes `true`).|
|`**`|List|List|Create a new 1-element list, where the first and only element is the given list (list of lists).|

### Infix Operators and Operations
|Left Type|Operator Symbol|Right Type|Result Type|Result Description|
|---|---|---|---|---|
|Identifier|`=`|Any|Any|Assign right value to variable on right. Return value of variable.|
|Any|`==`|Any|Boolean|Return `true` if both values are equal; `false` otherwise.|
|Any|`!=`|Any|Boolean|Return `false` if both values are equal; `true` otherwise.|
|Number|`+`|Number|Number|Add right number to left number.|
|String|`+`|String|String|Combine both strings into one new string.|
|List|`+`|List|List|Combine both lists into one new list.|
|Number|`-`|Number|Number|Subtract right number from left number.|
|List|`-`|List|List|Filter lists by value. Return a new list where values in the right list are removed from the left list.|
|Number|`*`|Number|Number|Multiply left number by right number.|
|Number|`/`|Number|Number|Divide left number by right number.|
|List|`@`|Number|Any|Get the value in the list at the given index position (e.g., index == 0 is the first element, index == 1 is the second element, index == 2 is the second element, etc.).|
|Number|`>`|Number|Boolean|Return `true` if the left value is greater than the right value; `false` otherwise.|
|Number|`>=`|Number|Boolean|Return `true` if the left value is greater than or equal to the right value; `false` otherwise.|
|Number|`<`|Number|Boolean|Return `true` if the left value is less than the right value; `false` otherwise.|
|Number|`<=`|Number|Boolean|Return `true` if the left value is less than or equal to the right value; `false` otherwise.|
|Number|`%`|Number|Number|Modulus. Divide the left value by the right value and return the remainder as a whole number.|
|Boolean|`&`|Boolean|Boolean|Return `true` if left and right are `true`; `false` otherwise.|
|Boolean|`\|`|Boolean|Boolean|Return `true` if left is `true` or right is `true`; `false` if both left and right are `false`.|
|List|`<-`|Any|List|Append the value on the right to the end of the list on the left. Return a new list.|
|Function|`<-`|List|Any|Call function on left with parameters on right.|

### Postfix Operators and Operations
|Left Type|Operator Symbol|Result Type|Result Description|
|---|---|---|---|
|Number|`--`|Number|Decrement number by 1. Return a new number.|
|Number|`++`|Number|Increment number by 1. Return a new number.|
|Number|`!`|Number|Factorial. Iteratively multiply values from 1 to left.|

## Expressions

### Variable Assignment and Reassignment
```
number = 10;
float = 3.14;
string = "hello, world!";
boolean = true;
list = (1, 2, 3, 4);
function = func a, b: a + b;
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

#### print
Send data to the output stream (e.g., print to console). Returns the list of values passed to `print`.

|Arguments|Return Value|
|---|---|
|`(v1:Any, v2:Any, ..., vn:Any)`|Print all values on same line separated by commas.|

#### random
Return a random number.

|Arguments|Return Value|
|---|---|
|`()`|Return random number between 0 and 1.|
|`(end:Number,)`|Return random number between 0 and `end`.|
|`(start:Number, end:Number)`|Return random number between `start` and `end`.|

#### len
Return the length of a sequence.

|Arguments|Return Value|
|---|---|
|`(sequence:List\|String,)`|For lists, return the number of elements. For strings, return the number of characters.|

#### range
Return a list of values from `start` to `end` (exclusive).

|Arguments|Return Value|
|---|---|
|`(start:Number)`|List of numbers from 0 to `start`.|
|`(start:Number, end:Number,)`|List of numbers from `start` to `end`.|
|`(start:Number, end:Number, step:Number)`|Return a list of numbers from `start` to `end` incrementing by `step`. If `step` is negative, the list will generate in descending order, but `start` will need to be greater than `end`.|

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
