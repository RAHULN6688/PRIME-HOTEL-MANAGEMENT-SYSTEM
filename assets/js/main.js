

// Handle form submission (assuming you are using AJAX)
$('#login-in').submit(function (e) {
    e.preventDefault();

    // ... (your existing code to collect username and password)

    $.ajax({
        type: 'POST',
        url: '/login.html',
        data: JSON.stringify({ 'username': username, 'password': password }),
        contentType: 'application/json',
        success: function (response) {
            if (response.success) {
                // Redirect to the customer page
                window.location.href = response.redirect;
            } else {
                // Handle unsuccessful login
                alert('Login failed: ' + data.message);
                alert(response.message);
            }
        },
        error: function (error) {
            console.log('Error:', error);
        }
    });
});

// ...



