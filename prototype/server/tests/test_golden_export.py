"""The local review export preserves compiled results and labels its extra context."""
from __future__ import annotations

import json

import pytest

from engine.events import canonical_json, sha256_hex
from golden import export as exporting
from golden.__main__ import main
from golden.build import BuildError, build_session
from golden.script import list_sessions


@pytest.fixture(scope="module")
def gallery():
    return exporting.export_gallery()


def test_export_has_every_real_golden_in_alphabetical_sample_name_order(gallery):
    assert gallery["schema_version"] == 1
    assert gallery["synthetic"] is True
    rows = gallery["sessions"]
    assert len(rows) == 12
    assert sorted(row["session_id"] for row in rows) == list_sessions()
    names = [row["view_context"]["header"]["student_name"] for row in rows]
    assert names == sorted(names, key=str.casefold)
    assert len(set(names)) == len(names)
    assert names == [f"Sample writer {n:02d}" for n in range(1, 13)]


@pytest.mark.parametrize("session_id", list_sessions())
def test_export_receipt_and_hash_are_unmodified_compiler_output(gallery, session_id):
    row = next(row for row in gallery["sessions"] if row["session_id"] == session_id)
    actual = build_session(session_id)
    assert canonical_json(row["receipt"]) == canonical_json(actual.receipt)
    assert row["receipt_hash"] == actual.receipt_hash
    assert sha256_hex(canonical_json(row["receipt"])) == row["receipt_hash"]
    assert "view_context" not in row["receipt"]
    assert "student_name" not in row["receipt"]
    assert row["view_context"]["synthetic"] is True


@pytest.mark.parametrize("session_id", list_sessions())
def test_context_sentence_and_paragraph_references_resolve(gallery, session_id):
    row = next(row for row in gallery["sessions"] if row["session_id"] == session_id)
    context = row["view_context"]
    paragraphs = {paragraph["id"]: paragraph for paragraph in context["paragraphs"]}
    sentences = {sentence["id"]: sentence for sentence in context["sentences"]}
    for sentence in sentences.values():
        assert sentence["paragraph_id"] in paragraphs
        paragraph = paragraphs[sentence["paragraph_id"]]
        assert sentence["id"] in paragraph["sentence_ids"]
        assert isinstance(sentence["text"], str)
        assert sentence["from"] < sentence["to"]
        assert set(("steps", "notes", "history", "history_note")) <= sentence["chain"].keys()
    for paragraph in paragraphs.values():
        assert all(sid in sentences for sid in paragraph["sentence_ids"])
    assert context["header"]["submitted_at"] == next(
        event["ts"] for event in build_session(session_id).events if event["type"] == "submit")


def test_export_file_is_byte_deterministic_and_canonical(tmp_path):
    first = exporting.write_gallery(tmp_path / "first.json")
    second = exporting.write_gallery(tmp_path / "nested" / "second.json")
    assert first.read_bytes() == second.read_bytes()
    parsed = json.loads(first.read_bytes())
    assert first.read_bytes() == canonical_json(parsed) + b"\n"


def test_export_requires_stub_before_building_or_writing(monkeypatch, tmp_path):
    monkeypatch.delenv("ROOM_LLM", raising=False)

    def forbidden(_):
        raise AssertionError("builder was entered without stub mode")

    monkeypatch.setattr(exporting, "build_session", forbidden)
    target = tmp_path / "gallery.json"
    with pytest.raises(BuildError, match="requires ROOM_LLM=stub"):
        exporting.write_gallery(target)
    assert not target.exists()


def test_export_does_not_include_unrelated_environment_values(monkeypatch):
    marker = "export-test-value-must-stay-in-environment"
    monkeypatch.setenv("DEEPSEEK_API_KEY", marker)
    monkeypatch.setenv("ROOM_LLM2_API_KEY", marker)
    body = canonical_json(exporting.export_gallery()).decode()
    assert marker not in body
    assert "DEEPSEEK_API_KEY" not in body
    assert "ROOM_LLM2_API_KEY" not in body


def test_export_cli_writes_the_same_contract(tmp_path, capsys):
    path = tmp_path / "gallery.json"
    assert main(["export", str(path)]) == 0
    assert json.loads(path.read_bytes())["synthetic"] is True
    assert str(path) in capsys.readouterr().out


def test_pending_actual_compiler_questions_are_preserved(monkeypatch):
    # Derived test run only: the normal gallery remains the twelve complete goldens.
    actual_build = build_session
    monkeypatch.setattr(exporting, "build_session", lambda sid: actual_build(sid, ask=None))
    rows = exporting.export_gallery()["sessions"]
    with_questions = [row for row in rows if row["receipt"]["questions"]]
    assert with_questions
    for row in with_questions:
        assert row["receipt"]["status"] == "questions_pending"
        assert row["receipt"]["questions_pending"] is True
        assert all(question["q"] is None for question in row["receipt"]["questions"])
        assert sha256_hex(canonical_json(row["receipt"])) == row["receipt_hash"]


def test_export_rejects_a_receipt_hash_mismatch(monkeypatch):
    actual_build = build_session

    def corrupted_hash(sid):
        result = actual_build(sid)
        result.receipt_hash = "0" * 64
        return result

    monkeypatch.setattr(exporting, "build_session", corrupted_hash)
    with pytest.raises(BuildError, match="receipt hash does not match"):
        exporting.export_gallery()


def test_export_does_not_leave_partial_output_on_builder_failure(monkeypatch, tmp_path):
    target = tmp_path / "gallery.json"
    target.write_text("prior complete export", encoding="utf-8")

    def unavailable():
        raise BuildError("test builder failure")

    monkeypatch.setattr(exporting, "export_gallery", unavailable)
    with pytest.raises(BuildError, match="test builder failure"):
        exporting.write_gallery(target)
    assert target.read_text(encoding="utf-8") == "prior complete export"


def test_export_builds_without_any_outbound_socket(monkeypatch):
    import socket

    def forbidden(*_args, **_kwargs):
        raise AssertionError("golden export attempted an outbound connection")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    assert len(exporting.export_gallery()["sessions"]) == 12


@pytest.mark.parametrize("case", ["not_synthetic", "missing_name", "blank_name"])
def test_export_rejects_unlabelled_view_context(monkeypatch, case):
    real_context = exporting.build_view_context

    def invalid_context(*args):
        context = real_context(*args)
        if case == "not_synthetic":
            context["synthetic"] = False
        elif case == "missing_name":
            context["header"].pop("student_name")
        else:
            context["header"]["student_name"] = " "
        return context

    monkeypatch.setattr(exporting, "build_view_context", invalid_context)
    with pytest.raises(BuildError, match="synthetic"):
        exporting.export_gallery()
