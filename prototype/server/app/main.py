import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import llm
from app.events_service import EventService
from app.routes_events import install_error_handlers, router as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Boot ping (D13): a failing backend is logged for the operator; the app still starts,
    # because writing must continue when AI help is unavailable.
    app.state.llm_ping = llm.ping_backends()
    yield


def create_app(db_path: str | None = None, clock=None) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    path = db_path if db_path is not None else os.environ.get("ROOM_DB_PATH", ":memory:")
    app.state.events = EventService(path, clock)
    install_error_handlers(app)
    app.include_router(events_router)

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    return app


app = create_app()
