import sys
import argparse
from pydantic import TypeAdapter, ValidationError
from models import Player


class WurdalArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2)


def read_in_word_list():
    """
    Reads in the words from the word list text file.
    return: words: list of words for the player to guess.
    """
    try:
        with open("../src/word_list.txt", "r") as f:
            words = f.read().split("\n")
        return words
    except FileNotFoundError:
        print("Word list not found.")
        sys.exit(3)


def parse_args():
    """
    Sets up argument parser for CLI
    return: words: list of words for the player to guess.
    """
    parser = WurdalArgumentParser(prog="wurdal", description="Wordle Cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # wurdal register <player-name>
    register_parser = subparsers.add_parser(
        "register", help="Register a new player", usage="%(prog)s <player-name>"
    )
    register_parser.add_argument(
        "player_name",
        metavar="player-name",
    )

    # wurdal guess <word>
    guess_parser = subparsers.add_parser(
        "guess", help="Make a guess", usage="%(prog)s <word>"
    )
    guess_parser.add_argument("word")

    # wurdal board
    subparsers.add_parser("board", help="Show board")

    # wurdal login <player-name>
    login_parser = subparsers.add_parser(
        "login", help="Login a player", usage="%(prog)s <player-name>"
    )
    login_parser.add_argument("player_name", metavar="player-name")

    # wurdal logout
    subparsers.add_parser("logout", help="Logout current player")

    # wurdal leaderboard [--by-games]
    leaderboard_parser = subparsers.add_parser("leaderboard", help="Show leaderboard")
    leaderboard_parser.add_argument(
        "--by-games", action="store_true", help="Sort by number of games played"
    )

    return parser.parse_args()


def load_players():
    """
    Load players from persisted storage
    return: list[Player]: list of registered players
    """
    try:
        json_data = ""
        with open("../players.json", "r", encoding="utf-8") as f:
            json_data = f.read()
        return TypeAdapter(list[Player]).validate_json(json_data)
    except FileNotFoundError:
        with open("../players.json", "w") as f:
            f.write("[]")
        return TypeAdapter(list[Player]).validate_json("[]")
    except ValidationError:
        print("Error: Invalid Json")


def write_players(registered_players: list[Player]):
    """
    Writes players to persisted storage
    """
    try:
        adapter = TypeAdapter(list[Player])
        json_bytes = adapter.dump_json(registered_players, indent=4)
        with open("../players.json", "wb") as f:
            f.write(json_bytes)
    except FileNotFoundError:
        print("Error: File Not Found")


def find_player(player_name: str, registered_players: list[Player]):
    """
    Load players from persisted storage

    :param player_name: a name of a player to be found
    :param registered_players: a list of registered players
    return: i: index of player in the list
    return: Player: found player in the list
    """
    i = next(
        i for i, player in enumerate(registered_players) if player.name == player_name
    )
    return i, registered_players[i]


def player_to_list(player: Player, idx: int, registered_players: list[Player]):
    """
    Updates a player in the registered players list.

    :param player: a Player object *
    :param idx: an int of the player's index *
    :param registered_players: a list of registered Player objects *
    :returns: updated Player object
    """
    registered_players[idx] = Player(
        name=player.name,
        current_word_index=player.current_word_index,
        current_word=player.current_word,
        game_in_progress=player.game_in_progress,
        seen_words=player.seen_words,
        record=player.record,
    )
    return registered_players[idx]
