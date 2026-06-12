from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.database import engine, Base, SessionLocal
from app.services.init_db import init_db
from app.admin import setup_admin
from app.routers import auth, users, teams, tasks, comments, evaluations, meetings, calendar
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version=settings.VERSION,
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router, tags=["Users"])
app.include_router(teams.router, tags=["Teams"])
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(comments.router, tags=["Comments"])
app.include_router(evaluations.router, tags=["Evaluations"])
app.include_router(meetings.router, tags=["Meetings"])
app.include_router(calendar.router, tags=["Calendar"])

setup_admin(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
