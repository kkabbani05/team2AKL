import requests

# Hardcoded test data - set USE_HARDCODED = False when API is ready
HARDCODED_USERS = {
    "tom": 123,
    "alice": 456,
}

HARDCODED_BOARDS = {
    123: {"guesses": [], "current_word": "python", "game_in_progress": True},
    456: {"guesses": [], "current_word": "wordle", "game_in_progress": True},
}

USE_HARDCODED = True  # Set to False when API is ready


def login_with_server(username: str):
    """
    POST /sessions with username, returns (user_id, error) tuple
    """
    if USE_HARDCODED:
        # Hardcoded for testing without server
        username_lower = username.lower()
        if username_lower in HARDCODED_USERS:
            return HARDCODED_USERS[username_lower], None
        else:
            return None, "user_not_found"
    
    try:
        response = requests.post(
            "http://localhost:5000/sessions",
            json={"name": username.lower()}
        )
        if response.status_code == 422:  # user not found
            return None, "user_not_found"
        elif response.status_code == 200:
            data = response.json()
            return data.get("id"), None
    except requests.exceptions.ConnectionError:
        return None, "server_down"
    except Exception:
        return None, "server_down"


def fetch_board(user_id):
    """
    GET /players/{user_id}/board, returns board data dict
    """
    if USE_HARDCODED:
        # Hardcoded for testing without server
        if user_id in HARDCODED_BOARDS:
            return HARDCODED_BOARDS[user_id]
        else:
            return None
    
    try:
        response = requests.get(
            f"http://localhost:5000/players/{user_id}/board"
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None