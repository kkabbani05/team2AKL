from api_client import get_leaderboard
import sys


def leaderboard():
    """
    Sorts the players by wins and prints the leaderboard.

    :param registered_players: a list of Player objects *
    """
    data = get_leaderboard()
    if data is None:
        print("Looks like the wurdal servers are taking a loss... try again later!")
        return
    elif len(data["players"]) == 0:
        print("No players on the leaderboard yet. Be the first to register!")
        return
    
    print("====---------====")
    print("== Leaderboard ==")
    print("====---------====")
    for player in data["players"]:
        print(f"{player["name"]} with {player["wins"]} wins, {player["losses"]} losses, and an average of {player["average_guesses"]} guesses")
