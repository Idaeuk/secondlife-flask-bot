import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Set your Gemini API key as an environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # fallback: hardcode for testing (not recommended for production)
  GEMINI_API_KEY = "AIzaSyCvGMBzn8mHAXQQCwDg2gZmaRHh2zFSbVY"

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
    try:
        response = model.generate_content(user_message)
        reply = response.text
    except Exception as e:
        reply = f"Error from Gemini: {str(e)}"

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
