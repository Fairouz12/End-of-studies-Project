// chatbot.js

// This function fetches the content of the /TTBOT page and injects it into the home page
function loadChatbot() {
    // Make a GET request to the /TTBOT route
    fetch('/TTBOT')
      .then(response => response.text()) // Parse the response as text
      .then(html => {
        // Create a new div element
        const chatbotDiv = document.createElement('div');
        chatbotDiv.innerHTML = html; // Set the inner HTML of the div to the fetched HTML
        // Find the chatbot container div in the home page
        const chatbotContainer = document.getElementById('chatbot-container');
        // Append the chatbot div to the container
        chatbotContainer.appendChild(chatbotDiv);
      });
  }
  
  // Load the chatbot when the home page is loaded
  document.addEventListener('DOMContentLoaded', loadChatbot);
  