import pytest

from register_service import register


def test_register_rejects_empty_name(capsys):
    with pytest.raises(SystemExit) as exc:
        register("", [])

    assert exc.value.code == 1
    assert "Error: invalid player name" in capsys.readouterr().out


def test_register_rejects_duplicate_name(player_factory, capsys):
    registered_players = [player_factory(name="alice", in_progress=False)]

    with pytest.raises(SystemExit) as exc:
        register("alice", registered_players)

    assert exc.value.code == 1
    assert "Error: player already exists" in capsys.readouterr().out


def test_register_rejects_invalid_characters(capsys):
    with pytest.raises(SystemExit) as exc:
        register("bad name!", [])

    assert exc.value.code == 1
    assert "Error: invalid player name" in capsys.readouterr().out


def test_register_appends_new_player():
    registered_players = []

    register("new_player", registered_players)

    assert len(registered_players) == 1
    player = registered_players[0]
    assert player.get("name") == "new_player"
    assert player.current_word_index == -1
    assert player.game_in_progress is False
    assert player.seen_words == []
    assert player.record.wins == 0
    assert player.record.guess_count == 0
