"""HTTP routes for the event log. Request models forbid unknown fields, so a client cannot send
a timestamp or any timing field."""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.events_service import Conflict, Invalid, LogNotFound

router = APIRouter()

CLIENT_EVENT_TYPES = frozenset({
    "source.add", "source.open", "source.view_span", "aid.pin_opened", "card.create",
    "card.edit", "card.delete", "card.anchor", "card.set_aside", "claim.create", "claim.edit",
    "import.declared", "editor.paste", "editor.insert_quote", "editor.insert_helper",
    "coach.outcome", "map.answer", "note.add", "link.add", "record.withdrawn",
})


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OpenLogBody(_Strict):
    log_id: str | None = None
    assignment_id: str
    consent_version: int
    mapper_enabled: bool


class LeaseBody(_Strict):
    device_id: str
    takeover: bool = False


class HeartbeatBody(_Strict):
    token: str


class BatchBody(_Strict):
    client_seq: int
    base_rev: int
    doc_rev: int
    steps: list[dict]
    input_kind: dict[str, int] = Field(default_factory=dict)
    lease_token: str


class CheckpointBody(_Strict):
    doc_rev: int
    doc_hash: str
    snapshot: dict
    lease_token: str


class SubmitBody(_Strict):
    idempotency_key: str = Field(min_length=8)
    doc_rev: int
    doc_hash: str
    snapshot: dict
    lease_token: str


class EventBody(_Strict):
    type: str
    payload: dict
    client_seq: int | None = None
    doc_rev: int | None = None


class ResubmitBody(_Strict):
    reason: str


def _svc(request: Request):
    return request.app.state.events


def install_error_handlers(app) -> None:
    @app.exception_handler(LogNotFound)
    async def _nf(_req, _exc):
        return JSONResponse({"error": "not_found"}, status_code=404)

    @app.exception_handler(Conflict)
    async def _conflict(_req, exc: Conflict):
        return JSONResponse({"error": exc.code, **exc.detail}, status_code=409)

    @app.exception_handler(Invalid)
    async def _invalid(_req, exc: Invalid):
        return JSONResponse({"error": exc.code, "message": exc.message}, status_code=422)


@router.post("/logs", status_code=201)
def open_log(body: OpenLogBody, request: Request):
    return _svc(request).open_log(body.log_id, assignment_id=body.assignment_id,
                                  consent_version=body.consent_version,
                                  mapper_enabled=body.mapper_enabled)


@router.post("/logs/{log_id}/lease")
def acquire(log_id: str, body: LeaseBody, request: Request):
    return _svc(request).acquire_lease(log_id, device_id=body.device_id, takeover=body.takeover)


@router.post("/logs/{log_id}/lease/heartbeat")
def heartbeat(log_id: str, body: HeartbeatBody, request: Request):
    return _svc(request).heartbeat(log_id, token=body.token)


@router.post("/logs/{log_id}/batches")
def batches(log_id: str, body: BatchBody, request: Request):
    return _svc(request).ack_batch(log_id, client_seq=body.client_seq, base_rev=body.base_rev,
                                   doc_rev=body.doc_rev, steps=body.steps,
                                   input_kind=body.input_kind, lease_token=body.lease_token)


@router.post("/logs/{log_id}/checkpoint")
def checkpoint(log_id: str, body: CheckpointBody, request: Request):
    return _svc(request).checkpoint(log_id, doc_rev=body.doc_rev, doc_hash=body.doc_hash,
                                    snapshot=body.snapshot, lease_token=body.lease_token)


@router.post("/logs/{log_id}/submit")
def submit(log_id: str, body: SubmitBody, request: Request):
    return _svc(request).submit(log_id, idempotency_key=body.idempotency_key,
                                doc_rev=body.doc_rev, doc_hash=body.doc_hash,
                                snapshot=body.snapshot, lease_token=body.lease_token)


@router.post("/logs/{log_id}/events")
def post_event(log_id: str, body: EventBody, request: Request):
    if body.type not in CLIENT_EVENT_TYPES:
        raise Invalid("type_not_allowed", f"Event type {body.type!r} cannot be sent here.")
    ev = _svc(request).append_event(log_id, type=body.type, actor="student",
                                    payload=body.payload, client_seq=body.client_seq,
                                    doc_rev=body.doc_rev)
    return {"event": ev}


@router.post("/logs/{log_id}/resubmit")
def resubmit(log_id: str, body: ResubmitBody, request: Request):
    return {"event": _svc(request).open_resubmission(log_id, reason=body.reason)}


@router.get("/logs/{log_id}/events")
def list_events(log_id: str, request: Request):
    return {"events": _svc(request).events(log_id)}


@router.get("/logs/{log_id}/verify")
def verify_log(log_id: str, request: Request, seal: str | None = None):
    return _svc(request).verify(log_id, seal)
