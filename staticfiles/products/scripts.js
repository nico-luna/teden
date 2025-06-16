// scripts.js - JS para el panel del vendedor

document.addEventListener("DOMContentLoaded", function () {
  const navLinks = document.querySelectorAll(".sidebar-seller .nav-link");

  navLinks.forEach(link => {
    link.addEventListener("click", () => {
      navLinks.forEach(el => el.classList.remove("active"));
      link.classList.add("active");
    });
  });

  console.log("Panel del vendedor activo 🛠️");
});
