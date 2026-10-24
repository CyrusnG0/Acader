import ast
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVER = Path(__file__).resolve().parents[1]
PACKAGES = ["app", "engine", "engine.events", "engine.replay", "engine.provenance",
            "engine.receipt", "sources", "coach", "mapper", "trail"]


@pytest.mark.parametrize("name", PACKAGES)
def test_package_imports(name):
    importlib.import_module(name)


def test_healthz():
    from app.main import app
    r = TestClient(app).get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_engine_is_pure():
    bad = []
    for path in (SERVER / "engine").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            else:
                continue
            for m in mods:
                if m.split(".")[0] in ("fastapi", "starlette"):
                    bad.append(f"{path}: {m}")
    assert not bad, bad


def test_engine_cli_stub_exits_2():
    env = {**os.environ, "PYTHONPATH": str(SERVER)}
    p = subprocess.run([sys.executable, "-m", "engine", "compile", "somefile"],
                       cwd=SERVER, env=env, capture_output=True, text=True)
    assert p.returncode == 2
    assert "not implemented yet" in p.stderr
