"""Idempotent ROR institutional import. No degree programs are inferred here."""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog import normalize_text
from app.models import (Country, ImportRun, University, UniversityAlias,
                        UniversityIdentifier, UniversityReviewCandidate, UniversitySource)
from .ror import InstitutionRecord, normalize_ror_record


def import_ror(db: Session, payloads: Iterable[dict], *, dry_run: bool = True,
               limit: int | None = None, batch_size: int = 100,
               source_version: str | None = None) -> dict[str, int]:
    allowed = set(db.scalars(select(Country.iso_code).where(Country.enabled.is_(True))).all())
    counts = {"processed": 0, "inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    run = None
    if not dry_run:
        run = ImportRun(source="ror", source_version=source_version, dry_run=False)
        db.add(run)
        db.commit()
    # A remote database round trip for every lookup makes a full ROR import take
    # hours. Load the keys once and keep these indexes current as rows are added.
    universities_by_ror = {row.ror_id: row for row in db.scalars(
        select(University).where(University.ror_id.is_not(None))).all()}
    names = {(country, normalized_name): university_id for country, normalized_name, university_id in
             db.execute(select(University.country, University.normalized_name, University.id)
                        .where(University.is_demo.is_(False))).all()}
    aliases = defaultdict(set)
    for university_id, name in db.execute(select(UniversityAlias.university_id, UniversityAlias.name)):
        aliases[university_id].add(name)
    identifiers = defaultdict(set)
    identifier_owners = set()
    for university_id, scheme, value in db.execute(select(
            UniversityIdentifier.university_id, UniversityIdentifier.scheme, UniversityIdentifier.value)):
        identifiers[university_id].add((scheme, value))
        identifier_owners.add((scheme, value))
    sources = {row.source_record_id: row for row in db.scalars(
        select(UniversitySource).where(UniversitySource.source == "ror")).all()}
    review_ids = set(db.scalars(select(UniversityReviewCandidate.source_record_id)).all())
    prior_expire_on_commit = db.expire_on_commit
    db.expire_on_commit = False
    try:
        for payload in payloads:
            if limit is not None and counts["processed"] >= limit:
                break
            counts["processed"] += 1
            record = normalize_ror_record(payload, allowed)
            if record is None:
                counts["skipped"] += 1
                continue
            existing = universities_by_ror.get(record.ror_id)
            if existing is None:
                # Names are a review signal, never sufficient grounds for an automatic merge.
                name_conflict = names.get((record.country, normalize_text(record.name)))
                if name_conflict:
                    counts["skipped"] += 1
                    if not dry_run and record.ror_id not in review_ids:
                        db.add(UniversityReviewCandidate(source="ror", source_record_id=record.ror_id,
                            candidate_university_id=name_conflict, name=record.name, country=record.country,
                            reason="same_normalized_name_different_ror_id", status="pending"))
                        review_ids.add(record.ror_id)
                    continue
                counts["inserted"] += 1
            else:
                counts["updated"] += 1
            if dry_run:
                continue
            previous_name = (existing.country, existing.normalized_name) if existing else None
            university = upsert_university(db, record, existing, aliases=aliases,
                identifiers=identifiers, identifier_owners=identifier_owners, sources=sources)
            universities_by_ror[record.ror_id] = university
            if previous_name and previous_name != (record.country, normalize_text(record.name)) \
                    and names.get(previous_name) == university.id:
                del names[previous_name]
            names[(record.country, normalize_text(record.name))] = university.id
            if counts["processed"] % batch_size == 0:
                db.commit()
                if run:
                    for key, value in counts.items():
                        setattr(run, key, value)
                    db.commit()
        if not dry_run and run:
            for key, value in counts.items():
                setattr(run, key, value)
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
        return counts
    except Exception as exc:
        db.rollback()
        if run:
            run = db.get(ImportRun, run.id)
            run.status = "failed"
            run.detail = str(exc)[:2000]
            run.completed_at = datetime.now(timezone.utc)
            for key, value in counts.items():
                setattr(run, key, value)
            db.commit()
        raise
    finally:
        db.expire_on_commit = prior_expire_on_commit


def upsert_university(db: Session, record: InstitutionRecord,
                      existing: University | None = None, *,
                      aliases: dict[int, set[str]],
                      identifiers: dict[int, set[tuple[str, str]]],
                      identifier_owners: set[tuple[str, str]],
                      sources: dict[str, UniversitySource]) -> University:
    now = datetime.now(timezone.utc)
    university = existing
    if university is None:
        slug = f"{normalize_text(record.name).replace(' ', '-')}-{record.ror_id.rsplit('/', 1)[-1]}"
        university = University(slug=slug[:160], ror_id=record.ror_id, name=record.name,
                                normalized_name=normalize_text(record.name),
                                city=record.city, country=record.country, website=record.website,
                                institution_type=record.institution_type, status="active",
                                source_url=record.source_url, retrieved_at=now, is_demo=False)
        db.add(university)
        db.flush()
    else:
        university.name = record.name
        university.normalized_name = normalize_text(record.name)
        university.city = record.city
        university.country = record.country
        university.website = record.website
        university.retrieved_at = now
        university.source_url = record.source_url
        university.status = "active"
        university.is_demo = False
    existing_aliases = aliases[university.id]
    for name, locale in record.aliases:
        if name not in existing_aliases:
            db.add(UniversityAlias(university_id=university.id, name=name, locale=locale,
                                   normalized_name=normalize_text(name)))
            existing_aliases.add(name)
    existing_ids = identifiers[university.id]
    for scheme, value in record.identifiers:
        if (scheme, value) not in existing_ids:
            if (scheme, value) not in identifier_owners:
                db.add(UniversityIdentifier(university_id=university.id, scheme=scheme, value=value))
                existing_ids.add((scheme, value))
                identifier_owners.add((scheme, value))
    source = sources.get(record.ror_id)
    if source is None:
        source = UniversitySource(university_id=university.id, source="ror",
                                  source_record_id=record.ror_id, source_url=record.source_url,
                                  retrieved_at=now)
        db.add(source)
        sources[record.ror_id] = source
    else:
        source.retrieved_at = now
    return university
