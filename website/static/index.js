function displayFlashMessages() {
    var flashMessages = document.querySelectorAll(".flash-message");
    if (flashMessages && flashMessages.length > 0) {
        flashMessages.forEach(function(messageElement) {
            var category = messageElement.getAttribute("data-category");
            var content = messageElement.textContent;
            alert("Category: " + category + "\nContent: " + content);
        });
    }
}


let selectedDVRPSet = null;


function selectDVRPSet(dvrpId) {
    selectedDVRPSet = dvrpId;
    document.getElementById('loadPointsBtn').disabled = false;
}


document.addEventListener('DOMContentLoaded', function() {
    displayFlashMessages();
    document.getElementById('loadPointsBtn').addEventListener('click', function() {
        if (selectedDVRPSet !== null) {
            fetch(`/plot-table?dvrpId=${selectedDVRPSet}`)
                .then(response => response.json())
                .then(data => {
                    Plotly.newPlot('plotly-table', data['data'], data['layout']);
                })
                .catch(error => console.error('Error loading plot data:', error));
            
            fetch(`/map-data?dvrpId=${selectedDVRPSet}`)
                .then(response => response.json())
                .then(data => {
                    Plotly.newPlot('plotly-map-container', data.data, data.layout, {responsive: true});
                })
                .catch(error => console.error('Error loading map data:', error));
        }
    });
});