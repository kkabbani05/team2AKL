import json
from pathlib import Path


SESSION_FILE = Path(__file__).resolve().parent.parent / "session.json"

# Session file to manage the logged in player's "session."


def save_session(user_id, player_name):
    if user_id is None or not str(player_name).strip():
        print("Error: Could not save session")
        return False

    session_data = {
        "user_id": user_id,
        "player_name": player_name,
        # "token": token
    }
    try:
        with SESSION_FILE.open("w") as f:
            json.dump(session_data, f)
        return True
    except OSError:
        print("Error: Could not save session")
        return False


def load_session():
    try:
        with SESSION_FILE.open("r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Error: Could not read session")
        return None


# delete sesion file
def clear_session():
    try:
        SESSION_FILE.unlink()
        return True
    except FileNotFoundError:
        return True
    except OSError:
        print("Error: Could not clear session")
        return False
