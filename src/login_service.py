import sys
import board_service
from utils import find_player, read_in_word_list
import new_game_service


def login(player_name: str, registered_players: list):
    """
    Checks if a player_name is registered and logs in the player.

    :param player_name: Player name to be logged in
    :param registered_players: a list of Player objects
    """
    player_name = str.lower(player_name)

    # if player name is empty
    if player_name == "":
        print("Error: invalid player name")
        sys.exit(1)

    # if player does not exist
    if not any(player.name == player_name for player in registered_players):
        print(f"Could not find user {player_name}. Please register")
        print(f"Please run 'wurdal register {player_name}' to register")
        sys.exit(1)

    print(f"Player {player_name} logged in successfully")

    file = open("current_player.txt", "w")
    file.write(player_name)
    file.close()

    print(f"May the odds be in your favor {player_name}!")

    player = find_player(player_name, registered_players)[1]
    if player.game_in_progress:
        print(f"Here is your current game board, {player_name}:")
        board_service.print_board(player)
    elif not player.game_in_progress:
        print(f"No active game found, starting new game for {player_name}.")
        word_list = read_in_word_list()
        new_game_service.new_game(player_name, registered_players, word_list)


def logout():
    """
    Logs out the current player by removing the current_player.txt file.
    """
    try:
        import os

        os.remove("current_player.txt")
        print("Successfully logged out")
    except FileNotFoundError:
        print("No player is currently logged in.")
