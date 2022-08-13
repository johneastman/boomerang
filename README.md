# Boomerang
Boomerang is an interpreted language written in Python.

# Install
1. Download and install [Python](https://www.python.org/downloads/)
2. `pip install -r requirements.txt`
    * May need to run `python3 -m pip install -r requirements.txt`
3. Install [graphviz](https://graphviz.org/download/)
4. Optional: this project uses lefthook for pre-commit verification. Follow the installation and setup process [here](https://github.com/evilmartians/lefthook/blob/master/docs/full_guide.md)

# Running
To run a Boomerang file:
`python3 main.py --path [PATH TO FILE]`

To run the repl:
`python3 main.py --repl`

**NOTE:** `python3` may not be how python files are run on your machine.

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
|Assignment: Add|+=|
|Assignment: Subtract|-=|
|Assignment: Multiply|*=|
|Assignment: Divide|/=|
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

## Comments
```
set variable = 3; # inline comment
/*
block comment
*/
```

## Statements

### Variable Assignment
```
set number = 10;
set float = 3.14;
set string = "hello, world!";
set boolean = true;
set dictionary = {"a": 1, "b": 2, "c": 3};
```

#### Operator Assignment
Unlike many languages, variable reassignment in Boomerang requires the `set` keyword.
```
set number = 1;
set number += 1;
set number -= 1;
set number *= 2
set number /= 1;

set dict = {"a": 1, "b": 2};
set dict["a"] += 1;
set dict["a"] -= 1;
set dict["a"] *= 2;
set dict["a"] /= 1;
```

### While Loops
```
set i = 0;
while i < 10 {
   print(i);
   set i = i + 1;
}
```

### Functions
```
func add(a, b) {
   set result = a + b;
   return result;
}

set sum = add(3, 4);
print(sum);
```

### If Statements
```
set r = random();  # generates a random number between 0 and 1
if r < 0.5 {
    print("r is less than 0.5");
} else {
    print("r is greater than or equal to 0.5");
}
```

## Expressions

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
5!;  # factorial. 5! = 120
```

### Boolean Expressions
```
!true;  # false
!false; # true

true && false;  # false
true || false;  # true
```

### Comparison Expressions
```
1 == 1;  # true
1 != 2;  # true
1 > 2;   # false
2 >= 1;  # true
2 < 1;   # true
1 <= 2;  # true

1 == 1 && 2 == 2;  # true
1 == 2 || 2 == 1;  # true
```
