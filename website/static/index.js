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