import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import datetime
import json

app = Flask(__name__)

# === CONFIGURATION ===
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyBRB8BS7QIxCq5Mh3kmEtvN4_6ShOBYjf4"

JARL_UUID = "5f56e25e-ce4e-415d-b8dc-21447d44c517"
MILADY_UUID = "3fbafd78-86af-4d80-868d-ec019aef6c09"
NICKNAMES_FILE = "nicknames.json"

# === GEMINI SETUP ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# === PERSISTENT NICKNAMES ===
def load_nicknames():
    if os.path.exists(NICKNAMES_FILE):
        with open(NICKNAMES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_nicknames(nicknames):
    with open(NICKNAMES_FILE, "w") as f:
        json.dump(nicknames, f)

nicknames = load_nicknames()

def get_nickname(uuid, name):
    return nicknames.get(uuid, name)

def set_nickname(uuid, nickname):
    nicknames[uuid] = nickname
    save_nicknames(nicknames)

# === TIME AND SEASON HELPERS ===
def get_time_of_day():
    hour = datetime.datetime.utcnow().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "evening"

def get_season():
    month = datetime.datetime.utcnow().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

# === CONVERSATION MEMORY ===
memory = {}  # {uuid: [history]}

def update_memory(uuid, entry):
    history = memory.get(uuid, [])
    history.append(entry)
    if len(history) > 5:
        history = history[-5:]
    memory[uuid] = history

def get_memory(uuid):
    return memory.get(uuid, [])

@app.route('/')
def hello():
    return "Hello from Rurik's Forge!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    event = data.get('event', 'chat')
    uuid = data.get('uuid')
    name = data.get('name', 'traveler')
    role = data.get('role', 'guest')
    user_message = data.get('message', '')
    nickname = get_nickname(uuid, name)
    time_of_day = data.get('time_of_day', get_time_of_day())
    season = data.get('season', get_season())

    # Allow users to set their nickname
    if user_message.lower().startswith("call me "):
        new_nick = user_message[8:].strip()
        set_nickname(uuid, new_nick)
        return jsonify({'reply': f"Alright, I'll call you {new_nick} from now on!"})

    # Role assignment
    if uuid == JARL_UUID:
        role = "Jarl"
    elif uuid == MILADY_UUID:
        role = "Milady"

    # Conversation memory
    history = get_memory(uuid)
    if user_message:
        update_memory(uuid, f"{nickname}: {user_message}")

    # Prompt construction
    personality = (
        "You are Rurik Forgefire, a burly, good-natured Viking blacksmith NPC in a virtual world. "
        "You speak with a hearty, Norse-inspired accent, love to tell stories of the old country, "
        "and often add humor to your replies. Stay in character as Rurik at all times, answer as if "
        "you’re in your forge, and never break the fourth wall. "
        "If the visitor asks about real-world news or facts, answer helpfully and accurately, but still in Rurik’s voice. "
        "If the visitor asks for a riddle, give a clever, Viking-appropriate riddle. "
        "If the visitor is the Jarl, greet and address them with extra respect. "
        "If the visitor is Milady, address her as 'My Lady' or 'Milady' with warmth. "
        "Use the visitor's nickname if you know it. "
        "Keep your replies brief and to the point—no more than 2 sentences unless specifically asked for a story or joke. "
        f"Adjust your greeting for the time of day ('{time_of_day}') and season ('{season}'). "
    )

    # Add memory/history to prompt
    if history:
        personality += "\nConversation so far:\n" + "\n".join(history[-3:]) + "\n"

    # Greeting event
    if event == "greet":
        full_prompt = (
            personality +
            f"\nA visitor ({role}) named {nickname} has entered the forge. "
            "Greet them appropriately, using their role and nickname if possible."
        )
    else:
        full_prompt = (
            personality +
            f"\nVisitor ({role}) named {nickname} says: {user_message}\nRurik replies:"
        )

    try:
        response = model.generate_content(full_prompt)
        reply = response.text.strip().replace('\n', ' ')
    except Exception as e:
        reply = f"Error from Gemini: {str(e)}"

    # Update memory with Rurik's reply
    update_memory(uuid, f"Rurik: {reply}")

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
