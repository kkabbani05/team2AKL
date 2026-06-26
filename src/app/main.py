from fastapi import FastAPI
from app.session_router import router as session_router

app = FastAPI()
app.include_router(session_router, prefix="/sessions", tags=["sessions"])
