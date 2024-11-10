const usernameField = document.querySelector("#usernameField");
const feedbackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const EmailfeedbackArea = document.querySelector(".EmailfeedbackArea");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");

// Debounce function to reduce validation calls
function debounce(func, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

// Validate username
usernameField.addEventListener("input", debounce((e) => {
  const usernameVal = e.target.value.trim();
  usernameSuccessOutput.style.display = 'block';
  usernameSuccessOutput.textContent = `Checking ${usernameVal}`;
  feedbackArea.style.display = 'none';

  fetch("/authentication/validate-username", {
    body: JSON.stringify({ username: usernameVal }),
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => res.json())
    .then((data) => {
      usernameSuccessOutput.style.display = 'none';
      if (data.error) {
        usernameField.classList.add('is-invalid');
        feedbackArea.style.display = 'block';
        feedbackArea.innerText = `${data.error}`;
      } else {
        usernameField.classList.remove("is-invalid");
        feedbackArea.style.display = "none";
      }
    })
    .catch(() => {
      feedbackArea.style.display = 'block';
      feedbackArea.innerText = 'An error occurred. Please try again.';
    });
}));

// Validate email
emailField.addEventListener("input", debounce((e) => {
  const emailVal = e.target.value.trim();
  EmailfeedbackArea.style.display = 'none';

  fetch("/authentication/validate-email", {
    body: JSON.stringify({ email: emailVal }),
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        emailField.classList.add('is-invalid');
        EmailfeedbackArea.style.display = 'block';
        EmailfeedbackArea.innerText = `${data.error}`;
      } else {
        emailField.classList.remove("is-invalid");
        EmailfeedbackArea.style.display = "none";
      }
    })
    .catch(() => {
      EmailfeedbackArea.style.display = 'block';
      EmailfeedbackArea.innerText = 'An error occurred. Please try again.';
    });
}));
