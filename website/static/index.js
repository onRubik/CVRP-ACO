function displayFlashMessage() {
  var flashMessages = {{ get_flashed_messages(with_categories=true) | tojson | safe }};
  
  if (flashMessages.length > 0) {
      flashMessages.forEach(function(message) {
          var category = message[0];
          var content = message[1];
          
          if (category === "error") {
              // Display an alert for error messages
              alert(content);
          } else if (category === "success") {
              // Display a success message (you can customize the styling)
              // Replace this with your preferred way of displaying success messages
              alert("Success: " + content);
          } else if (category === "info") {
              // Display an info message (you can customize the styling)
              // Replace this with your preferred way of displaying info messages
              alert("Info: " + content);
          }
          
          // You can add more conditions for other categories if needed
      });
  }
}