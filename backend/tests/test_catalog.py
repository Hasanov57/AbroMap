from sqlalchemy import func, select

from app.catalog import initialize_catalog, normalize_text
from app.field_search import search_fields
from app.models import AcademicField, AcademicFieldAlias, AcademicFieldRelation, Country


def test_repeatable_taxonomy_and_country_seed(db):
    assert initialize_catalog(db) == {"countries": 52, "isced_fields": 120, "specific_majors": 260}
    assert db.scalar(select(func.count(AcademicField.id))) == 380
    assert db.scalar(select(func.count(Country.iso_code))) == 52
    assert db.scalar(select(func.count(AcademicFieldRelation.id))) == 42
    assert db.scalar(select(func.count(AcademicFieldAlias.id))) > 400


def test_multilingual_search_ranking(db):
    assert search_fields(db, "IT", "az")[0].slug == "information-technology"
    assert search_fields(db, "Süni", "az")[0].slug == "artificial-intelligence"
    assert search_fields(db, "Программ", "ru")[0].slug == "software-engineering"
    assert search_fields(db, "Cybrsecurity", "en")[0].slug == "cybersecurity"
    assert normalize_text("İnformasiya") == "informasiya"
