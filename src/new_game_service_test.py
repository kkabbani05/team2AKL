import pytest

import new_game_service
from models import Word


def test_new_game_requires_existing_player(capsys):
    with pytest.raises(SystemExit) as exc:
        new_game_service.new_game("missing", [], ["apple"])

    assert exc.value.code == 1
    assert "Error: player not found" in capsys.readouterr().out


def test_new_game_rejects_existing_active_game(player_factory, capsys):
    players = [player_factory(name="amy", in_progress=True)]

    with pytest.raises(SystemExit) as exc:
        new_game_service.new_game("amy", players, ["apple", "berry"])

    assert exc.value.code == 1
    assert "Error: game in progress" in capsys.readouterr().out


def test_new_game_rejects_when_no_words_available(player_factory, capsys):
    seen = [Word(word="apple", guesses=[]), Word(word="berry", guesses=[])]
    players = [
        player_factory(
            name="amy",
            in_progress=False,
            seen_words=seen,
            word="apple",
            current_word_index=0,
        )
    ]

    with pytest.raises(SystemExit) as exc:
        new_game_service.new_game("amy", players, ["apple", "berry"])

    assert exc.value.code == 1
    assert "Error: no words available" in capsys.readouterr().out


def test_new_game_starts_and_prints_board(player_factory, monkeypatch, capsys):
    players = [player_factory(name="amy", in_progress=False, seen_words=[])]
    words = ["apple", "berry", "charm"]

    def fake_select_word(player, word_list):
        player.current_word = Word(word=word_list[1], guesses=[])
        player.seen_words.append(player.current_word)
        return 1

    board_calls = {"count": 0}

    def fake_print_board(_player):
        board_calls["count"] += 1

    monkeypatch.setattr(new_game_service, "select_word", fake_select_word)
    monkeypatch.setattr(new_game_service, "print_board", fake_print_board)

    new_game_service.new_game("amy", players, words)

    assert players[0].current_word_index == 1
    assert players[0].game_in_progress is True
    assert players[0].current_word.word == "berry"
    assert board_calls["count"] == 1
    assert "New game started" in capsys.readouterr().out


def test_select_word_skips_previously_seen_word(player_factory, monkeypatch):
    player = player_factory(name="amy", in_progress=False, seen_words=[], word=None)
    player.seen_words = [Word(word="apple", guesses=[])]

    picks = iter([0, 0, 1])
    monkeypatch.setattr(new_game_service.random, "randint", lambda _a, _b: next(picks))

    idx = new_game_service.select_word(player, ["apple", "berry"])

    assert idx == 1
    assert player.current_word.word == "berry"
    assert player.seen_words[-1].word == "berry"
