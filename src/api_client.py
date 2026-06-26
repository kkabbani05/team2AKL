import requests

def login_with_server(username: str):
    try:
        response = requests.post(
            "http://localhost:5000/sessions",  # Hardcode or config
            json={"name": username.lower()} # username is meant to be lowercase
        )
        if response.status_code == 422: # user is not found
            return None, "user_not_found"
        elif response.status_code == 200:
            data = response.json()
            return data.get("id"), None
    except:
        return None, "server_down"

def fetch_board(id):
    try:
        response = requests.get(
            "http://localhost:5000/sessions/players/" + id + "/board"
        )

    except requests.exceptions.ConnectionError:
        return None