
document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.has('reset_token')) {
        const token = params.get('reset_token');
        openResetModalFromToken(token);

        // Clean the URL after showing modal
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

function openResetModalFromToken(token) {
    fetch(`/reset_password/${token}`)
        .then(res => res.text())
        .then(html => {
            // Inject modal HTML if not already present
            let modalWrapper = document.getElementById('resetPasswordModalWrapper');
            if (!modalWrapper) {
                // Create and inject container
                modalWrapper = document.createElement('div');
                modalWrapper.id = 'resetPasswordModalWrapper';
                document.body.appendChild(modalWrapper);
            }

            modalWrapper.innerHTML = html;
            modalWrapper.style.display = 'block'; // Show modal

            const resetPasswordForm = document.getElementById('resetPasswordForm');
            const resetPasswordMessage = document.getElementById('resetPasswordMessage');
            const closeButton = modalWrapper.querySelector('.close-button');

            // Close button functionality
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    modalWrapper.style.display = 'none';
                });
            }

            if (resetPasswordForm) {
                resetPasswordForm.addEventListener('submit', function (e) {
                    e.preventDefault();

                    const newPassword = document.getElementById('newPassword').value.trim();
                    const confirmPassword = document.getElementById('confirmPassword').value.trim();

                    if (newPassword !== confirmPassword) {
                        resetPasswordMessage.innerText = "Passwords do not match.";
                        return;
                    }

                    const submitButton = resetPasswordForm.querySelector('button[type="submit"]');
                    submitButton.disabled = true;
                    resetPasswordMessage.innerText = 'Processing...';

                    const formData = new FormData();
                    formData.append('password', newPassword);
                    formData.append('confirm_password', confirmPassword); // important

                    fetch(`/reset_password/${token}`, {
                        method: 'POST',
                        body: formData
                    })
                        .then(res => res.json())
                        .then(data => {
                            resetPasswordMessage.innerText = data.message;
                            if (data.status === "success") {
                                setTimeout(() => {
                                    modalWrapper.style.display = 'none';
                                }, 2000);
                            } else {
                                submitButton.disabled = false;
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            resetPasswordMessage.innerText = 'Something went wrong.';
                            submitButton.disabled = false;
                        });
                });
            }
        })
        .catch(error => {
            console.error('Error fetching reset modal:', error);
        });
}
