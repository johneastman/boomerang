# Custom Interpreter in Python
This is a custom interpreted language written in Python.

# Install
1. `pip install -r requirements.txt`
    * May need to run `python3 -m pip install -r requirements.txt`
2. Install graphviz:
    * Mac: `brew install graphviz`
3. This project uses lefthook for pre-commit and pre-push verification. Follow the installation and setup process [here](https://github.com/evilmartians/lefthook/blob/master/docs/full_guide.md)

# Language Specs

## Data Types
|Data Type|Examples|
|---|---|
|INTEGER|1, 2, 3, 10, 13, 100, 1234567890|
|FLOAT|1.1, 2.5, 3.14159|
|STRING|"Hello, world!"|
|BOOLEAN|true, false|
|DICTIONARY|{"a": "b", 1: 2, true: false, 3.14: 0.159}|

## Operators
|Operator Name|Literal|
|---|---|
|Add|+|
|Subtract|-|
|Multiply|*|
|Divide|/|
|Assignment|=|
|Compare: Equal|==|
|Compare: Not Equal|!=|
|Compare: Greater than|>|
|Compare: Greater than or equal|>=|
|Compare: Less than|<|
|Compare: Less than or equal|<=|
|Unary: Not|!|
|Unary: Negative|-|
|Unary: Positive|+|
|Boolean AND|&&|
|Boolean OR| \|\| |
