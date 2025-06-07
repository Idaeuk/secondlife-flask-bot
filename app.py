import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Use your Gemini API key directly (for testing)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyCvGMBzn8mHAXQQCwDg2gZmaRHh2zFSbVY"  # Your API key from earlier

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route('/')
def hello():
    return "Hello from your Flask bot!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']

    # Rurik Forgefire personality prompt
    personality = (
        "You are Rurik Forgefire, a burly, good-natured Viking blacksmith NPC in a virtual world. "
        "You speak with a hearty, Norse-inspired accent, love to tell stories of the old country, "
        "and often add humor to your replies. Stay in character as Rurik at all times, answer as if "
        "you’re in your forge, and never break the fourth wall.\n\n"
    )

    # Combine the personality prompt with the user's message
    full_prompt = personality + f"Visitor says: {user_message}\nRurik replies:"

    try:
        response = model.generate_content(full_prompt)
        reply = response.text.strip().replace('\n', ' ')  # Removes ALL newlines from the reply
    except Exception as e:
        reply = f"Error from Gemini: {str(e)}"

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
