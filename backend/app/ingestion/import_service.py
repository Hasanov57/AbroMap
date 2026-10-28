"""Idempotent ROR institutional import. No degree programs are inferred here."""

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
    try:
        for payload in payloads:
            if limit is not None and counts["processed"] >= limit:
                break
            counts["processed"] += 1
            record = normalize_ror_record(payload, allowed)
            if record is None:
                counts["skipped"] += 1
                continue
            existing = db.scalar(select(University).where(University.ror_id == record.ror_id))
            if existing is None:
                # Names are a review signal, never sufficient grounds for an automatic merge.
                name_conflict = db.scalar(select(University.id).where(University.country == record.country,
                                                                      University.normalized_name == normalize_text(record.name),
                                                                      University.is_demo.is_(False)))
                if name_conflict:
                    counts["skipped"] += 1
                    if not dry_run:
                        review = db.scalar(select(UniversityReviewCandidate).where(
                            UniversityReviewCandidate.source_record_id == record.ror_id))
                        if review is None:
                            db.add(UniversityReviewCandidate(source="ror", source_record_id=record.ror_id,
                                candidate_university_id=name_conflict, name=record.name, country=record.country,
                                reason="same_normalized_name_different_ror_id", status="pending"))
                    continue
                counts["inserted"] += 1
            else:
                counts["updated"] += 1
            if dry_run:
                continue
            upsert_university(db, record, existing)
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


def upsert_university(db: Session, record: InstitutionRecord,
                      existing: University | None = None) -> University:
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
    existing_aliases = {row.name for row in db.scalars(select(UniversityAlias).where(
        UniversityAlias.university_id == university.id)).all()}
    for name, locale in record.aliases:
        if name not in existing_aliases:
            db.add(UniversityAlias(university_id=university.id, name=name, locale=locale,
                                   normalized_name=normalize_text(name)))
            existing_aliases.add(name)
    existing_ids = {(row.scheme, row.value) for row in db.scalars(select(UniversityIdentifier).where(
        UniversityIdentifier.university_id == university.id)).all()}
    for scheme, value in record.identifiers:
        if (scheme, value) not in existing_ids:
            owner = db.scalar(select(UniversityIdentifier.id).where(UniversityIdentifier.scheme == scheme,
                                                                     UniversityIdentifier.value == value))
            if owner is None:
                db.add(UniversityIdentifier(university_id=university.id, scheme=scheme, value=value))
                existing_ids.add((scheme, value))
    source = db.scalar(select(UniversitySource).where(UniversitySource.source == "ror",
                                                       UniversitySource.source_record_id == record.ror_id))
    if source is None:
        db.add(UniversitySource(university_id=university.id, source="ror",
                                source_record_id=record.ror_id, source_url=record.source_url,
                                retrieved_at=now))
    else:
        source.retrieved_at = now
    return university
