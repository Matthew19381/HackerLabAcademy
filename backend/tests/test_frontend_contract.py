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


def _collect_all_routes(router, prefix=""):
    """Recursively collect all routes from an APIRouter including included routers."""
    routes = []
    for r in router.routes:
        if hasattr(r, 'routes'):  # APIRouter
            routes.extend(_collect_all_routes(r, prefix + r.prefix))
        elif hasattr(r, 'path'):  # APIRoute
            methods = getattr(r, 'methods', None) or []
            routes.append((methods, prefix + r.path))
        elif type(r).__name__ == '_IncludedRouter':
            # Expand included router
            if hasattr(r, 'original_router'):
                routes.extend(_collect_all_routes(r.original_router, prefix + r.include_context.prefix))
    return routes


@pytest.mark.skipif(not CLIENT.exists(), reason="frontend not checked out")
def test_every_client_call_has_a_route():
    # Collect all routes including those from included routers
    all_routes = _collect_all_routes(app.router)
    routes = []
    for methods, path in all_routes:
        rx = re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", _norm(path)) + "$")
        routes += [(m, rx) for m in methods]
    calls = re.findall(r"\bapi\.(get|post|put|patch|delete)\(\s*[`\"'](/[^`\"']*)[`\"']", CLIENT.read_text(encoding="utf-8"))
    assert len(calls) > 30
    missing = []
    for meth, path in calls:
        full = _norm("/api/v1" + re.sub(r"\$\{[^}]+\}", "X", path.split("?")[0]))
        if not any(m == meth.upper() and rx.match(full) for m, rx in routes):
            missing.append(f"{meth.upper()} {full}")
    assert not missing, missing
