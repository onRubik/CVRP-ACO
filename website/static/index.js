const alertTrigger = document.getElementById('liveAlertBtn');

if (alertTrigger) {
  alertTrigger.addEventListener('click', async () => {
    const email = document.getElementById('floatingInput').value;
    const password = document.getElementById('floatingPassword').value;
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
          if (result.type === 'success') {
            // Redirect to the home page or perform other actions on success.
            window.location.href = '/home'; // Change to the appropriate URL.
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
  });
}
