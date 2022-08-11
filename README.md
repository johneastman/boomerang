# Boomerang
Boomerang is an interpreted language written in Python.

# Install
1. `pip install -r requirements.txt`
    * May need to run `python3 -m pip install -r requirements.txt`
2. Install [graphviz](https://graphviz.org/download/)
3. Optional: this project uses lefthook for pre-commit verification. Follow the installation and setup process [here](https://github.com/evilmartians/lefthook/blob/master/docs/full_guide.md)

# Running
Refer to `main.py` for an example of how to run the code. The language files end with the `ang` extension.

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
let variable = 3; # inline comment
/*
block comment
*/
```

## Statements

### Variable Assignment
```
let number = 10;
let float = 3.14;
let string = "hello, world!";
let boolean = true;
let dictionary = {"a": 1, "b": 2, "c": 3};
```

### While Loops
```
let i = 0;
while i < 10 {
   print(i);
   let i = i + 1;
}
```

### Functions
```
func add(a, b) {
   let result = a + b;
   return result;
}

let sum = add(3, 4);
print(sum);
```

### If Statements
```
let r = random();  # generates a random number between 0 and 1
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
