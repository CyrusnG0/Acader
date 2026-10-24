import os, sys
os.environ["ROOM_LLM"] = "stub"
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest

@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("ROOM_SESSIONS_DIR", str(tmp_path))
    import llmx
    llmx.CAPTURED.clear(); llmx.HANDLERS.clear()
    yield
    llmx.HANDLERS.clear()
