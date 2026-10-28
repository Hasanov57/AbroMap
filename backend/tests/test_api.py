def test_catalog_and_search(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    countries = client.get("/api/v1/countries?locale=az").json()
    assert len(countries) == 52
    assert next(row for row in countries if row["iso_code"] == "CN")["university_count"] == 1
    assert next(row for row in countries if row["iso_code"] == "DE")["verified_program_count"] == 2
    fields = client.get("/api/v1/academic-fields/search?q=S%C3%BCni&locale=az").json()
    assert fields[0]["slug"] == "artificial-intelligence"
    assert client.get("/api/v1/academic-fields/search?q=IT&locale=ru").json()[0]["slug"] == "information-technology"
    page = client.get("/api/v1/universities?page=1&page_size=1").json()
    assert page["total"] == 2 and page["total_pages"] == 2
    assert len(page["items"]) == 1
    assert client.get("/api/v1/universities?search=Hochschule&page=1").json()["total"] == 1
    catalog_only = client.get("/api/v1/universities/fixture-university-cn").json()
    assert catalog_only["programs"] == []
    assert all(not row["is_demo"] for row in client.get("/api/v1/universities").json())


def test_match_exact_related_and_historical(client):
    exact = client.post("/api/v1/matching/evaluate", json={
        "degree": "master", "field": "computer-science", "intake_year": 2027,
    })
    assert exact.status_code == 200
    results = exact.json()["results"]
    assert results[0]["subject_match"] == "exact"
    assert results[0]["requirement_confidence"] == "verified"
    assert results[0]["checks"]["hsk"] == "unknown"
    assert any(row["subject_match"] == "related" for row in results)
    historical = client.post("/api/v1/matching/evaluate", json={
        "degree": "master", "field": "computer-science", "intake_year": 2026,
    }).json()["results"][0]
    assert historical["requirement_confidence"] == "historical"
    assert "historical:2025/2026" in historical["notes"]
    assert historical["checks"]["language"] == "unknown"


def test_empty_and_custom_major_reasons(client):
    assert client.post("/api/v1/matching/evaluate", json={
        "degree": "master", "field": "medicine"}).json()["no_match_reason"] == "field_unavailable"
    assert client.post("/api/v1/matching/evaluate", json={
        "degree": "master", "field": "computer-science", "countries": ["CN"]
    }).json()["no_match_reason"] == "country_unavailable"
    assert client.post("/api/v1/matching/evaluate", json={
        "degree": "master", "field": "custom", "custom_field": "Space Law"}
    ).json()["no_match_reason"] == "custom_field_unmapped"
    assert client.get("/api/v1/programs").json()[0]["is_demo"] is False


def test_admin_and_invalid_gpa(client):
    assert client.get("/api/v1/admin/summary").status_code == 403
    assert client.post("/api/v1/matching/evaluate", json={
        "degree": "master", "field": "computer-science", "gpa": 85, "gpa_scale": 4,
    }).status_code == 422
