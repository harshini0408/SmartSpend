document.addEventListener("DOMContentLoaded", function() {
    let flashes = document.querySelectorAll(".flash");
    setTimeout(() => {
        flashes.forEach(flash => flash.style.display = "none");
    }, 3000);
});
