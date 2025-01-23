# CloudGuide AI Chatbot

CloudGuide AI is an interactive voice-enabled chatbot designed to assist users with IBM Cloud services. It supports text and voice input, and it responds with text and speech for a seamless user experience.

## Features

- **Text Input:** Users can type queries and receive responses in the chat interface.
- **Voice Input:** Users can speak their queries, and the chatbot processes them using the Web Speech API.
- **Speech Response:** The chatbot uses IBM Watson Text-to-Speech to generate audio responses.
- **Interactive UI:** A floating chatbot button, intuitive design, and seamless toggle between voice and text input.

---

## Technologies Used

### Backend
- **Python (Flask):** For handling user queries, maintaining conversation states, and managing chatbot logic.
- **IBM Watson Text-to-Speech:** Converts text responses to speech.
- **Speech Recognition:** Processes user voice inputs.

### Frontend
- **HTML/CSS/JavaScript:** Creates an interactive and responsive user interface.
- **Web Speech API:** Converts voice input to text for processing by the chatbot.
- **Bootstrap 5.3.0:** Provides a modern, responsive design.


## Installation and Setup

### Prerequisites
1. Python 3.7 or later
2. Pip (Python package manager)
3. IBM Cloud account for accessing Watson services

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/CloudGuide-AI.git
   cd CloudGuide-AI
