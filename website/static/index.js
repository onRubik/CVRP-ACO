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
        Plotly.newPlot('plotly-table', data['data'], data['layout']);
    })
    .catch(error => console.error('Error loading plot data:', error));

    fetch('/map-data')
    .then(response => response.json())
    .then(data => {
        const fig = JSON.parse(data.fig);
        Plotly.newPlot('plotly-map-container', fig.data, fig.layout);
    })
    .catch(error => console.error('Error loading map data:', error));
});