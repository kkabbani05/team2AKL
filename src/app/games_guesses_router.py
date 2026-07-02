from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy import UniqueConstraint, text
from sqlalchemy.exc import IntegrityError
from fastapi_camelcase import CamelModel
from fastapi.responses import JSONResponse

from app.database import Base, create_database_session
from app.utils import calculate_feedback
from app.session_router import User
from pathlib import Path

router = APIRouter()


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        UniqueConstraint("user_id", "word_to_guess", name="uix_user_word_to_guess"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_to_guess = Column(String(length=50), nullable=False)
    status = Column(String(length=50), nullable=False)
    guesses = relationship("Guess", back_populates="game")


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    attempt_no = Column(Integer, nullable=False)
    guess_word = Column(String(length=50), nullable=False)
    feedback = Column(String(length=50), nullable=False)
    game = relationship("Game", back_populates="guesses")


class GameCreate(CamelModel):
    user_id: int
    word_to_guess: str
    status: str


class GameRead(GameCreate):
    id: int


class GameStatusUpdate(CamelModel):
    status: str


class GuessCreate(CamelModel):
    game_id: int
    attempt_no: int
    guess_word: str
    feedback: str

class GuessRead(GuessCreate):
    id: int

class PlayerGuessCreate(CamelModel):
    guess: str

def repair_guesses_id_sequence(session: Session) -> None:
    session.execute(
        text(
            """
            SELECT setval(
                pg_get_serial_sequence('guesses', 'id'),
                COALESCE((SELECT MAX(id) FROM guesses), 0)
            )
            """
        )
    )
    session.commit()

def create_new_game_for_user(session: Session, user_id: int) -> Game:
    word_list_path = Path(__file__).parent.parent / "word_list.txt"
    with word_list_path.open() as f:
        words = [line.strip().upper() for line in f if line.strip()]

    # optional: avoid reusing words this user already had
    used_words = {
        g.word_to_guess
        for g in session.query(Game).filter(Game.user_id == user_id).all()
    }
    available_words = [w for w in words if w not in used_words]
    if not available_words:
        raise HTTPException(status_code=422, detail="No unused words available for this player")

    new_game = Game(
        user_id=user_id,
        word_to_guess=available_words[0],
        status="in_progress",
    )
    session.add(new_game)
    session.commit()
    session.refresh(new_game)
    return new_game

# Games Endpoints
@router.get("/games", response_model=list[GameRead])
def get_all_games(
    user_id: int = None, session: Session = Depends(create_database_session)
):
    query = session.query(Game)
    if user_id:
        query = query.filter(Game.user_id == user_id)
    return query.all()


@router.get("/games/{game_id}", response_model=GameRead)
def get_game(game_id: int, session: Session = Depends(create_database_session)):
    game = session.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/games", response_model=GameRead)
def create_game(game: GameCreate, session: Session = Depends(create_database_session)):
    word_to_guess = game.word_to_guess.strip().upper()
    existing_game = (
        session.query(Game)
        .filter(Game.user_id == game.user_id, Game.word_to_guess == word_to_guess)
        .first()
    )
    if existing_game:
        raise HTTPException(status_code=422, detail="Word already used for this player")

    db_game = Game(
        user_id=game.user_id,
        word_to_guess=word_to_guess,
        status=game.status,
    )
    session.add(db_game)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=422, detail="Word already used for this player")
    session.refresh(db_game)
    return db_game


@router.put("/games/{game_id}", response_model=GameRead)
def update_game_status(
    game_id: int,
    payload: GameStatusUpdate,
    session: Session = Depends(create_database_session),
):
    game = session.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game.status = payload.status
    session.commit()
    session.refresh(game)
    return game


# Guesses Endpoints
@router.get("/guesses", response_model=list[GuessRead])
def get_all_guesses(
    game_id: int = None, session: Session = Depends(create_database_session)
):
    query = session.query(Guess)
    if game_id:
        query = query.filter(Guess.game_id == game_id)
    return query.all()


@router.get("/guesses/{guess_id}", response_model=GuessRead)
def get_guess(guess_id: int, session: Session = Depends(create_database_session)):
    guess = session.query(Guess).filter(Guess.id == guess_id).first()
    if not guess:
        raise HTTPException(status_code=404, detail="Guess not found")
    return guess


@router.post("/guesses", response_model=GuessRead)
def create_guess(
    guess: GuessCreate, session: Session = Depends(create_database_session)
):
    # Verify game exists
    game = session.query(Game).filter(Game.id == guess.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    db_guess = Guess(
        game_id=guess.game_id,
        attempt_no=guess.attempt_no,
        guess_word=guess.guess_word,
        feedback=guess.feedback,
    )
    session.add(db_guess)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=422, detail="Attempt number already used for this game")
    session.refresh(db_guess)
    return db_guess

@router.post("/players/{user_id}/guess")
def make_guess(
    user_id: int, 
    guess: PlayerGuessCreate,
    authorization: str | None = Header(default=None),
    session: Session = Depends(create_database_session)
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
    current_game = session.query(Game).filter(Game.user_id == user_id, Game.status == "in_progress").order_by(Game.id.desc()).first()
    
    if not current_game: # create a new game 
        current_game = create_new_game_for_user(session, user_id)

    
    #use the game_id in the guesses table and count how many columns there are 
    attempt_count = session.query(Guess).filter(Guess.game_id == current_game.id).count()
    if (attempt_count >= 6):
        return "Cannot have an inprogress game with six guesses"
    game_id = current_game.id
    attempt_no = attempt_count + 1 
    guess_word = guess.guess.lower()
    print(guess_word)

    #get current word, compare against  
    correct_word = current_game.word_to_guess.lower()
    print(correct_word)
    if len(guess_word) != len(correct_word):
        raise HTTPException(status_code=422, detail="Invalid, guess length should be same as word length")
    not_actual_feedback = calculate_feedback(correct_word, guess_word)
    
    feedback = ""
    for i in range(len(guess_word)):
        feedback+= not_actual_feedback[str(i)] + ","

    feedback = feedback[:-1]
    print("feedback")
    print(feedback)
    letters = [{"letter": guess_word[i].upper(), "match": matches} 
           for i, matches in enumerate(feedback.split(","))]
    print("letters")
    print(letters)

    #put game_id, attmept_no, guess_word, and feedback in the guesses table 
    db_guess = Guess(
        game_id=game_id,
        attempt_no=attempt_no,
        guess_word=guess_word,
        feedback=feedback,
    )
    session.add(db_guess)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()

        # Auto-repair only for duplicate primary-key sequence drift
        exc_text = str(exc)
        if "guesses_pkey" in exc_text or "duplicate key value violates unique constraint" in exc_text:
            repair_guesses_id_sequence(session)

            # Recreate object after rollback and retry once
            db_guess = Guess(
                game_id=game_id,
                attempt_no=attempt_no,
                guess_word=guess_word,
                feedback=feedback,
            )
            session.add(db_guess)
            session.commit()
        else:
            raise
    session.refresh(db_guess)

    all_guesses = (
        session.query(Guess)
        .filter(Guess.game_id == current_game.id)
        .order_by(Guess.attempt_no.asc())
        .all()
    )
    guesses_payload = []
    print(all_guesses)
    for g in all_guesses:
        match_codes = [m.strip() for m in g.feedback.split(",")]

        letters_payload = []
        for i, ch in enumerate(g.guess_word):
            letters_payload.append({
                "letter": ch.upper(),
                "match": match_codes[i],  # "full" / "partial" / "none"
            })

        guesses_payload.append({
            "letters": letters_payload
        })

    if current_game:
        print({
            "id": current_game.id,
            "user_id": current_game.user_id,
            "word_to_guess": current_game.word_to_guess,
            "status": current_game.status,
        })
    else:
        print("No current game found")

    status = ""
    status_to_store = ""
    word = None 

    if (guess_word.lower() == correct_word.lower()):
        status = "won"
        status_to_store = "won"
        word = correct_word.upper()
        current_game.status = "won"
        session.commit()
        session.refresh(current_game)

        new_game = create_new_game_for_user(session, user_id)
    else:
        if (attempt_no == 6): 
            status = "lost"
            status_to_store = "lost"
            current_game.status = "lost"
            session.commit()
            session.refresh(current_game)
        else:
            status = "in-progress"
            status_to_store = "in_progress"

    if (status == "lost"):
        return {
            "current": {
                "result": {
                    "status": status,
                    "word": correct_word.upper()
                }
            }
        }
    
    return {
        "user": {
            "id": user.id,
            "name": user.name,
        },
        "current": {
            "length": len(guess_word),
            "guesses": guesses_payload,
            "result": {
                "status": status,
                "word": word,
            },
        },
    }
