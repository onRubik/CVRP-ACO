"use strict";

let to_array = [];

function loadFile (event) {
    var csvfile = event.target.files[0];

    if (csvfile) {
        var ta_original   = document.getElementById("original");
        var only_zeros    = true;
        var reader        = new FileReader();

        // Called after starting a read operation to initialize the textareas and the matrix
        reader.onloadstart = function () {
            ta_original.value   = "";
        }

        // Called when a read operation successfully completes. It separates the CSV headings
        // from the values and process them. Everything gets stored in the textareas and the matrix.
        reader.onload  = function () {
            var lines  = reader.result.split(reader.result.indexOf("\r") > 0 ? "\r\n" : "\n");
            var delim  = lines[0].indexOf(",") == -1 ? " " : ",";

            // Get & set the headings
            document.getElementById("head-text-div").innerHTML = lines[0];

            // Create a dynamic two-dimensional array (matrix) and store all values
            var matrix    = new Array(lines.length - 1);

            for (var row=1; row<lines.length; row++) {
                var values  = lines[row].split(delim);

                matrix[row-1] = new Array(values.length);
                for (var col=0; col<values.length; col++) {
                    matrix[row-1][col] = parseInt(values[col]);
                    ta_original.value += values[col];
                    ta_original.value += col+1 < values.length ? delim : "";

                    // There should be at least one number different than zero
                    if (only_zeros && matrix[row-1][col] != 0) {
                        only_zeros = false;
                    }
                }
                ta_original.value += row+1 < lines.length ? "\n" : "";
            }
        }

        // Called after a read completes (either successfully or unsuccessfully)
        reader.onloadend = function() {
            if (reader.error) {
                alert("The file was not loaded successfully. Please try again.");
                console.error("Unsuccessful load of " + csvfile.name + ": " + reader.error.message);
            }
            else {
                // Get the textarea's value and create the html content of the text-div
                // convert each row in the ta_original.value to an array, each row should be its own inner array inside the outer array
                // this array will be used to draw points and lines using p5js liibrary
                to_array = ta_original.value.split("\n");
                for (var i = 0; i < to_array.length; i++) {
                    to_array[i] = to_array[i].split(",");
                }
                // get rid of the last empty array
                to_array.pop();
                console.log(" to_array = " + typeof to_array)
                console.log(to_array)
                console.log(" ta_original.value = " + typeof ta_original.value)
                console.log(ta_original.value)
                var html = ta_original.value.replace(/\n/g,"<br>");
                document.getElementById("text-div").innerHTML = html;

                // Show the elements
                var hidden = document.getElementsByClassName("csv-details");
                if (hidden.length > 0) {
                    hidden[0].className = "";
                }
            }
        }

        // Called when there is an error during the load
        reader.onerror = function () {
            console.error("Error while loading " + csvfile.name + ": " + reader.error.message);
        }

        // Read from blob as a string and the result will be stored on this.result after the 'load' event fires
        reader.readAsText(csvfile);
    }
    else {
        alert("Oops! Something unexpected happened... Please try again.");
    }
}