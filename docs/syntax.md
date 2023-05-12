# Syntax

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
|`not`|Boolean|Boolean|Not operator. Return opposite boolean value (`true` becomes `false` and `false` becomes `true`).|
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
|List|`@`|Number|Any|Get the value in the list at the given index position (e.g., index == 0 is the first element, index == 1 is the second element, index == 2 is the second element, etc.). Negative indices are supported as well, so index == -1 gets the last element, index == -2 gets the second-to-last element, etc. The range of valid indices is `-len(self.values) <= index < len(self.values)`.|
|Number|`>`|Number|Boolean|Return `true` if the left value is greater than the right value; `false` otherwise.|
|Number|`>=`|Number|Boolean|Return `true` if the left value is greater than or equal to the right value; `false` otherwise.|
|Number|`<`|Number|Boolean|Return `true` if the left value is less than the right value; `false` otherwise.|
|Number|`<=`|Number|Boolean|Return `true` if the left value is less than or equal to the right value; `false` otherwise.|
|Number|`%`|Number|Number|Modulus. Divide the left value by the right value and return the remainder as a whole number.|
|Boolean|`and`|Boolean|Boolean|Return `true` if left and right are `true`; `false` otherwise.|
|Boolean|`or`|Boolean|Boolean|Return `true` if left is `true` or right is `true`; `false` if both left and right are `false`.|
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

### For Loops
For loops act like `map` in other languages. They return a new list where the expression is evaluated for each element in the original list. However, unlike `map`, the expression does not have to be applied to each element; any expression, including one that does not use the element variable, can be used.

Below are some examples:
```
for i in (1, 2, 3): i + 1;  # Returns: (2, 3, 4)
for i in range <- (10,): i % 2 == 0;  # Returns: (true, false, true, false, true, false, true, false, true, false)
for i in (1, 2, 3): "hello";  # Returns ("hello", "hello", "hello"). This ignores "i" entirely and returns its own thing
```
