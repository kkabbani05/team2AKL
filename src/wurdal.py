#!/usr/bin/env python

import register_service
import board_service
import new_game_service
import guess_service
import leaderboard_service
from utils import load_players, find_player, write_players, read_in_word_list, parse_args


def main():
    registered_players = load_players()
    args = parse_args()
    word_list = read_in_word_list()

    if args.command == "register":
        register_service.register(args.player_name, registered_players)
    elif args.command == "new-game":
        new_game_service.new_game(args.player_name, registered_players, word_list)
    elif args.command == "guess":
        guess_service.guess(args.player_name, args.word, registered_players)
    elif args.command == "board":
        board_service.print_board(find_player(args.player_name, registered_players)[1])
    elif args.command == "leaderboard":
        leaderboard_service.leaderboard(registered_players)

    write_players(registered_players)


if __name__ == "__main__":
    main()
