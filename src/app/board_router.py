from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi_camelcase import CamelModel

from app.database import create_database_session
from app.games_guesses_router import Game, Guess
from app.session_router import User

router = APIRouter()


class BoardGuessRead(CamelModel):
    attempt_no: int
    guess_word: str
    feedback: str


class BoardCurrentRead(CamelModel):
    length: int
    guesses: list[BoardGuessRead]


class BoardUserRead(CamelModel):
    id: int
    name: str


class BoardRead(CamelModel):
    user: BoardUserRead
    current: BoardCurrentRead


@router.get("/players/{user_id}/board", response_model=BoardRead)
def get_player_board(
    user_id: int,
    authorization: str | None = Header(default=None),
    session: Session = Depends(create_database_session),
):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=403,
            content={"error": {"description": "Access denied"}},
        )

    token = authorization.split(" ", 1)[1].strip()
    if token != str(user_id):
        return JSONResponse(
            status_code=403,
            content={"error": {"description": "Access denied"}},
        )

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")

    current_game = (
        session.query(Game)
        .filter(Game.user_id == user_id, Game.status == "in_progress")
        .order_by(Game.id.desc())
        .first()
    )
    if not current_game:
        current_game = (
            session.query(Game)
            .filter(Game.user_id == user_id)
            .order_by(Game.id.desc())
            .first()
        )
    # if not current_game:
    # # Auto-create a new game
    #     import random
    #     from pathlib import Path
        
    #     word_list_path = Path(__file__).parent.parent / "word_list.txt"
    #     with open(word_list_path) as f:
    #         words = [line.strip() for line in f if line.strip()]
        
    #     word = random.choice(words)
    #     current_game = Game(user_id=user_id, word_to_guess=word, status="in_progress")
    #     session.add(current_game)
    #     session.commit()
    if not current_game:
        raise HTTPException(status_code=404, detail="No games found for this user")

    guesses = (
        session.query(Guess)
        .filter(Guess.game_id == current_game.id)
        .order_by(Guess.attempt_no.asc())
        .all()
    )

    return {
        "user": {"id": user.id, "name": user.name},
        "current": {
            "length": len(current_game.word_to_guess),
            "guesses": [
                {
                    "attempt_no": guess.attempt_no,
                    "guess_word": guess.guess_word,
                    "feedback": guess.feedback,
                }
                for guess in guesses
            ],
        },
    }
