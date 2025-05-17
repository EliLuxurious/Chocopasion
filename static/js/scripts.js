document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password");
    const bunnyImg = document.getElementById("bunny-img");
  
    passwordInput.addEventListener("focus", () => {
      bunnyImg.src = "/static/img/bunny-covered.png"; // Conejo tapándose los ojos
    });
  
    passwordInput.addEventListener("blur", () => {
      bunnyImg.src = "/static/img/bunny-open.png"; // Conejo normal
    });
  });
  