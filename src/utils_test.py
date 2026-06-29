import argparse
from pathlib import Path

import pytest

import utils
from models import Player, Record, Word


def test_argument_parser_error_exits_with_code_2():
    parser = utils.WurdalArgumentParser(prog="wurdal")

    with pytest.raises(SystemExit) as exc:
        parser.error("boom")

    assert exc.value.code == 2


def test_read_in_word_list_reads_words(monkeypatch):
    expected = ["apple", "berry"]

    class FakeFile:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return "apple\nberry"

    monkeypatch.setattr("builtins.open", lambda *_a, **_k: FakeFile())

    assert utils.read_in_word_list() == expected


def test_read_in_word_list_file_not_found(monkeypatch, capsys):
    def fail_open(*_args, **_kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", fail_open)

    with pytest.raises(SystemExit) as exc:
        utils.read_in_word_list()

    assert exc.value.code == 3
    assert "Word list not found." in capsys.readouterr().out


def test_parse_args_register(monkeypatch):
    monkeypatch.setattr("sys.argv", ["wurdal", "register", "amy"])

    args = utils.parse_args()

    assert args.command == "register"
    assert args.player_name == "amy"


def test_parse_args_leaderboard_flag(monkeypatch):
    monkeypatch.setattr("sys.argv", ["wurdal", "leaderboard", "--by-games"])

    args = utils.parse_args()

    assert args.command == "leaderboard"
    assert args.by_games is True


def test_load_players_builds_players_from_db(monkeypatch):
    users = [{"name": "amy", "id": 1}]
    games = [
        {"id": 10, "user_id": 1, "word_to_guess": "PLANT", "status": "completed"},
        {"id": 11, "user_id": 1, "word_to_guess": "TRACK", "status": "in_progress"},
    ]
    guesses = {
        10: [
            {"attempt_no": 1, "guess_word": "STARE", "feedback": "G,G,Y,G,G"},
            {"attempt_no": 2, "guess_word": "PLANT", "feedback": "GR,GR,GR,GR,GR"},
        ],
        11: [
            {"attempt_no": 1, "guess_word": "SLATE", "feedback": "G,Y,G,G,G"},
        ],
    }

    class FakeResponse:
        def __init__(self, payload, status_code=200):
            self._payload = payload
            self.status_code = status_code

        def json(self):
            return self._payload

    def fake_get(url, params=None):
        if url.endswith("/sessions"):
            return FakeResponse(users)
        if url.endswith("/games"):
            return FakeResponse(games)
        if url.endswith("/guesses"):
            return FakeResponse(guesses[params["game_id"]])
        return FakeResponse(None, status_code=404)

    monkeypatch.setattr(utils.requests, "get", fake_get)

    players = utils.load_players()

    assert len(players) == 1
    player = players[0]
    assert player.name == "amy"
    assert player.record.wins == 1
    assert player.record.guess_count == 2
    assert player.game_in_progress is True
    assert player.current_word.word == "track"
    assert len(player.seen_words) == 2
    assert player.current_word.guesses[0].colors == {
        "0": "grey",
        "1": "yellow",
        "2": "grey",
        "3": "grey",
        "4": "grey",
    }


def test_load_players_returns_empty_on_server_error(monkeypatch):
    class FakeResponse:
        status_code = 500

        def json(self):
            return None

    monkeypatch.setattr(utils.requests, "get", lambda *_a, **_k: FakeResponse())

    assert utils.load_players() == []


def test_write_players_writes_json(tmp_path, monkeypatch):
    players_path = tmp_path / "players.json"
    original_open = open

    def redirected_open(path, mode="r", *args, **kwargs):
        if Path(path).as_posix() == "../players.json":
            return original_open(players_path, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", redirected_open)

    players = [
        Player(
            name="amy",
            current_word=None,
            game_in_progress=False,
            seen_words=[],
            record=Record(wins=2, guess_count=5),
        )
    ]

    utils.write_players(players)
    content = players_path.read_text()

    assert '"name": "amy"' in content
    assert '"wins": 2' in content


def test_load_players_handles_connection_error(monkeypatch, capsys):
    def fail_get(*_args, **_kwargs):
        raise utils.requests.exceptions.ConnectionError

    monkeypatch.setattr(utils.requests, "get", fail_get)

    result = utils.load_players()

    assert result == []
    assert "Could not connect to the server." in capsys.readouterr().out


def test_find_player_returns_index_and_player(player_factory):
    players = [player_factory(name="amy"), player_factory(name="bob")]

    idx, player = utils.find_player("bob", players)

    assert idx == 1
    assert player.get("name") == "bob"


def test_player_to_list_replaces_player(player_factory):
    players = [player_factory(name="amy", wins=0), player_factory(name="bob", wins=0)]
    replacement = player_factory(name="bob", wins=3)

    returned = utils.player_to_list(replacement, 1, players)

    assert returned.name == "bob"
    assert returned.record.wins == 3
    assert players[1].record.wins == 3
