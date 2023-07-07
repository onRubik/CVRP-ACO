"use strict";

let to_array = [];
let myChart;

function loadFile(event) {
  const csvfile = event.target.files[0];

  if (csvfile) {
    var ta_original = document.getElementById("original");
    var only_zeros = true;
    var reader = new FileReader();

    reader.onloadstart = function () {
      ta_original.value = "";
    };

    reader.onload = function () {
      var lines = reader.result.split(reader.result.indexOf("\r") > 0 ? "\r\n" : "\n");
      var delim = lines[0].indexOf(",") == -1 ? " " : ",";

      document.getElementById("head-text-div").innerHTML = lines[0];

      var matrix = new Array(lines.length - 1);

      for (var row = 1; row < lines.length; row++) {
        var values = lines[row].split(delim);

        matrix[row - 1] = new Array(values.length);
        for (var col = 0; col < values.length; col++) {
          matrix[row - 1][col] = parseInt(values[col]);
          ta_original.value += values[col];
          ta_original.value += col + 1 < values.length ? delim : "";

          if (only_zeros && matrix[row - 1][col] != 0) {
            only_zeros = false;
          }
        }
        ta_original.value += row + 1 < lines.length ? "\n" : "";
      }
    };

    reader.onloadend = function () {
      if (reader.error) {
        alert("The file was not loaded successfully");
        console.error("Unsuccessful load of " + csvfile.name + ": " + reader.error.message);
      } else {
        to_array = ta_original.value.split("\n");
        for (var i = 0; i < to_array.length; i++) {
          to_array[i] = to_array[i].split(",");
        }
        to_array.pop();
        var html = ta_original.value.replace(/\n/g, "<br>");
        document.getElementById("text-div").innerHTML = html;

        var hidden = document.getElementsByClassName("csv-details");
        if (hidden.length > 0) {
          hidden[0].className = "";
        }
        startChart(to_array);
      }
    };

    reader.onerror = function () {
      console.error("Error while loading " + csvfile.name + ": " + reader.error.message);
    };

    reader.readAsText(csvfile);
  } else {
    alert("Unexpected error");
  }
}

function startChart(fileContent) {
  const xValues = [];
  const yValues = [];

  for (let i = 0; i < fileContent.length; i++) {
    xValues.push(fileContent[i][0]);
    yValues.push(fileContent[i][1]);
  }

  const chartConfig = {
    type: "line",
    data: {
      datasets: [
        {
          label: "XY Data",
          data: xValues.map((x, i) => ({ x: x, y: yValues[i] })),
          borderColor: "#ffeecc",
          backgroundColor: "#ffeecc",
          pointRadius: 5,
          pointBackgroundColor: "#ffcc99",
          lineTension: 0.2,
          fill: false,
        },
      ],
    },
    options: {
      scales: {
        x: {
          type: "linear",
          position: "bottom",
        },
        y: {
          type: "linear",
          position: "left",
        },
      },
      aspectRatio: 1,
    },
  };

  const chartContainer = document.getElementById("chartContainer");
  const canvas = document.getElementById("myChart");

  if (myChart) {
    myChart.destroy();
  }

  myChart = new Chart(canvas.getContext("2d"), chartConfig);

  function updateChartSize() {
    const chartContainer = document.getElementById("chartContainer");
    const canvas = document.getElementById("myChart");
  
    const containerWidth = chartContainer.clientWidth;
    const containerHeight = containerWidth;
  
    canvas.width = containerWidth;
    canvas.height = containerHeight;
  
    myChart.resize();
  }

  window.addEventListener("resize", updateChartSize);
}