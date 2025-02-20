 // Function to get the CSRF token from the cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

    const csrfToken = getCookie('csrftoken'); // Get the CSRF token
 
 
    const usernameInput = document.getElementById('username-input');
    const feedbackElement = document.getElementById('username-feedback');
    const PasswordInput = document.getElementById('password');
    // const confirmPasswordInput = document.getElementById('password2');
    const passwordFeedbackElement = document.getElementById('password-feedback');
    // const confirmPasswordFeedbackElement = document.getElementById('confirm-password-feedback');
    const submitButton = document.getElementById('submit-button');

    // username validator
    if (usernameInput != null){
        usernameInput.addEventListener('input', function(event) {
            const username = event.target.value.trim();
    
            if (username === '') {
                feedbackElement.textContent = '';
                feedbackElement.style.color = ''; // Reset color
                submitButton.disabled = true; // Disable button if input is empty
                return;
            }
    
            fetch("{% url 'validate_user_password' %}", {  // Replace with your actual URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // Include CSRF token for security
                },
                body: JSON.stringify({ username: username }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    feedbackElement.textContent = data.success;
                    feedbackElement.style.color = 'green';
                    submitButton.disabled = false; // Enable button if username is valid
                } else if (data.detail) {
                    feedbackElement.textContent = data.detail;
                    feedbackElement.style.color = 'red';
                    submitButton.disabled = true; // Disable button if username is invalid
                }
            })
            .catch(error => {
                console.error('Error:', error);
                feedbackElement.textContent = 'An error occurred. Please try again.';
                feedbackElement.style.color = 'red';
                submitButton.disabled = true; // Disable button on error
            });
        });
    }

    // password validator
    PasswordInput.addEventListener('input', function(event) {
    const password = event.target.value.trim();

    if (password === '') {
        passwordFeedbackElement.textContent = '';
        passwordFeedbackElement.style.color = ''; // Reset color
        submitButton.disabled = false; // Disable button if input is empty
        return;
    }

    fetch("{% url 'validate_user_password' %}", {  // Replace with your actual URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  // Include CSRF token for security
        },
        body: JSON.stringify({ password: password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            passwordFeedbackElement.textContent = data.success;
            passwordFeedbackElement.style.color = 'green';
            submitButton.disabled = false; // Enable button if password is valid
        } else if (data.detail) {
            passwordFeedbackElement.textContent = data.detail; // Join multiple errors
            passwordFeedbackElement.style.color = 'red';
            submitButton.disabled = true; // Disable button if password is invalid
        }
    })
    .catch(error => {
        console.error('Error:', error);
        passwordFeedbackElement.textContent = 'An error occurred. Please try again.';
        passwordFeedbackElement.style.color = 'red';
        submitButton.disabled = true; // Disable button on error
    });
});
