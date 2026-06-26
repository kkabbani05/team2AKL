import sys
import new_game_service
from models import Player, Guess
from board_service import print_board
from utils import player_to_list, find_player, read_in_word_list


def guess(player_name: str, guess_string: str, registered_players: list[Player]):
    """
    Handles the guess command functionality, from checking the player name to handling guess validation and correctness.

    :param player_name: Registered player that is in a current game
    :param guess_string: Word that the player has entered as a guess
    :param registered_players: a list of player objects
    """

    if not any(player.get("name").strip().lower() == player_name.strip().lower() for player in registered_players):
        print("Error: player not found")
        sys.exit(1)

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

    guess_string = str.lower(guess_string)

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
        print(f"{player.get("name")} solved it in {len(player.current_word.guesses)} guesses!")

    if win or lose:
        player.game_in_progress = False
        print(f"Game over for {player.get("name")}.")
        print(f"The word was: {player.current_word.word}")
        print(f"Starting new game for {player.get("name")}:")
        word_list = read_in_word_list()
        new_game_service.new_game(player_name, registered_players, word_list)


def guess_validation(guess_string: str, word: str):
    """
    Checks guess validity ensuring that the guess is the same lenght as the secret word and is all letters.

    :param guess_string: Word that the player has entered as a guess
    :param word: the secret word that is to be guessed
    """

    # checks the length of the guess
    if len(guess_string) < len(word) or len(guess_string) > len(word):
        print("Error: invalid guess")
        sys.exit(1)

    # checks if the guess is all letters
    if not guess_string.isalpha():
        print("Error: invalid guess")
        sys.exit(1)
