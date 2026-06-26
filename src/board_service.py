import sys
from models import Player, Guess


def print_board(
    player: Player,
    command: str = "",
):
    """
    Validates the Player status and prints the game board.

    :param player: a Player object *
    """
    # if game has not started yet
    if not player.game_in_progress:
        print("Error: no active game")
        sys.exit(1)

    if command == "board":
        print(f"May the odds be in your favor {player.name}!")

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


def print_empty_board_line(count: int):
    """
    Prints an empty line of the game board.

    :param count: an int for the number of tile spaces to print *
    """
    line = ""
    spaces = ""
    for i in range(count):
        line += "*****  "
        spaces += "*   *  "
    print(line)
    print(spaces)
    print(line)


def print_color(color: str, to_print: str):
    """
    Matches the given color to the ANSI color code and returns the string
    with the color code.

    :param color: color for the given string *
    :param to_print: string to be printed *
    :returns: string with ANSI color codes for the given color and text
    """
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


def print_board_line(guess: Guess):
    """
    Prints a line of the game board.

    :param guess: a Guess object *
    """
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
