#!/usr/bin/env python
import sys
import argparse
import random
import re
from pydantic import BaseModel, TypeAdapter, ValidationError


class Guess(BaseModel):
    guess: str
    colors: dict


class Word(BaseModel):
    word: str
    guesses: list[Guess]


class Record(BaseModel):
    wins: int
    guess_count: int


class Player(BaseModel):
    name: str
    current_word_index: int
    current_word: Word | None = None
    game_in_progress: bool
    seen_words: list[Word]
    record: Record


word_list = [
    "hush",
    "harden",
    "slant",
    "lashed",
    "whirr",
    "online",
    "thorn",
    "wearer",
    "soled",
    "award",
    "sward",
    "sane",
    "slide",
    "watt",
    "estate",
    "lender",
    "hone",
    "strewn",
    "shone",
    "inhale",
    "sadist",
    "sewed",
    "tow",
    "whined",
    "swath",
    "aslant",
    "hoed",
    "astern",
    "salt",
    "hoist",
    "dilute",
    "dared",
    "dud",
    "hearse",
    "silent",
    "unseat",
    "rostra",
    "soot",
    "seethe",
    "whirl",
    "rioted",
    "riddle",
    "tented",
    "hand",
    "unsaid",
    "unseen",
    "audit",
    "waddle",
    "unread",
    "hereto",
    "learnt",
    "stern",
    "weird",
    "died",
    "horded",
    "hint",
    "shat",
    "tittle",
    "show",
    "tinier",
    "adore",
    "risen",
    "when",
    "woolen",
    "lute",
    "indue",
    "direst",
    "aster",
    "erased",
    "stole",
    "then",
    "worth",
    "shut",
    "raster",
    "swear",
    "dense",
    "rid",
    "artier",
    "taint",
    "dare",
    "worsen",
    "aloud",
    "stow",
    "salad",
    "oleo",
    "senate",
    "dill",
    "other",
    "loiter",
    "roil",
    "sassed",
    "resale",
    "stein",
    "tread",
    "wheel",
    "reset",
    "wen",
    "wear",
    "hooted",
    "wine",
    "redone",
    "deal",
    "rash",
    "ewe",
    "dent",
    "dialed",
    "ended",
    "insert",
    "turret",
    "listen",
    "herein",
    "deed",
    "lesson",
    "rider",
    "load",
    "rhea",
    "shout",
    "well",
    "rodeo",
    "outed",
    "retard",
    "nodded",
    "eroded",
    "waste",
    "dried",
    "adorn",
    "thwart",
    "sort",
    "wonted",
    "uh",
]


class WurdalArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2)


def parse_args():
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

    # wurdal new-game <player-name>
    new_game_parser = subparsers.add_parser(
        "new-game", help="Start a new game", usage="%(prog)s <player-name>"
    )
    new_game_parser.add_argument("player_name", metavar="player-name")

    # wurdal guess <player-name> <word>
    guess_parser = subparsers.add_parser(
        "guess", help="Make a guess", usage="%(prog)s <player-name> <word>"
    )
    guess_parser.add_argument("player_name", metavar="player-name")
    guess_parser.add_argument("word")

    board_parser = subparsers.add_parser(
        "board", help="Board", usage="%(prog)s <player-name>"
    )
    board_parser.add_argument("player_name", metavar="player-name")

    # wurdal leaderboard [--by-games]
    leaderboard_parser = subparsers.add_parser("leaderboard", help="Show leaderboard")
    leaderboard_parser.add_argument(
        "--by-games", action="store_true", help="Sort by number of games played"
    )

    return parser.parse_args()


def load_players():
    try:
        
        
        json_data = ""
        with open("players.json", "r", encoding="utf-8") as f:
            json_data = f.read()
        return TypeAdapter(list[Player]).validate_json(json_data)
    except FileNotFoundError:
        with open("players.json", "w") as f:
            f.write('[]')
        return TypeAdapter(list[Player]).validate_json('[]')
    except ValidationError:
        print("Error: Invalid Json")


def write_players(registered_players):
    try:
        adapter = TypeAdapter(list[Player])
        json_bytes = adapter.dump_json(registered_players, indent=4)
        with open("players.json", "wb") as f:
            f.write(json_bytes)
    except FileNotFoundError:
        print("Error: File Not Found")


def find_player(player_name, registered_players):
    i = next(
        i for i, player in enumerate(registered_players) if player.name == player_name
    )
    return i, registered_players[i]


def player_to_list(player, idx, registered_players):
    registered_players[idx] = Player(
        name=player.name,
        current_word_index=player.current_word_index,
        current_word=player.current_word,
        game_in_progress=player.game_in_progress,
        seen_words=player.seen_words,
        record=player.record,
    )
    return registered_players[idx]


def register(player_name, registered_players):
    # if player name is empty
    if player_name == "":
        print("Error: invalid player name")
        sys.exit(1)

    # if player already exists
    if any(player.name == player_name for player in registered_players):
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


def new_game(player_name, registered_players):
    # if player is not registered
    if not any(player.name == player_name for player in registered_players):
        print("Error: player not found")
        sys.exit(1)

    i = next(
        i for i, player in enumerate(registered_players) if player.name == player_name
    )
    player = registered_players[i]

    # if player is already in a game
    if player.game_in_progress:
        print("Error: game in progress")
        sys.exit(1)

    # if player has seen all the words
    if len(player.seen_words) == len(word_list):
        print("Error: no words available")
        sys.exit(1)

    word_idx = select_word(player)
    player.current_word_index = word_idx
    player.game_in_progress = True
    player = player_to_list(player, i, registered_players)
    print("✨ New game started ✨")
    print_board(player)


def select_word(player):
    # pick a random word from the word list that the player has not seen before
    idx = random.randint(0, len(word_list) - 1)
    word = word_list[idx]

    while any(word == seen_word.word for seen_word in player.seen_words):
        idx = random.randint(0, len(word_list) - 1)
        word = word_list[idx]

    player.current_word = Word(word=word, guesses=[])
    player.seen_words.append(player.current_word)
    return idx


def guess(player_name, guess_string, registered_players):
    idx, player = find_player(player_name, registered_players)

    # if game has not started yet
    if not player.game_in_progress:
        print("Error: no active game")
        sys.exit(1)

    # if player does not exist
    if player not in registered_players:
        print("Error: player not found")
        sys.exit(1)

    word = player.current_word.word

    # guess validation
    guess_validation(guess_string, word)
    win = False
    lose = False
    if guess_string == word:
        player.record.wins += 1
        player.record.guess_count += len(player.current_word.guesses) + 1
        win = True
    # track guesses after loss
    elif len(player.current_word.guesses) + 1 == 6:
        lose = True
        player.record.guess_count += 6

    # check one to one positions for green
    tally = dict()
    for c in word:
        if c in tally:
            tally[c] += 1
        else:
            tally[c] = 1

    colors = {}
    # check one to one positions for green tiles
    for i, c in enumerate(guess_string):
        if c == word[i]:
            colors[str(i)] = "green"
            tally[c] -= 1

    # check for yellow
    for i, c in enumerate(guess_string):
        if str(i) not in colors:
            if c in word and tally[c] > 0:
                colors[str(i)] = "yellow"
                tally[c] -= 1
            else:
                colors[str(i)] = "grey"

    new_guess = Guess(guess=guess_string, colors=colors)
    player.current_word.guesses.append(new_guess)
    player = player_to_list(player, idx, registered_players)
    print_board(player)
    
    if win:
        print(f"{player.name} solved it in {len(player.current_word.guesses)} guesses!")
    
    if win or lose:
        player.game_in_progress = False


def guess_validation(guess_string, word):
    # checks the length of the guess
    if len(guess_string) < len(word) or len(guess_string) > len(word):
        print("Error: invalid guess")
        sys.exit(1)

    # checks if the guess is all letters
    if not guess_string.isalpha():
        print("Error: invalid guess")
        sys.exit(1)


def print_board(player):
    # if game has not started yet
    if not player.game_in_progress:
        print("Error: no active game")
        sys.exit(1)

    count = len(player.current_word.word)

    # if player has not made any guesses yet, print empty board
    if len(player.current_word.guesses) == 0:
        for i in range(6):
            print_empty_board_line(count)
    else:
        # print game with guesses
        for guess in player.current_word.guesses:
            print_board_line(guess)

        for i in range(6 - len(player.current_word.guesses)):
            print_empty_board_line(count)


def print_empty_board_line(count):
    line = ""
    spaces = ""
    for i in range(count):
        line += "*****  "
        spaces += "*   *  "
    print(line)
    print(spaces)
    print(line)


def print_color(color, to_print):
    match color:
        case "green":
            return f"\033[32m{to_print}\033[32m\033[0m"
        case "yellow":
            return f"\033[33m{to_print}\033[33m\033[0m"
        case "grey":
            return f"\033[37m{to_print}\033[37m\033[0m"
        case _:
            print("Error: internal error")
            exit(3)


def print_board_line(guess):
    count = len(guess.guess)
    line = ""

    for i in range(count):
        color = guess.colors[str(i)]
        line += print_color(color, "*****  ")

    print(line)
    guess_line = ""
    for i, c in enumerate(guess.guess):
        color = guess.colors[str(i)]
        guess_line += print_color(color, "* ")
        guess_line += c
        guess_line += print_color(color, " *  ")
    print(guess_line)
    print(line)


def leaderboard(registered_players):
    print("Leaderboard\n")
    sorted_players = player_sort(registered_players)
    if len(sorted_players) == 0 or sorted_players[0].record.wins == 0:
        print("no wins yet.")
    else:
        for i, player in enumerate(sorted_players):
            print(f"{i + 1}. {player.name} - wins: {player.record.wins}")


def player_sort(registered_players):
    return sorted(registered_players, key=lambda x: (-x.record.wins, x.name))


def main():
    registered_players = load_players()
    args = parse_args()

    if args.command == "register":
        register(args.player_name, registered_players)
    elif args.command == "new-game":
        new_game(args.player_name, registered_players)
    elif args.command == "guess":
        guess(args.player_name, args.word, registered_players)
    elif args.command == "board":
        print_board(find_player(args.player_name, registered_players)[1])
    elif args.command == "leaderboard":
        leaderboard(registered_players)

    write_players(registered_players)


if __name__ == "__main__":
    main()
