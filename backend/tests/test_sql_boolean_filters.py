"""Regression: `Model.flag is True` inside .filter() is a Python identity check
(always False), not SQL - every such query returned nothing (CVE list, defense,
attack scenarios, certificates, videos, write-ups, error stats, brain agenda).
Found 2026-09-27; filters now use .is_(True/False)."""

import re
from datetime import datetime, timedelta
from pathlib import Path

from backend.models.cve import Cve
from backend.models.error_item import ErrorItem
from backend.models.user import User


def test_active_cves_are_listed(client, db_session):
    db_session.add_all(
        [
            Cve(cve_id="CVE-1", title="a", description="d", severity="HIGH", published_date=datetime(2026, 1, 1)),
            Cve(cve_id="CVE-2", title="b", description="d", severity="LOW", published_date=datetime(2026, 1, 2), is_active=False),
        ]
    )
    db_session.commit()
    ids = [c["cve_id"] for c in client.get("/api/v1/cves/").json()]
    assert "CVE-1" in ids and "CVE-2" not in ids


def test_brain_lists_due_errors(client, db_session):
    user = User(name="u")
    db_session.add(user)
    db_session.commit()
    db_session.add(
        ErrorItem(user_id=user.id, question="q", correct_answer="a", user_answer="b",
                  next_review=datetime.utcnow() - timedelta(hours=1))
    )
    db_session.commit()
    agenda = client.get(f"/api/v1/brain/today/{user.id}").json()
    items = agenda["agenda"] if isinstance(agenda, dict) else agenda
    assert any(i["type"] == "fix_errors" for i in items)


def test_no_identity_comparisons_in_queries():
    src = Path(__file__).resolve().parents[1]
    bad = []
    for f in list((src / "routers").glob("*.py")) + list((src / "services").glob("*.py")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\b[A-Z]\w*\.\w+ is (not )?(True|False|None)\b", line):
                bad.append(f"{f.name}:{n}")
    assert not bad, bad
