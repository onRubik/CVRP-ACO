function displayFlashMessages() {
    var post_request = sessionStorage.getItem("post_request");
    
    if (!post_request) {
        var flashMessages = document.querySelectorAll(".flash-message");
        if (flashMessages && flashMessages.length > 0) {
            flashMessages.forEach(function (messageElement) {
                var category = messageElement.getAttribute("data-category");
                var content = messageElement.textContent;

                alert("Category: " + category + "\nContent: " + content);

                sessionStorage.setItem("post_request", true);
            });
        }
    }
}

displayFlashMessages();