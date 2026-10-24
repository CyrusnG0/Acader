from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import llm


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Boot ping (D13): a failing backend is logged for the operator; the app still starts,
    # because writing must continue when AI help is unavailable.
    app.state.llm_ping = llm.ping_backends()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}
