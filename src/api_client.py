import requests
import sys

def login_with_server(username: str):
    """
    POST /sessions with username, returns (user_id, error) tuple
    """
    try:
        response = requests.post(
            "http://localhost:8000/sessions",
            json={"name": username.strip().lower()}
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
        response = requests.post(
            "http://localhost:8000/players",
            json={"name": username}
        )
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
            f"http://localhost:8000/players/{user_id}/board"
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None