import requests

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