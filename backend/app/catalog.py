"""Stable academic taxonomy and country initialization; no institution facts live here."""

import json
import re
import unicodedata
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (AcademicField, AcademicFieldAlias, AcademicFieldRelation,
                     AcademicFieldTranslation, Country)


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_data(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def normalize_text(value: str) -> str:
    value = value.casefold().replace("ı", "i").replace("ə", "e").replace("ё", "е")
    value = "".join(char for char in unicodedata.normalize("NFKD", value)
                    if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))


RELATED = (
    ("information-technology", "information-systems", "closely_related", .9),
    ("information-technology", "computer-science", "related", .75),
    ("computer-science", "information-systems", "related", .7),
    ("information-technology", "software-engineering", "related", .75),
    ("information-technology", "cybersecurity", "related", .7),
    ("artificial-intelligence", "machine-learning", "closely_related", .9),
    ("artificial-intelligence", "data-science", "related", .7),
    ("artificial-intelligence", "computer-science", "related", .7),
    ("data-science", "statistics", "related", .7),
    ("data-science", "data-analytics", "closely_related", .9),
    ("data-science", "computer-science", "related", .65),
    ("software-engineering", "computer-science", "closely_related", .85),
    ("computer-engineering", "computer-science", "related", .7),
    ("computer-engineering", "electrical-engineering", "related", .65),
    ("business-administration", "management", "closely_related", .85),
    ("business-administration", "international-business", "related", .7),
    ("finance", "economics", "related", .65),
    ("mathematics", "applied-mathematics", "closely_related", .9),
    ("mathematics", "statistics", "related", .7),
    ("architecture", "urban-planning", "related", .65),
    ("environmental-science", "environmental-engineering", "related", .6),
)


def initialize_catalog(db: Session) -> dict[str, int]:
    """Idempotently upsert supported countries, ISCED-F hierarchy and curated majors."""
    countries = load_data("countries.json")["countries"]
    country_by_code = {row.iso_code: row for row in db.scalars(select(Country)).all()}
    for item in countries:
        row = country_by_code.get(item["iso_code"])
        if row is None:
            row = Country(**item)
            db.add(row)
            country_by_code[row.iso_code] = row
        else:
            for key in ("name_en", "name_az", "name_ru", "region"):
                setattr(row, key, item[key])

    isced = load_data("iscedf_2013.json")["fields"]
    majors = load_data("specific_majors.json")["majors"]
    field_localizations = load_data("field_localizations.json")["translations"]
    isced_localizations = load_data("isced_localizations.json")["translations"]
    by_code = {row.code: row for row in db.scalars(select(AcademicField)).all()}
    desired: list[tuple[str, str, str, str | None, str | None, str]] = []
    for item in isced:
        code = item["code"]
        desired.append((f"isced:{code}", f"isced-{code}", item["level"],
                        f"isced:{item['parent_code']}" if item["parent_code"] else None,
                        code, item["name_en"]))
    for item in majors:
        desired.append((f"major:{item['slug']}", item["slug"], "specific",
                        f"isced:{item['isced_code']}", item["isced_code"], item["name_en"]))

    for level in ("broad", "narrow", "detailed", "specific"):
        for code, slug, item_level, parent_code, isced_code, _ in desired:
            if item_level != level:
                continue
            parent_id = by_code[parent_code].id if parent_code else None
            row = by_code.get(code)
            if row is None:
                row = AcademicField(code=code, slug=slug, level=level,
                                    parent_id=parent_id, isced_code=isced_code)
                db.add(row)
                by_code[code] = row
            else:
                row.parent_id = parent_id
                row.isced_code = isced_code
        db.flush()

    translations = {(row.academic_field_id, row.locale): row
                    for row in db.scalars(select(AcademicFieldTranslation)).all()}
    aliases = {(row.academic_field_id, row.locale, row.normalized_alias)
               for row in db.scalars(select(AcademicFieldAlias)).all()}
    for code, slug, level, _, isced_code, name_en in desired:
        field = by_code[code]
        localization = (field_localizations.get(slug, {}) if level == "specific"
                        else isced_localizations.get(isced_code or "", {}))
        for locale, name in (("en", name_en), ("az", localization.get("az")),
                             ("ru", localization.get("ru"))):
            if not name:
                continue
            key = (field.id, locale)
            if key in translations:
                translations[key].name = name
            else:
                row = AcademicFieldTranslation(academic_field_id=field.id, locale=locale, name=name)
                db.add(row)
                translations[key] = row
            alias_key = (field.id, locale, normalize_text(name))
            if alias_key not in aliases:
                db.add(AcademicFieldAlias(academic_field_id=field.id, alias=name,
                                          locale=locale, normalized_alias=alias_key[2]))
                aliases.add(alias_key)
        for alias in localization.get("aliases", []):
            alias_key = (field.id, "en", normalize_text(alias))
            if alias_key not in aliases:
                db.add(AcademicFieldAlias(academic_field_id=field.id, alias=alias,
                                          locale="en", normalized_alias=alias_key[2]))
                aliases.add(alias_key)

    relations = {(row.source_field_id, row.target_field_id): row
                 for row in db.scalars(select(AcademicFieldRelation)).all()}
    for source, target, kind, weight in RELATED:
        for a, b in ((source, target), (target, source)):
            key = (by_code[f"major:{a}"].id, by_code[f"major:{b}"].id)
            if key not in relations:
                db.add(AcademicFieldRelation(source_field_id=key[0], target_field_id=key[1],
                                             relationship_type=kind, similarity_weight=weight,
                                             reason="Curated subject relationship; admission eligibility is separate."))
    db.commit()
    return {"countries": len(countries), "isced_fields": len(isced), "specific_majors": len(majors)}
