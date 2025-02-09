import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import threading
import time
import os
import queue
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='\n%(asctime)s - %(levelname)s - %(message)s\n',
)
logger = logging.getLogger(__name__)

# Global variables
message_queue = queue.Queue()
agent = None
is_processing = False
latest_response = ""  # Add this to store the latest response


# Define emergency keywords
EMERGENCY_KEYWORDS = [
    'severe.*headache', 'unconscious', 'breathing.*difficult', 
    'chest.*pain', 'stroke', 'seizure', 'heart.*attack',
    'severe.*bleeding', 'high.*fever.*rash', 'drowning',
    'poisoning', 'snake.*bite', 'broken.*bone'
]

# System prompt optimized for voice output
MEDICAL_SYSTEM_PROMPT = """
You are an experienced rural doctor in India providing medical advice. Given the patient details including age, weight, and symptoms, provide a single, comprehensive response that will be converted to voice. Your response should:

1. Be direct and complete without any pauses for questions
2. Assume all necessary information is already provided
3. Give clear medical advice and specific instructions
4. For mild conditions: provide step-by-step home remedies
5. For emergencies: start with "EMERGENCY ALERT" and provide immediate action steps
6. Show genuine empathy and warmth in every response
7. Provide clear, practical medical advice suitable for rural settings
8. Suggest simple home remedies using commonly available items
9. Be aware of local cultural context and healthcare limitations

Communication style:
- Use simple, non-technical language
- Be conversational and warm, like talking to a family doctor
- Give step-by-step instructions for any remedies or treatments
- For mild conditions, suggest home remedies first
- For serious conditions, immediately recommend hospital care
- If the communication language is Hindi, then keep the text in Hindi language

Response format:
- No emojis or special characters (will be converted to voice)
- No conversational fillers or questions
- Clear, sequential instructions
- Specific dosages when recommending medicines
- Direct action items

For emergencies, start with "EMERGENCY ALERT" followed by immediate actions.
For normal cases, provide complete treatment plan in one go.

Remember: This response will be converted to voice, so keep it clear, concise, and sequential.
"""

# Flask app setup
app = Flask(__name__)
CORS(app)

# Global variables
message_queue = queue.Queue()
agent = None
is_processing = False

def check_for_emergency(text):
    """Check if the input contains emergency keywords"""
    return any(re.search(keyword, text.lower()) for keyword in EMERGENCY_KEYWORDS)

def format_voice_response(response_text, is_emergency=False):
    """Format response for voice output"""
    if is_emergency:
        return f"EMERGENCY ALERT. {response_text}"
    return response_text

def initialize_agent():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY not set in environment variables or .env file")
    
    return Agent(
        model=Gemini(id="gemini-1.5-flash"),
        show_tool_calls=True,
        markdown=True,
        system_prompt=MEDICAL_SYSTEM_PROMPT
    )

def process_message_queue():
    global is_processing, latest_response
    while True:
        try:
            if not message_queue.empty() and not is_processing:
                is_processing = True
                message = message_queue.get()
                
                try:
                    # Check for emergency
                    is_emergency = check_for_emergency(message)
                    
                    # Prepare context-aware prompt
                    full_prompt = f"EMERGENCY CASE. Patient details: {message}" if is_emergency else f"Patient details: {message}"

                    # Get response
                    response = agent.run(full_prompt)
                    
                    # Format for voice output
                    voice_response = format_voice_response(response.content, is_emergency)
                    
                    # Store the latest response
                    latest_response = voice_response
                    
                    print("\n" + "="*50)
                    print("\nMEDICAL ADVICE:")
                    print("="*50)
                    print(f"\n{voice_response}\n")
                    print("="*50 + "\n")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                
                is_processing = False
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
            is_processing = False

@app.route('/hey', methods=['GET'])
def get_latest_response():
    """Endpoint to get the latest response for text-to-speech"""
    global latest_response
    return jsonify({"user_input": latest_response})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        if not data or 'user_input' not in data:
            return jsonify({"error": "No user_input provided"}), 400
            
        user_input = data['user_input']
        message_queue.put(user_input)
        
        print("\n" + "="*50)
        print(f"\nReceived and queued patient input: {user_input}")
        print("="*50 + "\n")
        
        return jsonify({"status": "Message queued successfully"})
            
    except Exception as e:
        logger.error(f"Error in chatbot endpoint: {e}")
        return jsonify({"error":str(e)}),500


@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"})

def run_flask():
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    try:
        print("\n" + "="*50)
        print("\nSTARTING MEDICAL CHATBOT SERVER")
        print("="*50 + "\n")
        
        logger.info("Initializing Gemini agent with medical system prompt...")
        agent = initialize_agent()
        logger.info("Agent initialized successfully")
        
        # Start the message processing thread
        process_thread = threading.Thread(target=process_message_queue)
        process_thread.daemon = True
        process_thread.start()
        
        # Start Flask server
        logger.info("Starting Flask server...")
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        print("\nMedical Assistant is ready to process patient cases!")
        print("Press Ctrl+C to stop the server\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down Medical Assistant...\n")
    except Exception as e:
        logger.error(f"Startup Error: {e}")
        exit(1)