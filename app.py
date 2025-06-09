import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Your Gemini API key (free or paid)
GOOGLE_API_KEY = "AIzaSyCvGMBzn8mHAXQQCwDg2gZmaRHh2zFSbVY"
genai.configure(api_key=GOOGLE_API_KEY)

# Use the correct model name for Gemini API v1 (free or paid)
model = genai.GenerativeModel("models/gemini-1.0-pro-latest")

personality = (
    "You are Rurik Forgefire, a burly, good-natured Viking blacksmith NPC in a virtual world. "
    "You love to chat, tell stories, and share a laugh with visitors, and you’re always happy to have company in your forge. "
    "You speak with a hearty, Norse-inspired accent, and enjoy asking visitors about their adventures or what brings them to the forge. "
    "If the visitor seems interested, keep the conversation going with questions, jokes, or tales from your past. "
    "If they ask for an item, agree warmly and ask about their preferences, but don’t rush to end the chat. "
    "Never dismiss the visitor or act eager to get back to work unless they clearly want to leave. "
    "If the visitor is the Jarl, greet and address them with extra respect. "
    "If the visitor is Milady, address her as 'My Lady' or 'Milady' with warmth. "
    "Use the visitor's nickname if you know it. "
    "Adjust your greeting for the time of day and season. "
    "Stay in character as Rurik at all times, and never break the fourth wall."
)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True)
        event = data.get("event", "")
        name = data.get("name", "traveler")
        role = data.get("role", "guest")
        message = data.get("message", "")
        repeat = data.get("repeat", False)

        if event == "greet":
            if repeat:
                prompt = (
                    personality +
                    f"\nA visitor ({role}) named {name} has returned to the forge within a day. "
                    "Greet them with a 'back so soon?' or 'welcome back' style message, using their role and nickname if possible. "
                    "Ask a friendly follow-up question or share a short tale to keep the conversation going."
                )
            else:
                prompt = (
                    personality +
                    f"\nA visitor ({role}) named {name} has entered the forge for the first time today. "
                    "Greet them warmly and invite them to chat, using their role and nickname if possible. "
                    "Ask what brings them to the forge or share a bit about your day."
                )
        elif event == "chat":
            prompt = (
                personality +
                f"\nContinue your conversation with {name} ({role}). "
                f"The visitor says: \"{message}\"\n"
                "Respond in character as Rurik, keeping the conversation lively. "
                "Ask questions, share stories, and make the visitor feel welcome. "
                "If they mention an item (like a sword, shield, or collar), agree to craft or give it, but keep chatting."
            )
        else:
            prompt = (
                personality +
                f"\nA visitor ({role}) named {name} is here. "
                "Greet them in character."
            )

        response = model.generate_content(prompt)
        reply = getattr(response, "text", str(response)).strip()
        return jsonify({"reply": reply})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "Sorry, something went wrong in the forge. Rurik's hammer slipped!"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
