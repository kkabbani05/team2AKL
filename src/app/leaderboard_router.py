from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import create_database_session
from app.models import User

import random   # Generate random wins and losses for users

router = APIRouter()

@router.get("/")
def get_leaderboard(session: Session = Depends(create_database_session)):
    leaderboard = {
        "players": []
    }

    all_users = session.query(User).all()
    for user in all_users:
        wins = random.randint(0, 10)
        lb_player = {
            "name": user.name,
            "wins": wins,
            "losses": random.randint(0, 20),
            "average_guesses": get_average_guesses([random.randint(1, 6) for _ in range(wins)])
        }
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
