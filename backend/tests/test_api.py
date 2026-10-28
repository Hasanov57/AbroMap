from fastapi.testclient import TestClient
from app.main import app


def test_public_discovery_and_matching():
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        universities = client.get("/api/v1/universities").json()
        assert len(universities) >= 5
        assert all({"bachelor", "master", "phd"}.issubset({p["degree"] for p in u["programs"]}) for u in universities if u["is_demo"])
        response = client.post("/api/v1/matching/evaluate", json={
            "degree": "master", "field": "computer_science", "countries": [],
            "citizenship": "AZ", "scholarship_priority": "preferred",
            "gpa": 3.5, "gpa_scale": 4, "ielts": 7, "budget_eur": 5000,
        })
        assert response.status_code == 200
        result = response.json()["results"][0]
        assert result["program"]["is_demo"] is True
        assert result["score"] <= 69  # Unverified demo requirements cap confidence.
        assert "requirements_unverified" in result["uncertainty"]


def test_demo_bachelor_and_phd_profiles_return_uncertain_results():
    with TestClient(app) as client:
        for degree in ("bachelor", "phd"):
            response = client.post("/api/v1/matching/evaluate", json={"degree": degree, "field": "computer_science"})
            assert response.status_code == 200
            result = response.json()["results"][0]
            assert result["program"]["degree"] == degree
            assert result["category"] == "insufficient_information"
            assert result["program"]["tuition_eur"] is None


def test_no_match_reason_identifies_catalog_gap():
    with TestClient(app) as client:
        missing_field = client.post("/api/v1/matching/evaluate", json={"degree": "master", "field": "medicine"}).json()
        assert missing_field["results"] == []
        assert missing_field["no_match_reason"] == "field_unavailable"
        missing_country = client.post("/api/v1/matching/evaluate", json={"degree": "master", "field": "computer_science", "countries": ["NL"]}).json()
        assert missing_country["no_match_reason"] == "country_unavailable"
        milan_id = next(u["id"] for u in client.get("/api/v1/universities").json() if u["slug"] == "demo-milan-academy")
        missing_university = client.post("/api/v1/matching/evaluate", json={"degree": "master", "field": "computer_science", "university_id": milan_id}).json()
        assert missing_university["no_match_reason"] == "university_unavailable"


def test_admin_requires_backend_token():
    with TestClient(app) as client:
        assert client.get("/api/v1/admin/summary").status_code == 403
        assert client.get("/api/v1/admin/summary", headers={"X-Admin-Token": "any"}).status_code == 403


def test_invalid_gpa_is_rejected():
    with TestClient(app) as client:
        response = client.post("/api/v1/matching/evaluate", json={"degree": "master", "field": "computer_science", "gpa": 85, "gpa_scale": 4})
        assert response.status_code == 422
