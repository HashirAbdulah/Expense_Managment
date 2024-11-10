const usernameField = document.querySelector("#usernameField");
const feedbackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameField.classList.add('is-invalid');
    feedbackArea.style.display = 'block';
    feedbackArea.innerText = '';
      fetch("/authentication/validate-username", {
        body: JSON.stringify({ username: usernameVal }),
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            if(data.error){
              usernameField.classList.add('is-invalid');
              feedbackArea.style.display = 'block';
              feedbackArea.innerText = `${data.error}`;
            }else {
              usernameField.classList.remove("is-invalid");
              feedbackArea.style.display = "none";
            }
        });
  });

