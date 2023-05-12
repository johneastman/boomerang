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
