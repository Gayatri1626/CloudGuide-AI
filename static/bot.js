const chatbotToggle = document.getElementById('chatbot-toggle');
const chatContainer = document.getElementById('chat-container');
const helperText = document.getElementById('chatbot-helper-text');
const voiceButton = document.getElementById('voice-btn');
const typingIndicator = document.getElementById('typing-indicator');
const resetButton = document.getElementById('reset-conversation');
const messagesContainer = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');

// Store conversation history in localStorage
function saveConversation(messages) {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

function loadConversation() {
    const savedHistory = localStorage.getItem('chatHistory');
    return savedHistory ? JSON.parse(savedHistory) : [];
}

function clearConversation() {
    localStorage.removeItem('chatHistory');
    messagesContainer.innerHTML = ''; // Clear messages
    appendMessage("Conversation reset. How can I help you today?");
}

// Display helper text on page load
window.onload = () => {
    helperText.style.opacity = '1';
    setTimeout(() => {
        helperText.style.opacity = '0';
    }, 3000);

    // Load conversation history
    const savedMessages = loadConversation();
    savedMessages.forEach(msg => {
        appendMessage(msg.text, msg.isUser);
    });
};

// Toggle Chatbot Visibility
chatbotToggle.addEventListener('click', () => {
    const isCardVisible = chatContainer.style.display === 'flex';
    chatContainer.style.display = isCardVisible ? 'none' : 'flex';
});

// Reset Conversation
resetButton.addEventListener('click', clearConversation);

function sendMessage(message = null) {
    const userInput = document.getElementById('user-input');
    
    // If no message passed, use input field
    const messageToSend = message || userInput.value.trim();

    if (messageToSend) {
        // Clear input if using input field
        if (!message) {
            userInput.value = '';
        }

        appendMessage(messageToSend, true);
        
        // Show typing indicator
        typingIndicator.style.display = 'flex';

        fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: messageToSend
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            const botResponse = data.response;
            
            // Determine when to show buttons
            if (botResponse.toLowerCase().includes('would you like assistance today?')) {
                appendMessage(botResponse, false, 'initial');
            } else if (botResponse.toLowerCase().includes('are you done')) {
                appendMessage(botResponse, false, 'step');
            } else {
                appendMessage(botResponse);
            }
        })
        .catch(error => {
            appendMessage("Error: Unable to connect to the server.");
            typingIndicator.style.display = 'none';
        });
    }
}


function appendMessage(message, isUser = false, showButtons = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = message;

    messageDiv.appendChild(contentDiv);

    // Add quick action buttons if specified
    if (showButtons) {
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'quick-actions';
        
        if (showButtons === 'initial') {
            // Yes/No buttons for initial conversation
            const yesBtn = document.createElement('button');
            yesBtn.textContent = 'Yes';
            yesBtn.className = 'quick-action-btn';
            yesBtn.onclick = () => sendMessage('yes');

            const noBtn = document.createElement('button');
            noBtn.textContent = 'No';
            noBtn.className = 'quick-action-btn';
            noBtn.onclick = () => sendMessage('no');

            buttonsContainer.appendChild(yesBtn);
            buttonsContainer.appendChild(noBtn);
        } else if (showButtons === 'step') {
            // Done/Help buttons for step progression
            const doneBtn = document.createElement('button');
            doneBtn.textContent = 'Done';
            doneBtn.className = 'quick-action-btn';
            doneBtn.onclick = () => sendMessage('done');

            const helpBtn = document.createElement('button');
            helpBtn.textContent = 'Help';
            helpBtn.className = 'quick-action-btn';
            helpBtn.onclick = () => sendMessage('help');

            buttonsContainer.appendChild(doneBtn);
            buttonsContainer.appendChild(helpBtn);
        }

        messageDiv.appendChild(buttonsContainer);
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Save to conversation history
    const savedMessages = loadConversation();
    savedMessages.push({ text: message, isUser });
    saveConversation(savedMessages);
}

// Enable Speech-to-Text (STT) with Web Speech API
voiceButton.addEventListener('click', () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
        voiceButton.textContent = '🛑';
        appendMessage("Listening...", true);
    };

    recognition.onend = () => {
        voiceButton.textContent = '🎤';
    };

    recognition.onresult = (event) => {
        const spokenText = event.results[0][0].transcript;
        userInput.value = spokenText;
        sendMessage();
    };

    recognition.onerror = (event) => {
        appendMessage("Error in speech recognition: " + event.error, true);
        voiceButton.textContent = '🎤';
    };

    recognition.start();
});

// Allow sending message with Enter key
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});