from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.core.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, comments, evaluations, meetings, tasks, teams, users, web
from app.services.init_db import init_db


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
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(web.router, tags=["Web Pages"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router, tags=["Users"])
app.include_router(teams.router, tags=["Teams"])
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(comments.router, tags=["Comments"])
app.include_router(evaluations.router, tags=["Evaluations"])
app.include_router(meetings.router, tags=["Meetings"])

setup_admin(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
