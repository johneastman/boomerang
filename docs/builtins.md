# Builtin Functions
Functions that are built into the language.

## print
Send data to the output stream (e.g., print to console). Returns the list of values passed to `print`.

|Arguments|Return Value|
|---|---|
|`(v1:Any, v2:Any, ..., vn:Any)`|Print all values on same line separated by commas.|

## randint
Return a random whole (integer) number between two whole (integer) numbers.

|Arguments|Return Value|
|---|---|
|`(end:Number,)`|Return random number between 0 and `end`.|
|`(start:Number, end:Number)`|Return random number between `start` and `end`.|

## randfloat
Return a random decimal (float) number between two decimal (float) or whole (integer) numbers.

|Arguments|Return Value|
|---|---|
|`()`|Return random number between 0 and 1.|
|`(end:Number,)`|Return random number between 0 and `end`.|
|`(start:Number, end:Number)`|Return random number between `start` and `end`.|

## len
Return the length of a sequence.

|Arguments|Return Value|
|---|---|
|`(sequence:List\|String,)`|For lists, return the number of elements. For strings, return the number of characters.|

## range
Return a list of values from `start` to `end` (exclusive).

|Arguments|Return Value|
|---|---|
|`(start:Number)`|List of numbers from 0 to `start`.|
|`(start:Number, end:Number,)`|List of numbers from `start` to `end`.|
|`(start:Number, end:Number, step:Number)`|Return a list of numbers from `start` to `end` incrementing by `step`. If `step` is negative, the list will generate in descending order, but `start` will need to be greater than `end`.|

# round
Round a decimal (floating-point) number to a certain number of digits after the decimal place.

|Arguments|Return Value|
|---|---|
|`(number:Number, round_to:Number)`|Round `number`, a floating-point value, to `round_to` digits after the decimal place.|

# input
Accept input from the user. Returns a `String` value.

|Arguments|Return Value|
|---|---|
|`(prompt:String,)`|Prompt displayed to the user when accepting user input.|

# format
Create formatted strings.

|Arguments|Return Value|
|---|---|
|`(s: String)`|Return `s`.|
|`(s: String, ...args: Any)`|Replace placeholder values in `s` with values in `args`. Placeholders are a dollar sign followed by an integer (e.g., `$0`, `$1`, etc.). The integer corresponds to the position of a value in `args` (for example, `$0` refers to the first value in `args`, `$1` refers to the second value in `args`, etc.).|

# is_whole_number
Checks if a number is a whole number or not. Returns `Boolean` value.

|Arguments|Return Value|
|---|---|
|`(n: Number)`|Any number value.|
