document.addEventListener('DOMContentLoaded', () => {
  const alertTrigger = document.getElementById('liveAlertBtn');

  if (alertTrigger) {
    alertTrigger.addEventListener('click', async () => {
      const email = document.getElementById('floatingInput').value;
      const password = document.getElementById('floatingPassword').value;

      if (email !== '' && password !== '') {
        const response = await fetch('/login', {
          method: 'POST',
          body: new URLSearchParams({ 'floatingInput': email, 'floatingPassword': password }),
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        if (response.ok) {
          try {
            const result = await response.json();
            if (result.message && result.type) {
              alert(result.message);
              window.location.href = '/login';
              if (result.type === 'success') {
                window.location.href = '/home';
              }
            } else {
              alert('Invalid response from the server.');
            }
          } catch (error) {
            alert('Error processing response.');
          }
        } else {
          alert('Failed to log in');
        }
      } else {
        alert('Please fill in both email and password fields.');
      }
    });
  }
});

// You can check and use the errorMessage variable here if needed
if (typeof errorMessage !== 'undefined' && errorMessage !== null) {
  alert(errorMessage);
  // You can redirect as needed here
  // window.location.href = '/desired_location';
}
