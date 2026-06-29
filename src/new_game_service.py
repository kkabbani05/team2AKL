import sys
import random
import api_client
import session_manager
from board_service import print_board
from models import Player, Word
from utils import player_to_list


def new_game(player_name: str, registered_players: list[Player], word_list: list[str]):
    """
    Handles the new game command functionality, from checking that the player is registered to assiging them a new word from the word list.

    :param player_name: Registered player that isn't in a current game
    :param registered_players: a list of player objects
    :param word_list: List of secret words to seed the game for the player
    """
    # if player is not registered
    if not any(player.name.strip().lower() == player_name.strip().lower() for player in registered_players):
        print("Error: player not found")
        sys.exit(1)

    i = next(
        i for i, player in enumerate(registered_players) if player.name.strip().lower() == player_name.strip().lower()
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

    select_word(player, word_list)

    if not persist_new_game(player_name, player.current_word.word):
        # Roll back local state when DB persistence fails.
        if player.seen_words and player.seen_words[-1] == player.current_word:
            player.seen_words.pop()
        player.current_word = None
        print("Error: could not start a new game")
        sys.exit(1)

    player.game_in_progress = True
    player = player_to_list(player, i, registered_players)
    print("✨ New game started ✨")
    print_board(player)


def persist_new_game(player_name: str, word_to_guess: str):
    """
    Persist a newly created game to the API backend when a matching session exists.
    """
    session = session_manager.load_session()
    if not session:
        return True

    session_player = str(session.get("player_name", "")).strip().lower()
    if session_player != player_name.strip().lower():
        return True

    user_id = session.get("user_id")
    if not user_id:
        return False

    return api_client.create_game(user_id, word_to_guess, "in_progress")


def select_word(player: Player, word_list: list[str]):
    """
    Randomly selects a new word from the word list

    :param player_name: Registered player that isn't in a current game
    :param registered_players: a list of player objects
    :param word_list: List of secret words for the player to guess
    :returns idx: returns index of secret word
    """
    # pick a random word from the word list that the player has not seen before
    idx = random.randint(0, len(word_list) - 1)
    word = word_list[idx]

    while any(word == seen_word.word for seen_word in player.seen_words):
        idx = random.randint(0, len(word_list) - 1)
        word = word_list[idx]

    player.current_word = Word(word=word, guesses=[])
    player.seen_words.append(player.current_word)
    return idx