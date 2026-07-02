import sys
import os 
import argparse
from pathlib import Path
import requests
from pydantic import TypeAdapter
from models import Player, Word, Guess, Record

BASE_URL = "http://localhost:8000"

# Maps the DB feedback codes to the colors used by the CLI board.
FEEDBACK_COLORS = {"GR": "green", "Y": "yellow", "G": "grey"}


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
        word_list_path = Path(__file__).with_name("word_list.txt")
        with word_list_path.open("r") as f:
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
    Load players from the database via the API.
    return: list[Player]: list of registered players
    """
    try:
        response = requests.get(f"{BASE_URL}/sessions")
        if response.status_code != 200:
            return []
        users = response.json()
        if not isinstance(users, list):
            return []
        return [build_player(user) for user in users]
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        print("An unexpected error occurred while loading players.")
        return []


def read_field(payload: dict, *keys, default=None):
    """
    Reads a field from a response payload using any of the provided key names.
    This supports both snake_case and camelCase API responses.
    """
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def feedback_to_colors(feedback: str):
    """
    Converts a DB feedback string (e.g. "G,Y,GR") into the colors dict used
    by the CLI board. Returns None if the feedback is not a valid colour list.
    """
    colors = {}
    for i, code in enumerate(feedback.split(",")):
        color = FEEDBACK_COLORS.get(code.strip().upper())
        if color is None:
            return None
        colors[str(i)] = color
    return colors


def build_word(game: dict):
    """
    Builds a Word object for a game by fetching its guesses from the API.

    :param game: a game dict from the /games endpoint
    :returns: a Word object with its guesses
    """
    game_id = read_field(game, "id")
    response = requests.get(f"{BASE_URL}/guesses", params={"game_id": game_id})
    guesses = []
    if response.status_code == 200:
        guess_rows = response.json()
        if not isinstance(guess_rows, list):
            guess_rows = []

        for db_guess in sorted(
            guess_rows,
            key=lambda g: read_field(g, "attempt_no", "attemptNo", default=0),
        ):
            feedback = read_field(db_guess, "feedback")
            guess_word = read_field(db_guess, "guess_word", "guessWord")
            if feedback is None or guess_word is None:
                continue

            colors = feedback_to_colors(feedback)
            if colors is None:
                continue
            guesses.append(Guess(guess=guess_word.lower(), colors=colors))

    word_to_guess = read_field(game, "word_to_guess", "wordToGuess", default="")
    return Word(word=word_to_guess.lower(), guesses=guesses)


def build_player(user: dict):
    """
    Builds a Player object from a user by fetching their games and guesses.

    :param user: a user dict from the /sessions endpoint
    :returns: a fully populated Player object
    """
    user_id = read_field(user, "id")
    response = requests.get(f"{BASE_URL}/games", params={"user_id": user_id})
    games = response.json() if response.status_code == 200 else []
    if not isinstance(games, list):
        games = []

    seen_words = []
    current_word = None
    game_in_progress = False
    wins = 0
    guess_count = 0

    for game in games:
        word = build_word(game)
        seen_words.append(word)
        status = read_field(game, "status", default="")
        if status == "in_progress":
            current_word = word
            game_in_progress = True
        else:
            guess_count += len(word.guesses)
            if status in ("completed", "won"):
                wins += 1

    return Player(
        name=read_field(user, "name", default=""),
        current_word=current_word,
        game_in_progress=game_in_progress,
        seen_words=seen_words,
        record=Record(wins=wins, guess_count=guess_count),
    )


def write_players(registered_players: list):
    """
    Writes players to persisted storage
    """
    ##NEW 

    expected_keys = {
        "name",
        "current_word_index",
        "current_word",
        "game_in_progress",
        "seen_words",
        "record",
    }

    if not registered_players:
        return

    if not all(isinstance(player, dict) and expected_keys.issubset(player.keys()) for player in registered_players):
        return

    ## NEW
    try:
        adapter = TypeAdapter(list[Player])
        json_bytes = adapter.dump_json(registered_players, indent=4)
        with open("../players.json", "wb") as f:
            f.write(json_bytes)
    except FileNotFoundError:
        print("Error: File Not Found")


def find_player(player_name: str, registered_players: list):
    """
    Load players from persisted storage

    :param player_name: a name of a player to be found
    :param registered_players: a list of registered players
    return: i: index of player in the list
    return: Player: found player in the list
    """
    i = next(
        i
        for i, player in enumerate(registered_players)
        if player.name.strip().lower() == player_name.strip().lower()
    )
    return i, registered_players[i]


def player_to_list(player: Player, idx: int, registered_players: list):
    """
    Updates a player in the registered players list.

    :param player: a Player object *
    :param idx: an int of the player's index *
    :param registered_players: a list of registered Player objects *
    :returns: updated Player object
    """
    registered_players[idx] = Player(
        name=player.name,
        current_word=player.current_word,
        game_in_progress=player.game_in_progress,
        seen_words=player.seen_words,
        record=player.record,
    )
    return registered_players[idx]
