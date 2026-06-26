import sys
import re
from api_client import register_player


def register(player_name: str, registered_players: list):
    """
    Checks if a valid player_name was given and registers a new player.

    :param player_name: New unique player_name to be registered
    :param registered_players: a list of Player objects
    """

    # if player name does not contain only letters, numbers, hyphens, and underscores
    pattern = r"^[a-zA-Z0-9_-]+$"
    if not re.match(pattern, player_name):
        print("Error: username can only contain letters, numbers, hyphens, and underscores")
        sys.exit(1)

    register_player(player_name)
