#!/usr/bin/env python

import register_service
import board_service
import guess_service
import leaderboard_service
import login_service
from utils import (
    load_players,
    find_player,
    write_players,
    parse_args,
)


def main():
    registered_players = load_players()
    print(registered_players)
    args = parse_args()

    if args.command in ("register", "login"):
        player_name = args.player_name
    elif args.command == "logout":
        player_name = None
    else:
        try:
            with open("current_player.txt", "r") as file:
                player_name = file.read().strip() or None
        except FileNotFoundError:
            player_name = None
        if player_name is None:
            print("Please login to continue")
            return

    if args.command == "register":
        register_service.register(player_name, registered_players)
    elif args.command == "guess":
        guess_service.guess(player_name, args.word, registered_players)
    elif args.command == "board":
        board_service.print_board(
            find_player(player_name, registered_players)[1], "board"
        )
    elif args.command == "leaderboard":
        leaderboard_service.leaderboard(registered_players)
    elif args.command == "login":
        login_service.login(args.player_name, registered_players)
    elif args.command == "logout":
        login_service.logout()

    write_players(registered_players)


if __name__ == "__main__":
    main()
