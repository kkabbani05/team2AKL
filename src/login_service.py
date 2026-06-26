import sys
import board_service
import api_client 
import session_manager
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

    # Call API to login
    user_id, error = api_client.login_with_server(player_name)
    if error:
        if error == "server_down":
            print("Looks like the wurdal servers are taking a loss... try again later!")
        elif error == "user_not_found":
            print(f"Could not find user {player_name}. Please register first with: wurdal register {player_name}")
        return  # Don't save session on error
 
    # Save session to disk
    session_manager.save_session(user_id, player_name)

    # Write current player file for CLI
    with open("current_player.txt", "w") as file:
        file.write(player_name)

    # Display welcome message
    print(f"May the odds be in your favor {player_name}!")

    # Fetch board from API
    board_data = api_client.fetch_board(user_id)
    if board_data:
        # TODO: Convert API board response to Player object or handle display
        # For now, just confirm login succeeded
        #board_service.print_board(board_data)
        pass
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
