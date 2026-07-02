from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import create_database_session
from app.models import User
from app.games_guesses_router import Game, Guess

router = APIRouter()

@router.get("/")
def get_leaderboard(session: Session = Depends(create_database_session)):
    leaderboard = {
        "players": []
    }

    all_users = session.query(User).all()
    
    for user in all_users:        
        lb_player = {
            "name": user.name,
            "wins": 0,
            "losses": 0,
            "average_guesses": 0.0
        }
        all_games = session.query(Game).filter(user.id == Game.user_id)
        guess_list = []
        for game in all_games:
            if game.status == "in-progress":
                continue
            elif game.status == "won":
                lb_player["wins"] += 1
            elif game.status == "lost":
                lb_player["losses"] += 1

            all_guesses = session.query(Guess).filter(game.id == Guess.game_id)
            total_guesses = 0
            for _ in all_guesses:   # len() does not work on query
                total_guesses += 1
            guess_list.append(total_guesses)
        lb_player["average_guesses"] = get_average_guesses(guess_list)

        leaderboard.get("players").append(lb_player)

    leaderboard.get("players").sort(key=lambda player: player.get("average_guesses"))
    leaderboard.get("players").sort(key=lambda player: player.get("losses"))
    leaderboard.get("players").sort(key=lambda player: player.get("wins"), reverse=True)
    return leaderboard

def get_average_guesses(guess_count):
    if len(guess_count) == 0:
        return 0.0
    total = 0
    for n in guess_count:
        total += n
    return round((total / len(guess_count)) * 10) / 10
