import json 
import os 

# Session file to manage the logged in player's "session."

def save_session(user_id, player_name):
    session_data = {
        "user_id": user_id,
        "player_name": player_name,
        # "token": token
    }
    try:
        with open("../session.json", "w") as f:
            json.dump(session_data, f)
    except FileNotFoundError:
        print("Error: Could not save session")

def load_session():
    try:
        with open("../session.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# delete sesion file 
def clear_session():
    try:
        os.remove("../session.json")
    except FileNotFoundError:
        pass  # Already gone, no problem