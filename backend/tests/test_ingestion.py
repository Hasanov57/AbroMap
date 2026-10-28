import json
import zipfile

from sqlalchemy import func, select

from app.ingestion.import_service import import_ror
from app.ingestion.ror import iter_ror_dump, normalize_ror_record
from app.models import (University, UniversityAlias, UniversityIdentifier,
                        UniversityReviewCandidate, UniversitySource)


def ror_payload():
    return {
        "id": "https://ror.org/03cve4549", "status": "active", "types": ["education"],
        "names": [
            {"value": "Tsinghua University", "lang": "en", "types": ["ror_display", "label"]},
            {"value": "清华大学", "lang": "zh", "types": ["label"]},
            {"value": "THU", "lang": None, "types": ["acronym"]},
        ],
        "locations": [{"geonames_details": {"country_code": "CN", "name": "Beijing"}}],
        "links": [{"type": "website", "value": "https://www.tsinghua.edu.cn"}],
        "external_ids": [{"type": "wikidata", "all": ["Q16955"]}],
    }


def test_ror_normalization_and_unicode():
    record = normalize_ror_record(ror_payload(), {"CN"})
    assert record.name == "Tsinghua University" and record.country == "CN"
    assert ("清华大学", "zh") in record.aliases
    assert ("wikidata", "Q16955") in record.identifiers
    payload = ror_payload()
    payload["status"] = "inactive"
    assert normalize_ror_record(payload, {"CN"}) is None
    payload["status"] = "active"
    payload["names"][0]["value"] = "Example High School"
    assert normalize_ror_record(payload, {"CN"}) is None


def test_ror_import_is_dry_run_and_idempotent(db):
    payload = ror_payload()
    assert import_ror(db, [payload])["inserted"] == 1
    assert db.scalar(select(func.count(University.id))) == 0
    assert import_ror(db, [payload], dry_run=False)["inserted"] == 1
    assert import_ror(db, [payload], dry_run=False)["updated"] == 1
    assert db.scalar(select(func.count(University.id))) == 1
    university = db.scalar(select(University))
    assert university.is_demo is False
    assert db.scalar(select(func.count(UniversityAlias.id))) == 2
    assert db.scalar(select(func.count(UniversityIdentifier.id))) == 2
    assert db.scalar(select(func.count(UniversitySource.id))) == 1
    same_name_different_id = ror_payload()
    same_name_different_id["id"] = "https://ror.org/123456789"
    assert import_ror(db, [same_name_different_id], dry_run=False)["skipped"] == 1
    assert db.scalar(select(func.count(UniversityReviewCandidate.id))) == 1
    assert db.scalar(select(func.count(University.id))) == 1


def test_stream_json_and_zip(tmp_path):
    payload = [ror_payload(), ror_payload()]
    source = tmp_path / "ror.json"
    source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    archive = tmp_path / "ror.zip"
    with zipfile.ZipFile(archive, "w") as target:
        target.write(source, "v2-ror-data.json")
    assert len(list(iter_ror_dump(source))) == 2
    assert len(list(iter_ror_dump(archive))) == 2
