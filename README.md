# Boomerang
Boomerang is an interpreted language written in Python.

Boomerang is:
* **Procedural:** commands are executed in the order they are defined.
* **Dynamically Typed:** variable, function, parameter, etc. types are not declared explicitly; rather, they are interpreted from the values they are assigned (e.g., `1` is an integer, `3.14159` is a float, `"hello world!"` is a string, etc.).
* **Strongly Typed:** strict rules for how different types interact (e.g. `1 + 1` or `1 + 1.5` are valid, but `1 + "hello world!"` is invalid).

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
```

#### Operator Assignment
Unlike many languages, variable assignment and reassignment requires the `set` keyword.
```
set number = 1;
set number += 1;
set number -= 1;
set number *= 2
set number /= 1;
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

### Trees
Boomerang features built-in tree objects. Each node can have `n` children, which means trees in Boomerang are n-ary trees. Nodes are expressions, edges are defined with `=>`, and child nodes fall between straight brackets (`[` and `]`). Place commas between expressions in brackets to denote multiple child nodes.

Be aware that the root node does not have brackets before it or after the proceeding tree. Tree structures expect an expression followed by the Pointer operator.
```
set list_tree = "list" => [
   "a",
   "b",
   1 + (2 + 2),
   "hello" + " " + "world!"
];
print(list_tree);  # "list" => ["a", "b", 5, "hello world!"]

set tree = "root" => [
    "parent_1" => [
        "child_1_1" => [
            "grandchild_1_1_1"
        ]
    ],
    "parent_2" => [
        "child_2_2"
    ],
    "parent_3"
];
print(tree);  # "root" => ["parent_1" => ["child_1_1" => ["grandchild_1_1_1"]], "parent_2" => ["child_2_2"], "parent_3"]
```
