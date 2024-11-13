// Selecting Elements
const usernameField = document.querySelector("#usernameField");
const feedbackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedbackArea = document.querySelector(".EmailfeedbackArea");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const passwordInput = document.querySelector("#passwordField");
const submit_btn = document.querySelector('.submit-btn')
// Debounce function to reduce validation calls
function debounce(func, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

// Toggle password visibility
function togglePasswordVisibility() {
  const isPasswordVisible = passwordInput.type === "password";
  passwordInput.type = isPasswordVisible ? "text" : "password";
  showPasswordToggle.textContent = isPasswordVisible ? "Hide" : "Show";
}

showPasswordToggle.addEventListener("click", togglePasswordVisibility);

// Validate username
async function validateUsername() {
  const usernameVal = usernameField.value.trim();
  usernameSuccessOutput.style.display = 'block';
  usernameSuccessOutput.textContent = `Checking ${usernameVal}`;
  feedbackArea.style.display = 'none';
  usernameField.setAttribute("aria-busy", "true");

  try {
    const res = await fetch("/authentication/validate-username", {
      body: JSON.stringify({ username: usernameVal }),
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const data = await res.json();
    usernameSuccessOutput.style.display = 'none';
    usernameField.setAttribute("aria-busy", "false");

    if (data.error) {
      usernameField.classList.add('is-invalid');
      feedbackArea.style.display = 'block';
      feedbackArea.innerText = data.error;
      feedbackArea.setAttribute("role", "alert");
      submit_btn.disabled = true;
    } else {
      usernameField.classList.remove("is-invalid");
      feedbackArea.style.display = "none";
      submit_btn.removeAttribute("disabled");
    }
  } catch (error) {
    feedbackArea.style.display = 'block';
    feedbackArea.innerText = 'An error occurred. Please try again.';
    feedbackArea.setAttribute("role", "alert");
    usernameField.setAttribute("aria-busy", "false");
  }
}

// Validate email
async function validateEmail() {
  const emailVal = emailField.value.trim();
  emailFeedbackArea.style.display = 'none';
  emailField.setAttribute("aria-busy", "true");

  try {
    const res = await fetch("/authentication/validate-email", {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const data = await res.json();
    emailField.setAttribute("aria-busy", "false");

    if (data.error) {
      submit_btn.disabled = true;
      emailField.classList.add('is-invalid');
      emailFeedbackArea.style.display = 'block';
      emailFeedbackArea.innerText = data.error;
      emailFeedbackArea.setAttribute("role", "alert");
    } else {
      submit_btn.removeAttribute('disabled');
      emailField.classList.remove("is-invalid");
      emailFeedbackArea.style.display = "none";
    }
  } catch (error) {
    emailFeedbackArea.style.display = 'block';
    emailFeedbackArea.innerText = 'An error occurred. Please try again.';
    emailFeedbackArea.setAttribute("role", "alert");
    emailField.setAttribute("aria-busy", "false");
  }
}

// Event Listeners with Debounce
usernameField.addEventListener("input", debounce(validateUsername));
emailField.addEventListener("input", debounce(validateEmail));
