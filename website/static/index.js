function displayFlashMessages() {
    
    var flashMessages = document.querySelectorAll(".flash-message");
    if (flashMessages && flashMessages.length > 0) {
        flashMessages.forEach(function (messageElement) {
            var category = messageElement.getAttribute("data-category");
            var content = messageElement.textContent;

            alert("Category: " + category + "\nContent: " + content);

        });
    }
}

displayFlashMessages();

document.addEventListener('DOMContentLoaded', function() {
    fetch('/plot-table')
    .then(response => response.json())
    .then(data => {
        console.log('Plot data:', data['data']);
        Plotly.newPlot('plotly-table', data['data'], data['layout']);
        // var data = [{
        //     type: 'table',
        //     header: {
        //       values: [["Column A"], ["Column B"]],
        //       align: "center",
        //       line: {width: 1, color: 'black'},
        //       fill: {color: "grey"},
        //       font: {family: "Arial", size: 12, color: "white"}
        //     },
        //     cells: {
        //       values: [
        //         ["A1", "A2"], // Column A values
        //         ["B1", "B2"], // Column B values
        //       ],
        //       align: "center",
        //       line: {color: "black", width: 1},
        //       fill: {color: ["yellow", "white"]},
        //       font: {family: "Arial", size: 11, color: ["black"]}
        //     }
        //   }];
          
        //   Plotly.newPlot('plotly-table', data);
    })
    .catch(error => console.error('Error loading plot data:', error));
});