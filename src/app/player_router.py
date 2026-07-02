import random
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi_camelcase import CamelModel

from app.database import create_database_session
from app.models import User, UserCreate, UserRead
from app.games_guesses_router import Game, Guess

router = APIRouter()


class PlayerGuessCreate(CamelModel):
    guess: str


class PlayerBoardGuessRead(CamelModel):
    attempt_no: int
    guess_word: str
    feedback: str


class PlayerGuessRead(CamelModel):
    length: int
    guesses: list[PlayerBoardGuessRead]
    result: str
    secret_word: str | None = None
    new_game_started: bool


def _word_list_path() -> Path:
    return Path(__file__).resolve().parent.parent / "word_list.txt"


def _read_word_list() -> list[str]:
    path = _word_list_path()
    with path.open("r") as f:
        return [line.strip().upper() for line in f if line.strip()]


def _feedback_from_guess(secret_word: str, guess_word: str) -> str:
    secret = secret_word.upper()
    guess = guess_word.upper()

    tally = {}
    for char in secret:
        tally[char] = tally.get(char, 0) + 1

    feedback = ["G"] * len(secret)

    for i, char in enumerate(guess):
        if char == secret[i]:
            feedback[i] = "GR"
            tally[char] -= 1

    for i, char in enumerate(guess):
        if feedback[i] == "GR":
            continue
        if tally.get(char, 0) > 0:
            feedback[i] = "Y"
            tally[char] -= 1

    return ",".join(feedback)


def _choose_next_word(session: Session, user_id: int) -> str | None:
    all_words = _read_word_list()
    if not all_words:
        return None

    used_words = {
        str(word).strip().upper()
        for (word,) in session.query(Game.word_to_guess)
        .filter(Game.user_id == user_id)
        .all()
    }

    remaining_words = [word for word in all_words if word not in used_words]
    if not remaining_words:
        return None

    return random.choice(remaining_words)


@router.post("/", response_model=UserRead, status_code=201)
def register_user(
    user: UserCreate, session: Session = Depends(create_database_session)
):
    username = user.name.strip().lower()
    if len(username) == 0:
        raise HTTPException(status_code=422, detail="Name cannot be empty")

    all_users = session.query(User).all()
    for db_user in all_users:
        if username == db_user.name.strip().lower():
            raise HTTPException(status_code=422, detail="Username is already taken")

    new_db_user = User(**user.model_dump())
    session.add(new_db_user)
    session.commit()
    session.refresh(new_db_user)
    return new_db_user


@router.get("/", response_model=list[UserRead])
def get_registered_users(session: Session = Depends(create_database_session)):
    return session.query(User).all()


@router.post("/{user_id}/guess", response_model=PlayerGuessRead)
def submit_guess(
    user_id: int,
    payload: PlayerGuessCreate,
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

    game = (
        session.query(Game)
        .filter(Game.user_id == user_id, Game.status == "in_progress")
        .order_by(Game.id.desc())
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="No active game")

    normalized_guess = payload.guess.strip().lower()
    expected_length = len(game.word_to_guess)
    if len(normalized_guess) != expected_length:
        return JSONResponse(
            status_code=422,
            content={"error": {"description": f"Guess must be exactly {expected_length} letters"}},
        )
    if not normalized_guess.isalpha():
        raise HTTPException(
            status_code=422,
            detail="Guess must contain only letters",
        )

    guesses = (
        session.query(Guess)
        .filter(Guess.game_id == game.id)
        .order_by(Guess.attempt_no.asc())
        .all()
    )

    attempt_no = len(guesses) + 1
    feedback = _feedback_from_guess(game.word_to_guess, normalized_guess)
    db_guess = Guess(
        game_id=game.id,
        attempt_no=attempt_no,
        guess_word=normalized_guess,
        feedback=feedback,
    )
    session.add(db_guess)

    win = normalized_guess.upper() == str(game.word_to_guess).strip().upper()
    loss = not win and attempt_no >= 6
    result = "in_progress"

    if win:
        game.status = "won"
        result = "won"
    elif loss:
        game.status = "loss"
        result = "loss"

    new_game_started = False
    if win or loss:
        next_word = _choose_next_word(session, user_id)
        if next_word:
            session.add(
                Game(
                    user_id=user_id,
                    word_to_guess=next_word,
                    status="in_progress",
                )
            )
            new_game_started = True

    session.commit()

    latest_guesses = (
        session.query(Guess)
        .filter(Guess.game_id == game.id)
        .order_by(Guess.attempt_no.asc())
        .all()
    )

    return {
        "length": expected_length,
        "guesses": [
            {
                "attempt_no": row.attempt_no,
                "guess_word": row.guess_word,
                "feedback": row.feedback,
            }
            for row in latest_guesses
        ],
        "result": result,
        "secret_word": str(game.word_to_guess).strip().upper()
        if (win or loss)
        else None,
        "new_game_started": new_game_started,
    }
