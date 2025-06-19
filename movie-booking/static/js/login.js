// Login Modal
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    document.getElementById('loginError').innerText = '';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

// Sign Up Modal
function openSignupModal() {
    document.getElementById('signupModal').style.display = 'block';
    document.getElementById('signupError').innerText = '';
}

function closeSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
}

function switchToSignup() {
    closeLoginModal();
    openSignupModal();
}

function switchToLogin() {
    closeSignupModal();
    openLoginModal();
}

// Login Form Submission
document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/ajax-login', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                document.getElementById('loginError').innerText = data.message;
            }
        });
});

// Sign Up Form Submission
document.getElementById('signupForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');

    if (password !== confirmPassword) {
        document.getElementById('signupError').innerText = 'Passwords do not match';
        return;
    }

    fetch('/ajax-register', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                document.getElementById('signupError').innerText = data.message;
            }
        });
});

// Close modal when clicking outside
window.onclick = function (event) {
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');

    if (event.target == loginModal) closeLoginModal();
    if (event.target == signupModal) closeSignupModal();
}


// forgot password modal 
function openForgotPasswordModal() {
    document.getElementById('forgotPasswordModal').style.display = 'block';
    document.getElementById('forgotPasswordMessage').innerText = '';
}

function closeForgotPasswordModal() {
    document.getElementById('forgotPasswordModal').style.display = 'none';
}

// Optional: Close modal if user clicks outside the box
window.onclick = function (event) {
    const modal = document.getElementById('forgotPasswordModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Actual AJAX request for forgot password
document.getElementById('forgotPasswordForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/forgot_password', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('forgotPasswordMessage').innerText = data.message;
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('forgotPasswordMessage').innerText = 'Something went wrong.';
        });
});

