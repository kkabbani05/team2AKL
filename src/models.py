from pydantic import BaseModel


class Guess(BaseModel):
    guess: str
    colors: dict


class Word(BaseModel):
    word: str
    guesses: list[Guess]


class Record(BaseModel):
    wins: int
    guess_count: int


class Player(BaseModel):
    name: str
    current_word_index: int
    current_word: Word | None = None
    game_in_progress: bool
    seen_words: list[Word]
    record: Record
