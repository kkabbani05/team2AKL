from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, create_database_session
from app.games_guesses_router import Game, Guess
from app.main import app
from app.session_router import User


def _build_test_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_create_database_session():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[create_database_session] = override_create_database_session
    return TestClient(app)


def _seed_board_data(client: TestClient):
    session_generator = app.dependency_overrides[create_database_session]()
    session = next(session_generator)
    try:
        session.add(User(id=33, name="Tom"))
        session.add(Game(id=1, user_id=33, word_to_guess="planet", status="in_progress"))
        session.add(Guess(game_id=1, attempt_no=1, guess_word="planes", feedback="GR,GR,GR,GR,GR,YE"))
        session.add(Guess(game_id=1, attempt_no=2, guess_word="planet", feedback="GR,GR,GR,GR,GR,GR"))
        session.commit()
    finally:
        session.close()


def test_get_player_board_success_includes_length_and_guesses():
    client = _build_test_client()
    _seed_board_data(client)

    response = client.get("/players/33/board", headers={"Authorization": "Bearer 33"})

    assert response.status_code == 200
    assert response.json() == {
        "user": {"id": 33, "name": "Tom"},
        "current": {
            "length": 6,
            "guesses": [
                {
                    "attemptNo": 1,
                    "guessWord": "planes",
                    "feedback": "GR,GR,GR,GR,GR,YE",
                },
                {
                    "attemptNo": 2,
                    "guessWord": "planet",
                    "feedback": "GR,GR,GR,GR,GR,GR",
                },
            ],
        },
    }


def test_get_player_board_missing_auth_header_returns_access_denied():
    client = _build_test_client()
    _seed_board_data(client)

    response = client.get("/players/33/board")

    assert response.status_code == 403
    assert response.json() == {"error": {"description": "Access denied"}}


def test_get_player_board_invalid_auth_token_returns_access_denied():
    client = _build_test_client()
    _seed_board_data(client)

    response = client.get(
        "/players/33/board", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 403
    assert response.json() == {"error": {"description": "Access denied"}}
