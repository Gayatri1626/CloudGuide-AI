from flask import Flask, request, render_template, jsonify,Response
import json
import os
from pathlib import Path
from test import generate_audio_stream

app = Flask(__name__)

# Load all JSON files from the jsonfiles directory
def load_intents():
    intents_data = {"intents": []}
    json_folder = Path('jsonfiles')  # Use jsonfiles folder
    
    if not json_folder.exists():
        print("Warning: jsonfiles directory not found")
        return intents_data
        
    json_files = list(json_folder.glob('*.json'))
    
    for file in json_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if 'intents' in data:
                    intents_data['intents'].extend(data['intents'])
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")
    
    return intents_data

# Initialize conversation states
conversation_states = {}

def find_intent_by_key(intent_key):
    intents = load_intents()
    for intent in intents['intents']:
        if intent['intent'] == intent_key:
            return intent
    return None

def find_intent(user_input):
    """
    Matches the user input to an intent from the JSON file.
    
    Parameters:
        user_input (str): The user's input text.
    
    Returns:
        dict or None: The matched intent if found, otherwise None.
    """
    # Load intents from the JSON file
    intents = load_intents()
    
    for intent in intents['intents']:
        # Check if any trigger phrase matches the user input
        for phrase in intent.get('trigger_phrases', []):
            if phrase.lower() in user_input.lower():
                return intent

    return None


def get_step_response(intent, step_number):
    for step in intent.get('conversation_flow', []):
        if step['step'] == step_number:
            return {
                'message': step['chatbot'],
                'follow_up': step.get('follow_up', {})
            }
    return None


def handle_troubleshooting(intent, issue):
    if 'troubleshooting' in intent:
        for problem in intent['troubleshooting']:
            if issue.lower() in problem['issue'].lower():
                return problem['solution']
    return "I'm sorry, I couldn't find a solution for that specific issue."

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_input = data.get('message', '').lower()
    session_id = data.get('session_id', 'default')

    # Initialize session state if not exists
    if session_id not in conversation_states:
        conversation_states[session_id] = {
            'current_stage': 'init',
            'selected_service': None,
            'current_intent': None,
            'current_step': 1,
            'waiting_for_confirmation': False,
            'pending_switch': None
        }

    state = conversation_states[session_id]

    # Handle pending switch confirmation
    if state.get('pending_switch'):
        if 'yes' in user_input:
            state.update({
                'current_stage': 'intent_flow',
                'current_intent': state['pending_switch']['intent'],
                'current_step': 1,
                'waiting_for_confirmation': False,
                'pending_switch': None
            })
            response_text = f"Switching to {state['pending_switch']['intent']['intent']}. Let's begin:\n{state['current_intent']['conversation_flow'][0]['chatbot']}"
        elif 'no' in user_input:
            state['pending_switch'] = None
            response_text = "Got it! Continuing with the current process."
        else:
            response_text = "Would you like to switch to the new process? Please respond with Yes or No."
    else:
        # Regular chatbot flow
        if state['current_stage'] == 'init':
            if 'yes' in user_input:
                state['current_stage'] = 'category_selection'
                response_text = "Great! Here are the available categories:\n\n• Database Services\n• Compute Services\n• AI Services\n• Storage Services\n\nWhich category would you like to explore?"
            elif 'no' in user_input:
                response_text = "No problem! Let me know if you need help later."
            else:
                response_text = "Please respond with Yes or No."
        elif state['current_stage'] == 'category_selection':
            if 'database' in user_input:
                state['current_stage'] = 'service_selection'
                response_text = "Here are the available Database Services:\n\n• DB2\n• Cloudant\n• MongoDB\n\nWhich specific service would you like to work with?"
            else:
                response_text = "I couldn't identify the category. Please choose from Database, Compute, AI, or Storage Services."
        elif state['current_stage'] == 'service_selection':
            if 'db2' in user_input:
                state['current_stage'] = 'operation_selection'
                state['selected_service'] = 'DB2'
                response_text = "Would you like to create or scale a DB2 instance?"
            else:
                response_text = "Currently, I support DB2 operations. Let me know if you'd like to work with DB2."
        elif state['current_stage'] == 'operation_selection':
            if 'create' in user_input or 'scale' in user_input:
                intent_key = 'create_db2_instance' if 'create' in user_input else 'scale_db2_instance'
                intent = find_intent_by_key(intent_key)
                if intent:
                    state['current_intent'] = intent
                    state['current_stage'] = 'intent_flow'
                    state['current_step'] = 1
                    response_text = intent['conversation_flow'][0]['chatbot']
                else:
                    response_text = "I couldn't find steps for this operation. Please try again."
            else:
                response_text = "Would you like to create or scale a DB2 instance?"
        elif state['current_stage'] == 'intent_flow':
            if 'done' in user_input or 'yes' in user_input:
                state['current_step'] += 1
                step = get_step_response(state['current_intent'], state['current_step'])
                if step:
                    response_text = step['message']
                else:
                    state['current_stage'] = 'operation_completion'
                    response_text = "You've completed the process. Can I assist with anything else?"
            elif 'help' in user_input:
                step = get_step_response(state['current_intent'], state['current_step'])
                if step and step['follow_up']:
                    response_text = step['follow_up']['user_response']['help']['chatbot']
                else:
                    response_text = "I'm sorry, I couldn't find help for this step."
            else:
                response_text = "Please respond with 'yes', 'done', or 'help' to proceed."
        elif state['current_stage'] == 'operation_completion':
            response_text = "Process complete. Let me know if you need further assistance."
        else:
            response_text = "I didn't understand. Could you please rephrase?"

    # Generate speech response if requested
    is_speech_required = data.get("speech", False)
    audio_response = None

    if is_speech_required:
        audio_stream = generate_audio_stream(response_text)
        if audio_stream:
            audio_response = Response(audio_stream, mimetype='audio/mp3')
        else:
            return jsonify({'response': response_text, 'error': "Failed to generate speech."})

    # Return combined response
    if audio_response:
        # Include text response as a custom header
        audio_response.headers['X-Response-Text'] = response_text
        return audio_response

    # Default text response
    return jsonify({'response': response_text})


if __name__ == '__main__':
    app.run(debug=True)