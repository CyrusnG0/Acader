import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import llm
from app.compile_jobs import CompileJobs
from app.events_service import EventService
from app.jobs import JobRunner
from app.lifecycle import ReceiptLifecycle
from app.routes_events import install_error_handlers, router as events_router


def _unconfigured(log_id: str):
    raise RuntimeError("sources_for is not configured on this app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Boot ping (D13): a failing backend is logged for the operator; the app still starts,
    # because writing must continue when AI help is unavailable.
    app.state.llm_ping = llm.ping_backends()
    app.state.jobs.reconcile()
    stop = threading.Event()
    thread = None
    if app.state.job_loop:
        handlers = dict(app.state.jobs.handlers())
        if app.state.lifecycle is not None:
            handlers.update(app.state.lifecycle.handlers())

        def loop():
            runner = JobRunner(app.state.jobs.queue, handlers, worker_id="compile")
            while not stop.is_set():
                runner.run_pending()
                stop.wait(2.0)
        thread = threading.Thread(target=loop, name="room-jobs", daemon=True)
        thread.start()
    try:
        yield
    finally:
        stop.set()
        if thread is not None:
            thread.join()


def create_app(db_path: str | None = None, clock=None, *, sources_for=None,
               start_job_loop=None, deadline_for=None, scope_for=None, identity_for=None,
               enable_lifecycle=None) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    path = db_path if db_path is not None else os.environ.get("ROOM_DB_PATH", ":memory:")
    app.state.events = EventService(path, clock)
    # Every submit schedules durable work, even when no source text is configured yet.
    app.state.jobs = CompileJobs(app.state.events,
                                 sources_for=sources_for or _unconfigured)
    app.state.identity_for = identity_for
    # Release and withdrawal need a deadline and record scope. Until an assignment/roster
    # layer supplies them, the lifecycle is attached only when the app is given them (or
    # explicitly asked). Existing apps keep the previous compile-only scheduling.
    wanted = enable_lifecycle
    if wanted is None:
        wanted = deadline_for is not None or scope_for is not None
    app.state.lifecycle = None
    if wanted:
        app.state.lifecycle = ReceiptLifecycle(
            app.state.events, queue=app.state.jobs.queue, receipts=app.state.jobs.receipts,
            deadline_for=deadline_for, scope_for=scope_for)
        app.state.jobs.add_questions_hook(app.state.lifecycle.questions_ready)
    if sources_for is None:
        app.state.job_loop = False
    elif start_job_loop is None:
        app.state.job_loop = os.environ.get("ROOM_JOB_LOOP") == "1"
    else:
        app.state.job_loop = bool(start_job_loop)
    install_error_handlers(app)
    app.include_router(events_router)

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    return app


app = create_app()
