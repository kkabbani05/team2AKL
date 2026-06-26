import sys
import re
from models import Player, Record


def register(player_name: str, registered_players: list):
    """
    Checks if a valid player_name was given and registers a new player.

    :param player_name: New unique player_name to be registered
    :param registered_players: a list of Player objects
    """

    # if player name is empty
    if player_name == "":
        print("Error: invalid player name")
        sys.exit(1)

    # if player already exists
    if any(player.get("name").strip().lower() == player_name.strip().lower() for player in registered_players):
        print("Error: player already exists")
        sys.exit(1)

    # if player name does not contain only letters, numbers, hyphens, and underscores
    pattern = r"^[a-zA-Z0-9_-]+$"
    if not re.match(pattern, player_name):
        print("Error: invalid player name")
        sys.exit(1)

    player = Player(
        name=player_name,
        current_word_index=-1,
        seen_words=[],
        game_in_progress=False,
        record=Record(wins=0, guess_count=0),
    )
    registered_players.append(player)

    print(f"Player {player_name} registered successfully")
    print(f"May the odds be in your favor {player_name}!")
