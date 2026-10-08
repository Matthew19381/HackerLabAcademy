"""The Docker stack must use the registered backend port :8003 (B7, found 2026-10-08).

start.bat/start.ps1, the Vite proxy and the hub (MODULE_ENDPOINTS) all use :8003, but
docker-compose.yml published :8001 - LinguaAI's port - so the two stacks collided and the
hub never reached the dockerised backend. Registry: System-Glowny/CLAUDE.md.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = "8003"
LINGUA_AI_PORT = "8001"

DOCKER_FILES = ["docker-compose.yml", "backend/Dockerfile", "frontend/Dockerfile", "frontend/nginx.conf"]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def test_docker_stack_does_not_use_lingua_ai_port():
    for rel in DOCKER_FILES:
        assert LINGUA_AI_PORT not in _read(rel), rel


def test_docker_stack_uses_registered_port():
    compose = _read("docker-compose.yml")
    assert f'"{PORT}:{PORT}"' in compose
    assert f"--port {PORT}" in compose
    assert f"127.0.0.1:{PORT}/api/health" in compose
    assert f"backend:{PORT}" in _read("frontend/nginx.conf")
    assert f"EXPOSE {PORT}" in _read("backend/Dockerfile")


def test_local_launchers_and_vite_proxy_use_the_same_port():
    assert f"--port {PORT}" in _read("start.bat")
    assert f"--port {PORT}" in _read("start.ps1")
    assert f"localhost:{PORT}" in _read("frontend/vite.config.js")
