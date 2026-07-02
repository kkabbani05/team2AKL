import pytest


@pytest.fixture
def player_factory():
    from models import Player, Record, Word

    def _make_player(
        name="alice",
        word="crane",
        guesses=None,
        in_progress=True,
        seen_words=None,
        wins=0,
        guess_count=0,
    ):
        if guesses is None:
            guesses = []

        current_word = None
        if word is not None:
            current_word = Word(word=word, guesses=guesses)

        if seen_words is None:
            seen_words = []
            if current_word is not None:
                seen_words.append(current_word)

        return Player(
            name=name,
            current_word=current_word,
            game_in_progress=in_progress,
            seen_words=seen_words,
            record=Record(wins=wins, guess_count=guess_count),
        )

    return _make_player
