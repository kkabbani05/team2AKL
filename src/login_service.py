import sys
import board_service
import api_client 
import session_manager


def login(player_name: str, registered_players: list):
    """
    Checks if a player_name is registered and logs in the player via API.

    :param player_name: Player name to be logged in
    :param registered_players: a list of Player objects (not used in API flow)
    """
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

    # Fetch and display board from API
    board_data = api_client.fetch_board(user_id)
    if board_data:
        board_service.print_board(board_data)


def logout():
    """
    Logs out the current player by clearing session and current_player.txt.
    """
    try:
        session_manager.clear_session()
        with open("current_player.txt", "w") as f:
            f.write("")
        print("Successfully logged out")
    except FileNotFoundError:
        print("No player is currently logged in.")
