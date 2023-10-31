CodeMirror.defineMode("boomerang", function() {
    return {
        token: function(stream,state) {
            if (stream.match(/\b(func|when|is|else|true|false|for|in|and|or|xor|not|if)\b/)) {
                return "keywords";
            } else if (stream.match(/\".*?\"/)) {
                return "strings";
            } else if (stream.match(/\b(print|len|randint|randfloat|range|round|input|format|is_whole_number)\b/)) {
                return "builtins";
            } else if (stream.match(/[0-9]+(.?[0-9]+)*/)) {
                return "numbers";
            }
            stream.next();
            return null;
        }
    };
});

let myTextarea = document.getElementById("code-editor");
let editor = CodeMirror.fromTextArea(myTextarea, {
    mode: "boomerang",
    lineNumbers: true
});
