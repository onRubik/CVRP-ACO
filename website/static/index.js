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
    var plotlyTableDiv = document.getElementById('plotly-table');
    var rawData = plotlyTableDiv.getAttribute('data-fig');
    console.log(rawData);

    if (rawData) {
        try {
            var figData = JSON.parse(rawData);
            Plotly.newPlot('plotly-table', figData.data, figData.layout);
        } catch (error) {
            console.error("Parsing error:", error, "Raw data:", rawData);
        }
    } else {
        console.error("No data found for Plotly table.");
    }
});


