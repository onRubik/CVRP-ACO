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

// Global variable to hold the selected DVRP set ID
let selectedDVRPSet = null;

function selectDVRPSet(dvrpId) {
    selectedDVRPSet = dvrpId;
    document.getElementById('loadPointsBtn').disabled = false; // Enable the "Load points" button
}

document.addEventListener('DOMContentLoaded', function() {
    displayFlashMessages();
    // Setup event listener for the "Load Points" button
    document.getElementById('loadPointsBtn').addEventListener('click', function() {
        if (selectedDVRPSet !== null) {
            // Fetch and display the table data
            fetch(`/plot-table?dvrpId=${selectedDVRPSet}`)
                .then(response => response.json())
                .then(data => {
                    Plotly.newPlot('plotly-table', data['data'], data['layout']);
                })
                .catch(error => console.error('Error loading plot data:', error));
            
            // Fetch and display the map data
            fetch(`/map-data?dvrpId=${selectedDVRPSet}`)
                .then(response => response.json())
                .then(data => {
                    // Ensure the Plotly map is correctly displayed with the data and layout provided by the backend
                    Plotly.newPlot('plotly-map-container', data.data, data.layout, {responsive: true});
                })
                .catch(error => console.error('Error loading map data:', error));
        }
    });
});



// function displayFlashMessages() {
//     var flashMessages = document.querySelectorAll(".flash-message");
//     if (flashMessages && flashMessages.length > 0) {
//         flashMessages.forEach(function (messageElement) {
//             var category = messageElement.getAttribute("data-category");
//             var content = messageElement.textContent;
//             alert("Category: " + category + "\nContent: " + content);
//         });
//     }
// }

// // Global variable to hold the selected DVRP set ID
// let selectedDVRPSet = null;

// function selectDVRPSet(dvrpId) {
//     selectedDVRPSet = dvrpId;
//     document.getElementById('loadPointsBtn').disabled = false; // Enable the "Load points" button
// }

// document.getElementById('loadPointsBtn').addEventListener('click', function() {
//     if (selectedDVRPSet !== null) {
//         fetch(`/plot-table?dvrpId=${selectedDVRPSet}`)
//         .then(response => response.json())
//         .then(data => {
//             Plotly.newPlot('plotly-table', data['data'], data['layout']);
//         })
//         .catch(error => console.error('Error loading plot data:', error));

//         // Additional fetch request for map data can be implemented here once the table functionality is confirmed
//     }
// });

// document.addEventListener('DOMContentLoaded', function() {
//     displayFlashMessages();
//     // Removed the immediate fetch calls to /plot-table and /map-data to rely on "Load Points" button click
// });
