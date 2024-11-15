// script.js

document.addEventListener("DOMContentLoaded", function () {
    const notification = document.getElementById("language-notification");
    const submitButton = document.getElementById("submit-language");

    // Check if the user has already selected a language
    if (!localStorage.getItem("preferredLanguage")) {
        // Show the notification
        notification.classList.remove("hidden");
    }

    // Handle language selection submission
    submitButton.onclick = function () {
        const selectedLanguage = document.getElementById("language").value;
        // Store the selected language in localStorage
        localStorage.setItem("preferredLanguage", selectedLanguage);
        // Hide the notification
        notification.classList.add("hidden");
        // You can load content based on the selected language here
        alert(`You selected: ${selectedLanguage}`); // Placeholder for language-specific content loading
    };
});

