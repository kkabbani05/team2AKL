from models import Player


def leaderboard(registered_players: list[Player]):
    """
    Sorts the players by wins and prints the leaderboard.

    :param registered_players: a list of Player objects *
    """
    print("Leaderboard\n")
    sorted_players = player_sort(registered_players)
    if len(sorted_players) == 0 or sorted_players[0].record.wins == 0:
        print("No wins yet.")
    else:
        for i, player in enumerate(sorted_players):
            print(f"{i + 1}. {player.get("name")} - wins: {player.record.wins}")


def player_sort(registered_players: list[Player]):
    """
    Sorts the list of Player objects by wins in descending order.

    :param registered_players: a list of Player objects *
    :returns: sorted list of Player objects 
    """
    return sorted(registered_players, key=lambda x: (-x.record.wins, x.name))