from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.session_router import router as session_router

app = FastAPI()
app.include_router(session_router, prefix="/sessions", tags=["sessions"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    missing_name = any(
        error.get("type") == "missing" and "name" in error.get("loc", ())
        for error in exc.errors()
    )
    if missing_name:
        return JSONResponse(status_code=422, content={"description": "Name is required"})
    else:
        return JSONResponse(status_code=422, content={"description": "Invalid request body"})