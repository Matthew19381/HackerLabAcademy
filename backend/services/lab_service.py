"""
Docker lab management using DVWA (Damn Vulnerable Web Application).

Requirements: Docker installed and running.
DVWA image: vulnerables/web-dvwa
"""
import logging
import subprocess
import time
import requests

logger = logging.getLogger(__name__)

DVWA_IMAGE = "vulnerables/web-dvwa"
DVWA_CONTAINER_NAME = "hackerlabacademy_dvwa"
DVWA_PORT = 8080
DVWA_URL = f"http://localhost:{DVWA_PORT}"


def is_docker_available() -> bool:
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def get_lab_status() -> dict:
    """Check if DVWA container is running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", DVWA_CONTAINER_NAME],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            status = result.stdout.strip()
            return {"running": status == "running", "status": status, "url": DVWA_URL}
        return {"running": False, "status": "not_found", "url": None}
    except Exception as e:
        logger.error(f"Error checking lab status: {e}")
        return {"running": False, "status": "error", "url": None}


def start_lab() -> dict:
    """Start DVWA Docker container."""
    if not is_docker_available():
        return {"success": False, "error": "Docker nie jest dostępny. Zainstaluj Docker Desktop."}

    # Check if already running
    status = get_lab_status()
    if status["running"]:
        return {"success": True, "url": DVWA_URL, "message": "Lab już działa"}

    # Remove stopped container if exists
    subprocess.run(["docker", "rm", DVWA_CONTAINER_NAME], capture_output=True)

    # Start DVWA
    try:
        result = subprocess.run([
            "docker", "run", "-d",
            "--name", DVWA_CONTAINER_NAME,
            "-p", f"{DVWA_PORT}:80",
            DVWA_IMAGE
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {"success": False, "error": result.stderr or "Nie udało się uruchomić kontenera"}

        # Wait for DVWA to be ready (max 30 seconds)
        for _ in range(30):
            try:
                r = requests.get(DVWA_URL, timeout=2)
                if r.status_code in [200, 302]:
                    return {"success": True, "url": DVWA_URL, "message": "Lab uruchomiony"}
            except Exception:
                pass
            time.sleep(1)

        return {"success": True, "url": DVWA_URL, "message": "Lab uruchamiany (może potrzebować chwili)"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout podczas uruchamiania Dockera"}
    except Exception as e:
        logger.error(f"Error starting lab: {e}")
        return {"success": False, "error": str(e)}


def stop_lab() -> dict:
    """Stop and remove DVWA container."""
    try:
        subprocess.run(["docker", "stop", DVWA_CONTAINER_NAME], capture_output=True, timeout=15)
        subprocess.run(["docker", "rm", DVWA_CONTAINER_NAME], capture_output=True, timeout=10)
        return {"success": True, "message": "Lab zatrzymany"}
    except Exception as e:
        logger.error(f"Error stopping lab: {e}")
        return {"success": False, "error": str(e)}


def reset_lab() -> dict:
    """Reset DVWA to clean state."""
    stop_lab()
    return start_lab()


# Lab type → DVWA URL mapping
LAB_URLS = {
    "dvwa_sqli": f"{DVWA_URL}/vulnerabilities/sqli/",
    "dvwa_sqli_blind": f"{DVWA_URL}/vulnerabilities/sqli_blind/",
    "dvwa_xss_reflected": f"{DVWA_URL}/vulnerabilities/xss_r/",
    "dvwa_xss_stored": f"{DVWA_URL}/vulnerabilities/xss_s/",
    "dvwa_csrf": f"{DVWA_URL}/vulnerabilities/csrf/",
    "dvwa_file_upload": f"{DVWA_URL}/vulnerabilities/upload/",
    "dvwa_file_inclusion": f"{DVWA_URL}/vulnerabilities/fi/",
    "dvwa_command_injection": f"{DVWA_URL}/vulnerabilities/exec/",
    "dvwa_brute_force": f"{DVWA_URL}/vulnerabilities/brute/",
    "dvwa_idor": f"{DVWA_URL}/vulnerabilities/idor/",
}


def get_lab_url(lab_type: str) -> str:
    return LAB_URLS.get(lab_type, DVWA_URL)
