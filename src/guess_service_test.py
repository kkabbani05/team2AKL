import pytest

import guess_service
from models import Guess


def test_guess_requires_existing_player(capsys):
    with pytest.raises(SystemExit) as exc:
        guess_service.guess("missing", "crane", [])

    assert exc.value.code == 1
    assert "Error: player not found" in capsys.readouterr().out


def test_guess_requires_active_game(player_factory, capsys):
    players = [player_factory(name="amy", in_progress=False)]

    with pytest.raises(SystemExit) as exc:
        guess_service.guess("amy", "crane", players)

    assert exc.value.code == 1
    assert "Error: no active game" in capsys.readouterr().out


def test_guess_validation_rejects_wrong_length(capsys):
    with pytest.raises(SystemExit) as exc:
        guess_service.guess_validation("cat", "crane")

    assert exc.value.code == 1
    assert "Error: invalid guess" in capsys.readouterr().out


def test_guess_validation_rejects_non_alpha(capsys):
    with pytest.raises(SystemExit) as exc:
        guess_service.guess_validation("ab12e", "crane")

    assert exc.value.code == 1
    assert "Error: invalid guess" in capsys.readouterr().out


def test_guess_win_updates_record_and_ends_game(player_factory, monkeypatch, capsys):
    player = player_factory(
        name="amy",
        word="crane",
        guesses=[],
        in_progress=True,
        wins=1,
        guess_count=2,
    )
    players = [player]

    monkeypatch.setattr(guess_service, "print_board", lambda _player: None)

    guess_service.guess("amy", "crane", players)

    updated = players[0]
    assert updated.record.wins == 2
    assert updated.record.guess_count == 3
    assert updated.game_in_progress is False
    assert len(updated.current_word.guesses) == 1
    assert all(c == "green" for c in updated.current_word.guesses[0].colors.values())
    assert "amy solved it in 1 guesses!" in capsys.readouterr().out


def test_guess_loss_on_sixth_attempt_updates_stats(player_factory, monkeypatch):
    existing_guesses = [
        Guess(guess="aaaaa", colors={str(i): "grey" for i in range(5)}) for _ in range(5)
    ]
    player = player_factory(
        name="amy",
        word="crane",
        guesses=existing_guesses,
        in_progress=True,
        wins=2,
        guess_count=4,
    )
    players = [player]

    monkeypatch.setattr(guess_service, "print_board", lambda _player: None)

    guess_service.guess("amy", "zzzzz", players)

    updated = players[0]
    assert updated.record.wins == 2
    assert updated.record.guess_count == 10
    assert updated.game_in_progress is False
    assert len(updated.current_word.guesses) == 6


def test_guess_duplicate_letter_coloring(player_factory, monkeypatch):
    player = player_factory(name="amy", word="apple", guesses=[], in_progress=True)
    players = [player]
    monkeypatch.setattr(guess_service, "print_board", lambda _player: None)

    guess_service.guess("amy", "allee", players)

    colors = players[0].current_word.guesses[0].colors
    assert colors == {
        "0": "green",
        "1": "yellow",
        "2": "grey",
        "3": "grey",
        "4": "green",
    }
