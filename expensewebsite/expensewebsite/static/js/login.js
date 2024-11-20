document.addEventListener("DOMContentLoaded", function () {
    const usernameField = document.getElementById("usernameField");
    const passwordField = document.getElementById("passwordField");
    const form = document.getElementById("loginForm");
    const togglePassword = document.querySelector(".showPasswordToggle");

    // Password visibility toggle
    togglePassword.addEventListener("click", function () {
        if (passwordField.type === "password") {
            passwordField.type = "text";
            togglePassword.textContent = "Hide";
        } else {
            passwordField.type = "password";
            togglePassword.textContent = "Show";
        }
    });

    // Form validation on submit
    form.addEventListener("submit", function (event) {
        // Clear previous feedback
        document.querySelectorAll(".invalid-feedback").forEach((el) => (el.style.display = "none"));

        let isValid = true;

        // Check if the username field is empty
        if (!usernameField.value.trim()) {
            const usernameFeedback = usernameField.nextElementSibling;
            usernameFeedback.style.display = "block";
            usernameFeedback.textContent = "Username is required.";
            isValid = false;
        }

        // Check if the password field is empty
        if (!passwordField.value.trim()) {
            const passwordFeedback = passwordField.parentElement.querySelector(".invalid-feedback");
            passwordFeedback.style.display = "block";
            passwordFeedback.textContent = "Password is required.";
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault(); // Prevent form submission if invalid
        }
    });
});
