from leaderboard_service import leaderboard, player_sort


def test_player_sort_orders_by_wins_then_name(player_factory):
    players = [
        player_factory(name="bob", wins=2, in_progress=False),
        player_factory(name="amy", wins=2, in_progress=False),
        player_factory(name="zed", wins=1, in_progress=False),
    ]

    sorted_players = player_sort(players)

    assert [p.name for p in sorted_players] == ["amy", "bob", "zed"]


def test_leaderboard_shows_no_wins_message(player_factory, capsys):
    players = [
        player_factory(name="amy", wins=0, in_progress=False),
        player_factory(name="bob", wins=0, in_progress=False),
    ]

    leaderboard(players)
    out = capsys.readouterr().out

    assert "Leaderboard" in out
    assert "No wins yet." in out


def test_leaderboard_prints_rankings(player_factory, capsys):
    players = [
        player_factory(name="amy", wins=3, in_progress=False),
        player_factory(name="bob", wins=1, in_progress=False),
    ]

    leaderboard(players)
    out = capsys.readouterr().out

    assert "1. amy - wins: 3" in out
    assert "2. bob - wins: 1" in out
