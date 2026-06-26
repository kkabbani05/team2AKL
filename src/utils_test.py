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


def test_load_players_reads_valid_json(monkeypatch):
    json_str = (
        '[{"name":"amy","current_word_index":-1,"current_word":null,'
        '"game_in_progress":false,"seen_words":[],"record":{"wins":1,"guess_count":2}}]'
    )

    class FakeFile:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json_str

    monkeypatch.setattr("builtins.open", lambda *_a, **_k: FakeFile())

    players = utils.load_players()

    assert len(players) == 1
    assert players[0].name == "amy"
    assert players[0].record.wins == 1


def test_load_players_creates_empty_file_if_missing(tmp_path, monkeypatch):
    players_path = tmp_path / "players.json"
    original_open = open

    def redirected_open(path, mode="r", *args, **kwargs):
        if Path(path).as_posix() == "../players.json":
            return original_open(players_path, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", redirected_open)

    players = utils.load_players()

    assert players == []
    assert players_path.read_text() == "[]"


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
            current_word_index=-1,
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


def test_load_players_invalid_json_prints_error(monkeypatch, capsys):
    class FakeFile:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return "not-json"

    monkeypatch.setattr("builtins.open", lambda *_a, **_k: FakeFile())

    result = utils.load_players()

    assert result is None
    assert "Error: Invalid Json" in capsys.readouterr().out


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
