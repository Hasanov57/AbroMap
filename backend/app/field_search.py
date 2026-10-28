"""Deterministic multilingual field search for the current catalog size."""

from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .catalog import normalize_text
from .models import AcademicField
from .schemas import AcademicFieldOut


def localized_name(field: AcademicField, locale: str) -> str:
    names = {item.locale: item.name for item in field.translations}
    return names.get(locale) or names.get("en") or field.slug.replace("-", " ").title()


def field_out(field: AcademicField, locale: str) -> AcademicFieldOut:
    return AcademicFieldOut(id=field.id, slug=field.slug, name=localized_name(field, locale),
                            category=localized_name(field.parent, locale) if field.parent else "",
                            isced_code=field.isced_code)


def _rank(field: AcademicField, query: str, locale: str) -> tuple[int, float] | None:
    preferred = normalize_text(localized_name(field, locale))
    names = [normalize_text(item.name) for item in field.translations]
    aliases = [item.normalized_alias for item in field.aliases]
    if query == preferred or query in names:
        return 0, 1
    if query in aliases:
        return 1, 1
    values = names + aliases
    if any(value.startswith(query) for value in values):
        return 2, 1
    if any(any(word.startswith(query) for word in value.split()) for value in values):
        return 3, 1
    if any(query in value for value in values):
        return 4, 1
    if len(query) >= 4:
        score = max((SequenceMatcher(None, query, value).ratio() for value in values), default=0)
        if score >= .72:
            return 5, score
    return None


def search_fields(db: Session, query: str, locale: str = "az", limit: int = 10) -> list[AcademicFieldOut]:
    fields = db.scalars(select(AcademicField).where(AcademicField.level == "specific").options(
        selectinload(AcademicField.translations), selectinload(AcademicField.aliases),
        selectinload(AcademicField.parent).selectinload(AcademicField.translations))).all()
    normalized = normalize_text(query)
    if not normalized:
        return [field_out(row, locale) for row in sorted(fields, key=lambda row: localized_name(row, locale))[:limit]]
    ranked = []
    for field in fields:
        match = _rank(field, normalized, locale)
        if match:
            ranked.append((match[0], -match[1], localized_name(field, locale).casefold(), field))
    ranked.sort(key=lambda item: item[:3])
    return [field_out(item[3], locale) for item in ranked[:limit]]
