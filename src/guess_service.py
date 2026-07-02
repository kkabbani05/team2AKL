import sys
import new_game_service
import api_client
import session_manager
from models import Player, Guess, Word
from board_service import print_board
from utils import player_to_list, find_player, read_in_word_list, feedback_to_colors


def guess(player_name: str, guess_string: str, registered_players: list[Player]):
    """
    Handles the guess command functionality, from checking the player name to handling guess validation and correctness.

    :param player_name: Registered player that is in a current game
    :param guess_string: Word that the player has entered as a guess
    :param registered_players: a list of player objects
    """

    if not any(
        player.name.strip().lower() == player_name.strip().lower()
        for player in registered_players
    ):
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

    if _try_submit_guess_with_api(player_name, guess_string, player):
        return

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

    persist_guess(player, new_guess)

    player = player_to_list(player, idx, registered_players)
    print_board(player)

    if win:
        print(f"{player.name} solved it in {len(player.current_word.guesses)} guesses!")

    if win or lose:
        end_status = "won" if win else "loss"
        persist_game_status(player, end_status)
        player.game_in_progress = False
        print(f"Game over for {player.name}.")
        print(f"The word was: {player.current_word.word}")
        print(f"Starting new game for {player.name}:")
        word_list = read_in_word_list()
        new_game_service.new_game(player_name, registered_players, word_list)


def _try_submit_guess_with_api(player_name: str, guess_string: str, player: Player):
    """
    Try the server-driven guess flow when a matching user session exists.
    Returns True when handled via API, False when local fallback should continue.
    """
    session = session_manager.load_session()
    if not session:
        return False

    session_player = str(session.get("player_name", "")).strip().lower()
    if session_player != player_name.strip().lower():
        return False

    user_id = session.get("user_id")
    if not user_id:
        return False

    response, error = api_client.submit_player_guess(user_id, guess_string)
    if error:
        print(error)
        return True

    _print_board_from_api_response(player, response)

    current = response.get("current", {}) if isinstance(response, dict) else {}
    result_payload = current.get("result") if isinstance(current, dict) else None
    if result_payload is None:
        result_payload = response.get("result") if isinstance(response, dict) else None

    if isinstance(result_payload, dict):
        result = str(result_payload.get("status", "in_progress")).strip().lower()
    else:
        result = str(result_payload or "in_progress").strip().lower()

    if result == "won":
        print("🎉 You won! 🎉")
    elif result in ("loss", "lost"):
        secret_word = None
        if isinstance(result_payload, dict):
            secret_word = result_payload.get("word")
        if secret_word is None and isinstance(response, dict):
            secret_word = response.get("secret_word")
            if secret_word is None:
                secret_word = response.get("secretWord")
        secret_word = str(secret_word or "")
        print(f"Game over! The word was {secret_word}.")

    _print_new_game_board_if_started(player, user_id, response)

    return True


def _print_board_from_api_response(player: Player, response: dict):
    """
    Render board state returned by the API guess endpoint.
    """
    current = response.get("current", {}) if isinstance(response, dict) else {}
    length = int(
        (current.get("length") if isinstance(current, dict) else None)
        or response.get("length")
        or len(player.current_word.word)
    )
    guess_rows = []
    if isinstance(current, dict):
        guess_rows = current.get("guesses", [])
    if not isinstance(guess_rows, list):
        guess_rows = response.get("guesses", []) if isinstance(response, dict) else []
    if not isinstance(guess_rows, list):
        guess_rows = []

    rendered_guesses = []
    for row in guess_rows:
        parsed_guess = _parse_guess_row(row)
        if parsed_guess is not None:
            rendered_guesses.append(parsed_guess)

    board_player = Player(
        name=player.name,
        current_word=Word(word=("x" * length), guesses=rendered_guesses),
        game_in_progress=True,
        seen_words=player.seen_words,
        record=player.record,
    )
    print_board(board_player)


def _print_new_game_board_if_started(player: Player, user_id: int, response: dict):
    """
    Render the next game board after a win/loss when the API starts a new game.
    """
    started_flag = response.get("new_game_started")
    if started_flag is None:
        started_flag = response.get("newGameStarted")

    if not started_flag:
        return

    board_data = api_client.fetch_board(user_id)
    if not board_data:
        return

    current = board_data.get("current", {})
    length = int(current.get("length") or len(player.current_word.word))
    guess_rows = current.get("guesses", [])

    rendered_guesses = []
    for row in guess_rows:
        parsed_guess = _parse_guess_row(row)
        if parsed_guess is not None:
            rendered_guesses.append(parsed_guess)

    print(f"Starting new game for {player.name}:")
    new_board_player = Player(
        name=player.name,
        current_word=Word(word=("x" * length), guesses=rendered_guesses),
        game_in_progress=True,
        seen_words=player.seen_words,
        record=player.record,
    )
    print_board(new_board_player)


def persist_guess(player: Player, guess: Guess):
    """
    Persist a guess to the API backend when a user session is available.
    """
    session = session_manager.load_session()
    if not session:
        return

    session_player = str(session.get("player_name", "")).strip().lower()
    if session_player != player.name.strip().lower():
        return

    user_id = session.get("user_id")
    if not user_id:
        return

    game_id = api_client.find_active_game_id(user_id, player.current_word.word)
    if not game_id:
        return

    attempt_no = len(player.current_word.guesses)
    feedback = feedback_from_colors(guess.colors)
    api_client.create_guess(game_id, attempt_no, guess.guess, feedback)


def persist_game_status(player: Player, status: str):
    """
    Persist game completion status to the API backend when a matching session exists.
    """
    session = session_manager.load_session()
    if not session:
        return

    session_player = str(session.get("player_name", "")).strip().lower()
    if session_player != player.name.strip().lower():
        return

    user_id = session.get("user_id")
    if not user_id:
        return

    game_id = api_client.find_active_game_id(user_id, player.current_word.word)
    if not game_id:
        return

    api_client.update_game_status(game_id, status)


def feedback_from_colors(colors: dict[str, str]):
    """
    Convert in-memory tile colors to API feedback tokens.
    """
    token_map = {"green": "GR", "yellow": "Y", "grey": "G"}
    feedback_tokens = [
        token_map.get(colors.get(str(i), "grey"), "G") for i in range(len(colors))
    ]
    return ",".join(feedback_tokens)


def _parse_guess_row(row: dict):
    """
    Parse a guess row from either API format:
    1) legacy: {guess_word/guessWord, feedback}
    2) new: {letters: [{letter, match}, ...]}
    Returns Guess or None if row is not parseable.
    """
    letters = row.get("letters")
    if isinstance(letters, list) and letters:
        guess_word = "".join(str(item.get("letter", "")) for item in letters).strip().lower()
        token_map = {"full": "GR", "partial": "Y", "none": "G"}
        feedback_tokens = [
            token_map.get(str(item.get("match", "")).strip().lower(), "G")
            for item in letters
        ]
        feedback = ",".join(feedback_tokens)
    else:
        guess_word = str(row.get("guess_word") or row.get("guessWord") or "").strip().lower()
        feedback = str(row.get("feedback", "")).strip().upper()

    if not guess_word:
        return None

    colors = feedback_to_colors(feedback)
    if colors is None:
        colors = {str(i): "grey" for i in range(len(guess_word))}

    return Guess(guess=guess_word, colors=colors)


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
