"""Every api.<method>('/path') in frontend/src/api/client.js has a backend route.

Added 2026-09-27 after finding POST /articles/{slug}/read and
/articles/{slug}/quiz/submit called by the UI but never implemented."""

import re
from pathlib import Path

import pytest

from backend.main import app

CLIENT = Path(__file__).resolve().parents[2] / "frontend" / "src" / "api" / "client.js"


def _norm(path: str) -> str:
    return path.rstrip("/") or "/"


@pytest.mark.skipif(not CLIENT.exists(), reason="frontend not checked out")
def test_every_client_call_has_a_route():
    routes = []
    for r in app.routes:
        if getattr(r, "path", None):
            rx = re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", _norm(r.path)) + "$")
            routes += [(m, rx) for m in (getattr(r, "methods", None) or [])]
    calls = re.findall(r"\bapi\.(get|post|put|patch|delete)\(\s*[`'\"](/[^`'\"]*)[`'\"]", CLIENT.read_text(encoding="utf-8"))
    assert len(calls) > 30
    missing = []
    for meth, path in calls:
        full = _norm("/api/v1" + re.sub(r"\$\{[^}]+\}", "X", path.split("?")[0]))
        if not any(m == meth.upper() and rx.match(full) for m, rx in routes):
            missing.append(f"{meth.upper()} {full}")
    assert not missing, missing
