"""
CVE Auto-Fetch Service
Integrates with NVD API to fetch latest CVEs and store them in the database.
"""
import logging
import json
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.cve import Cve
from backend.database import SessionLocal

logger = logging.getLogger(__name__)

# NVD API v2.0 base URL
NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Mapping CVSS score to severity
CVSS_TO_SEVERITY = {
    9.0: "CRITICAL",
    7.0: "HIGH",
    4.0: "MEDIUM",
    0.0: "LOW"
}

def score_to_severity(cvss_score: float) -> str:
    """Convert CVSS score to severity string."""
    for threshold, severity in sorted(CVSS_TO_SEVERITY.items(), reverse=True):
        if cvss_score >= threshold:
            return severity
    return "LOW"

def fetch_nvd_cves(days_back: int = 7, results_per_page: int = 2000) -> dict:
    """
    Fetch CVEs from NVD API for the last N days.

    Args:
        days_back: Number of days to look back
        results_per_page: Max results per request (NVD limit: 2000)

    Returns:
        Raw NVD API response as dict
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)

    # Format: YYYY-MM-DDTHH:MM:SS
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    params = {
        "pubStartDate": start_str,
        "pubEndDate": end_str,
        "resultsPerPage": results_per_page
    }

    try:
        logger.info(f"Fetching CVEs from NVD API for last {days_back} days...")
        resp = requests.get(NVD_API_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        total = data.get("totalResults", 0)
        logger.info(f"NVD API returned {total} CVEs")
        return data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch CVEs from NVD: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from NVD: {e}")
        raise

def extract_affected_products(vuln_data: dict) -> list:
    """
    Extract affected product names from NVD configurations.
    Returns list of product strings (vendor:product).
    """
    products = []
    try:
        configurations = vuln_data.get("configurations", [])
        for config in configurations:
            nodes = config.get("nodes", [])
            for node in nodes:
                # CPE matches
                cpe_matches = node.get("cpeMatch", [])
                for match in cpe_matches:
                    cpe = match.get("criteria", "")
                    if cpe:
                        # Parse CPE: cpe:2.3:o:microsoft:windows_server:2019:*:*:*:*:*:*:*
                        parts = cpe.split(":")
                        if len(parts) >= 5:
                            vendor = parts[3]
                            product = parts[4]
                            products.append(f"{vendor}:{product}")
    except Exception as e:
        logger.warning(f"Error extracting products: {e}")
    return list(set(products))[:10]  # Dedup, limit to 10

def extract_references(refs_data: list) -> list:
    """Extract reference URLs."""
    urls = []
    try:
        for ref in refs_data:
            url = ref.get("url")
            if url:
                urls.append(url)
    except Exception:
        pass
    return urls

def get_cvss_severity(vuln_data: dict) -> str:
    """Extract severity from CVSS metrics (prefer v3, fallback to v2)."""
    try:
        cve = vuln_data.get("cve", {})
        metrics = cve.get("metrics", {})

        # Try CVSS v3 first
        cvss_v3 = metrics.get("cvssMetricV3", [])
        if cvss_v3:
            base_score = cvss_v3[0].get("cvssData", {}).get("baseScore", 0)
            return score_to_severity(base_score)

        # Fallback to CVSS v2
        cvss_v2 = metrics.get("cvssMetricV2", [])
        if cvss_v2:
            base_score = cvss_v2[0].get("cvssData", {}).get("baseScore", 0)
            return score_to_severity(base_score)
    except Exception as e:
        logger.warning(f"Error extracting severity: {e}")

    return "UNKNOWN"

def transform_cve_item(vuln_entry: dict) -> dict:
    """
    Transform a single NVD vulnerability entry into our Cve model dict.

    Args:
        vuln_entry: Single item from NVD 'vulnerabilities' array

    Returns:
        Dict with keys matching Cve model fields
    """
    cve = vuln_entry.get("cve", {})
    cve_id = cve.get("id", "")
    descriptions = cve.get("descriptions", [])
    description = next((d["value"] for d in descriptions if d["lang"] == "en"), "")
    if not description and descriptions:
        description = descriptions[0]["value"]

    # Extract published date
    published_date_str = cve.get("published")
    if published_date_str:
        try:
            published_date = datetime.fromisoformat(published_date_str.replace("Z", "+00:00"))
        except ValueError:
            published_date = datetime.utcnow()
    else:
        published_date = datetime.utcnow()

    severity = get_cvss_severity(vuln_entry)
    affected_products = extract_affected_products(vuln_entry)
    references = extract_references(cve.get("references", []))

    # Build title: use CVE ID + first sentence of description or just CVE ID
    title = cve_id
    if description:
        first_sentence = description.split(".")[0][:100]
        title = f"{cve_id}: {first_sentence}"

    return {
        "cve_id": cve_id,
        "title": title,
        "description": description,
        "severity": severity,
        "published_date": published_date,
        "affected_products": json.dumps(affected_products) if affected_products else None,
        "references": json.dumps(references) if references else None,
        "topic_slug": None,  # TODO: AI mapping later
        "is_active": True
    }

def save_cves_to_db(cve_dicts: list, db: Session = None) -> int:
    """
    Save CVE entries to database, skipping duplicates.

    Args:
        cve_dicts: List of transformed CVE dicts
        db: SQLAlchemy Session (optional, creates own if None)

    Returns:
        Number of new CVEs added
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        added = 0
        for cve_dict in cve_dicts:
            existing = db.query(Cve).filter(Cve.cve_id == cve_dict["cve_id"]).first()
            if existing:
                # Optionally update? Skip for now to preserve manual edits
                continue

            cve = Cve(**cve_dict)
            db.add(cve)
            added += 1

        db.commit()
        logger.info(f"Added {added} new CVEs to database")
        return added
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving CVEs to database: {e}")
        raise
    finally:
        if close_db:
            db.close()

def refresh_cves(days_back: int = 7) -> dict:
    """
    Full refresh: fetch from NVD, transform, save to DB.

    Returns:
        Summary dict with counts and status
    """
    try:
        raw_data = fetch_nvd_cves(days_back=days_back)
        vulnerabilities = raw_data.get("vulnerabilities", [])

        transformed = []
        for vuln in vulnerabilities:
            try:
                cve_dict = transform_cve_item(vuln)
                transformed.append(cve_dict)
            except Exception as e:
                logger.error(f"Failed to transform CVE: {e}")
                continue

        added = save_cves_to_db(transformed)

        return {
            "status": "success",
            "fetched": len(vulnerabilities),
            "transformed": len(transformed),
            "added": added,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"CVE refresh failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Optional: Background scheduler (simple in-process)
import threading
import time

class CveScheduler:
    """Simple background scheduler for periodic CVE fetching."""
    def __init__(self, interval_hours: int = 24):
        self.interval_hours = interval_hours
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """Start the background fetch loop."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"CVE scheduler started (every {self.interval_hours}h)")

    def stop(self):
        """Stop the background fetch loop."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("CVE scheduler stopped")

    def _run(self):
        while not self._stop_event.is_set():
            try:
                result = refresh_cves(days_back=1)  # daily fetch
                logger.info(f"[Scheduler] CVE refresh: {result}")
            except Exception as e:
                logger.error(f"[Scheduler] CVE refresh failed: {e}")

            # Wait for next interval
            self._stop_event.wait(self.interval_hours * 3600)

# Global scheduler instance
_scheduler = None

def start_scheduler(interval_hours: int = 24) -> CveScheduler:
    """Start the global CVE scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = CveScheduler(interval_hours=interval_hours)
        _scheduler.start()
    return _scheduler

def stop_scheduler():
    """Stop the global CVE scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
