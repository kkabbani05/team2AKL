import requests
import sys


BASE_URL = "http://localhost:8000"


def _auth_headers(user_id: int):
    return {"Authorization": f"Bearer {user_id}"}


def login_with_server(username: str):
    """
    POST /sessions with username, returns (user_id, error) tuple
    """
    try:
        response = requests.post(
            f"{BASE_URL}/sessions", json={"name": username.strip().lower()}
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


def register_player(username: str):
    """
    POST /players with username
    """
    try:
        response = requests.post(f"{BASE_URL}/players", json={"name": username})
        if response.status_code == 201:
            print(f"May the odds be in your favor {username}!")
            sys.exit(0)
        elif response.status_code == 422:
            data = response.json()
            detail = data.get("detail")
            if detail == "Name cannot be empty":
                print("Name cannot be empty.")
                sys.exit(1)
            elif detail == "Username is already taken":
                print("That name is already taken. Please choose another.")
                sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Looks like the wurdal servers are taking a loss... try again later!")
    except Exception:
        print("Looks like the wurdal servers are taking a loss... try again later!")


def fetch_board(user_id):
    """
    GET /players/{user_id}/board, returns board data dict
    """

    try:
        response = requests.get(
            f"{BASE_URL}/players/{user_id}/board",
            headers=_auth_headers(user_id),
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def fetch_games_for_user(user_id: int):
    """
    GET /games filtered by user_id, returns list of game dicts or empty list.
    """
    try:
        response = requests.get(f"{BASE_URL}/games", params={"user_id": user_id})
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception:
        return []


def find_active_game_id(user_id: int, word_to_guess: str | None = None):
    """
    Find the most recent in-progress game id for a user.
    If word_to_guess is provided, prefer a matching game first.
    """
    games = fetch_games_for_user(user_id)
    if not games:
        return None

    ordered_games = sorted(games, key=lambda game: game.get("id", 0), reverse=True)

    if word_to_guess:
        normalized_word = word_to_guess.strip().upper()
        for game in ordered_games:
            if (
                game.get("status") == "in_progress"
                and str(game.get("word_to_guess", "")).strip().upper()
                == normalized_word
            ):
                return game.get("id")

    for game in ordered_games:
        if game.get("status") == "in_progress":
            return game.get("id")

    return None


def create_guess(game_id: int, attempt_no: int, guess_word: str, feedback: str):
    """
    POST /guesses for a specific game.
    Returns True if persisted; False otherwise.
    """
    payload = {
        "game_id": game_id,
        "attempt_no": attempt_no,
        "guess_word": guess_word.strip().lower(),
        "feedback": feedback,
    }
    try:
        response = requests.post(f"{BASE_URL}/guesses", json=payload)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def create_game(user_id: int, word_to_guess: str, status: str = "in_progress"):
    """
    POST /games for a specific user.
    Returns True if persisted; False otherwise.
    """
    payload = {
        "user_id": user_id,
        "word_to_guess": word_to_guess.strip().lower(),
        "status": status,
    }
    try:
        response = requests.post(f"{BASE_URL}/games", json=payload)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def update_game_status(game_id: int, status: str):
    """
    PUT /games/{game_id} to update game status.
    Returns True if updated; False otherwise.
    """
    payload = {"status": status}
    try:
        response = requests.put(f"{BASE_URL}/games/{game_id}", json=payload)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False
<<<<<<< Updated upstream
    
def get_leaderboard():
    try:
        response = requests.get(f"{BASE_URL}/leaderboard")
        return response.json()
    except requests.exceptions.ConnectionError:
        return
    except Exception:
        return
=======


def submit_player_guess(user_id: int, guess_word: str):
    """
    POST /players/{user_id}/guess with bearer auth.
    Returns (response_data, error_message)
    """
    payload = {"guess": guess_word.strip().lower()}
    try:
        response = requests.post(
            f"{BASE_URL}/players/{user_id}/guess",
            json=payload,
            headers=_auth_headers(user_id),
        )
        if response.status_code == 200:
            return response.json(), None

        if response.status_code == 422:
            detail = response.json().get("detail")
            return None, detail or "Error: invalid guess"

        if response.status_code == 403:
            return None, "Please login to continue"

        return None, "Error: could not submit guess"
    except requests.exceptions.ConnectionError:
        return None, "Looks like the wurdal servers are taking a loss... try again later!"
    except Exception:
        return None, "Looks like the wurdal servers are taking a loss... try again later!"
>>>>>>> Stashed changes
