from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from fastapi_camelcase import CamelModel
from fastapi.responses import JSONResponse

from app.database import Base, create_database_session
from app.utils import calculate_feedback
from app.session_router import User

router = APIRouter()


class Game(Base):
    __tablename__ = "games"

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


class GuessCreate(CamelModel):
    game_id: int
    attempt_no: int
    guess_word: str
    feedback: str

class GuessRead(GuessCreate):
    id: int

class PlayerGuessCreate(CamelModel):
    guess: str

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
    db_game = Game(
        user_id=game.user_id,
        word_to_guess=game.word_to_guess,
        status=game.status,
    )
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


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
    session.commit()
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
    #use the game_id in the guesses table and count how many columns there are 
    attempt_count = session.query(Guess).filter(Guess.game_id == current_game.id).count()
    if (attempt_count >= 6):
        return "Cannot have an inprogress game with six guesses"
    game_id = current_game.id
    attempt_no = attempt_count + 1 
    guess_word = guess.guess

    #get current word, compare against  
    correct_word = current_game.word_to_guess
    not_actual_feedback = calculate_feedback(correct_word, guess_word)
    feedback = ""
    for i in range(len(guess_word)):
        feedback+= not_actual_feedback[str(i)] + ","

    feedback = feedback[:-1]
    print(feedback)
    letters = [{"letter": guess_word[i], "match": matches} 
           for i, matches in enumerate(feedback.split(","))]
    print(letters)

    #put game_id, attmept_no, guess_word, and feedback in the guesses table 
    # db_guess = Guess(
    #     game_id=game_id,
    #     attempt_no=attempt_no,
    #     guess_word=guess_word,
    #     feedback=feedback,
    # )
    # session.add(db_guess)
    # session.commit()

    return "yo mama"