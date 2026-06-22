import pytest

from board_service import print_board, print_board_line, print_color
from models import Guess


def test_print_board_requires_active_game(player_factory, capsys):
    player = player_factory(in_progress=False)

    with pytest.raises(SystemExit) as exc:
        print_board(player)

    assert exc.value.code == 1
    assert "Error: no active game" in capsys.readouterr().out


def test_print_board_empty_state_renders_six_rows(player_factory, capsys):
    player = player_factory(in_progress=True, guesses=[])

    print_board(player)
    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 18
    assert "*****" in lines[0]


def test_print_color_returns_ansi_wrapped_content():
    out = print_color("green", "X")
    assert "\033[32m" in out
    assert out.endswith("\033[0m")


def test_print_color_rejects_unknown_color(capsys):
    with pytest.raises(SystemExit) as exc:
        print_color("blue", "X")

    assert exc.value.code == 3
    assert "Error: internal error" in capsys.readouterr().out


def test_print_board_line_renders_guess_and_colors(capsys):
    guess = Guess(
        guess="crane",
        colors={
            "0": "green",
            "1": "yellow",
            "2": "grey",
            "3": "green",
            "4": "grey",
        },
    )

    print_board_line(guess)
    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 3
    assert "c" in lines[1]
    assert "r" in lines[1]
    assert "a" in lines[1]
