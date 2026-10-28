from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from .config import settings
from .db import get_db
from .matching import evaluate
from .catalog import normalize_text
from .field_search import search_fields
from .models import (AcademicField, AcademicFieldRelation, Country, Program, Requirement,
                     Scholarship, University, UniversityAlias)
from .schemas import (AcademicFieldOut, CountryOut, MatchResponse, ProgramOut, ScholarshipOut,
                      StudentProfile, UniversityOut, UniversityPage, UniversitySearchOut)
app = FastAPI(title="AbroMap API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True,
                   allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "X-Admin-Token"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/countries", response_model=list[CountryOut])
def countries(locale: str = Query("az", pattern="^(az|en|ru)$"), db: Session = Depends(get_db)):
    university_counts = dict(db.execute(select(University.country, func.count(University.id)).where(
        University.is_demo.is_(False), University.status == "active").group_by(University.country)).all())
    program_counts = dict(db.execute(select(University.country, func.count(Program.id)).join(Program).where(
        University.is_demo.is_(False), University.status == "active",
        Program.is_demo.is_(False)).group_by(University.country)).all())
    verified_counts = dict(db.execute(select(University.country, func.count(Program.id)).join(Program).where(
        University.is_demo.is_(False), University.status == "active",
        Program.is_demo.is_(False), Program.data_status == "verified_source")
        .group_by(University.country)).all())
    return [CountryOut(iso_code=row.iso_code, name=getattr(row, f"name_{locale}"), region=row.region,
                       university_count=university_counts.get(row.iso_code, 0),
                       program_count=program_counts.get(row.iso_code, 0),
                       verified_program_count=verified_counts.get(row.iso_code, 0))
            for row in db.scalars(select(Country).where(Country.enabled.is_(True)).order_by(Country.name_en))]


@app.get("/api/v1/academic-fields/search", response_model=list[AcademicFieldOut])
def academic_field_search(q: str = Query("", max_length=100), locale: str = Query("az", pattern="^(az|en|ru)$"),
                          limit: int = Query(10, ge=1, le=30), db: Session = Depends(get_db)):
    return search_fields(db, q, locale, limit)


@app.get("/api/v1/academic-fields", response_model=list[AcademicFieldOut])
def academic_fields(locale: str = Query("az", pattern="^(az|en|ru)$"),
                    limit: int = Query(100, ge=1, le=300), offset: int = Query(0, ge=0),
                    db: Session = Depends(get_db)):
    from .field_search import field_out
    rows = db.scalars(select(AcademicField).where(AcademicField.level == "specific").options(
        selectinload(AcademicField.translations),
        selectinload(AcademicField.parent).selectinload(AcademicField.translations))
        .order_by(AcademicField.slug).limit(limit).offset(offset)).all()
    return [field_out(row, locale) for row in rows]


def university_query():
    return select(University).options(selectinload(University.aliases),
        selectinload(University.programs).selectinload(Program.requirements).selectinload(Requirement.exams),
        with_loader_criteria(Program, (Program.is_demo.is_(False)) & (Program.data_status == "verified_source")))


def program_query():
    return select(Program).options(selectinload(Program.requirements).selectinload(Requirement.exams),
                                   selectinload(Program.university).selectinload(University.aliases))


@app.get("/api/v1/universities", response_model=list[UniversityOut] | UniversityPage)
def universities(country: str | None = None, search: str | None = None, city: str | None = None,
                 limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0),
                 page: int | None = Query(None, ge=1), page_size: int = Query(20, ge=1, le=100),
                 db: Session = Depends(get_db)):
    query = select(University).where(University.is_demo.is_(False), University.status == "active")
    if country:
        query = query.where(University.country == country.upper())
    if search:
        term = f"%{normalize_text(search)}%"
        alias_match = select(UniversityAlias.id).where(
            UniversityAlias.university_id == University.id, UniversityAlias.normalized_name.like(term)).exists()
        query = query.where(or_(University.normalized_name.like(term), alias_match,
                                University.name.ilike(f"%{search}%")))
    if city:
        query = query.where(University.city.ilike(f"%{city}%"))
    if page is not None:
        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = db.scalars(query.order_by(University.name, University.id)
                          .limit(page_size).offset((page - 1) * page_size)).all()
        ids = [row.id for row in rows]
        counts = dict(db.execute(select(Program.university_id, func.count(Program.id)).where(
            Program.university_id.in_(ids), Program.is_demo.is_(False), Program.data_status == "verified_source")
            .group_by(Program.university_id)).all()) if ids else {}
        return UniversityPage(items=[UniversitySearchOut(id=row.id, slug=row.slug, name=row.name,
            city=row.city, country=row.country, website=row.website, ror_id=row.ror_id,
            program_count=counts.get(row.id, 0)) for row in rows], total=total, page=page,
            page_size=page_size, total_pages=(total + page_size - 1) // page_size)
    return db.scalars(query.options(selectinload(University.aliases),
        selectinload(University.programs).selectinload(Program.requirements).selectinload(Requirement.exams),
        with_loader_criteria(Program, (Program.is_demo.is_(False)) & (Program.data_status == "verified_source")))
        .order_by(University.name).limit(limit).offset(offset)).all()


@app.get("/api/v1/universities/by-id/{university_id}", response_model=UniversityOut)
def university_by_id(university_id: int, db: Session = Depends(get_db)):
    item = db.scalar(university_query().where(University.id == university_id,
                                              University.is_demo.is_(False), University.status == "active"))
    if not item:
        raise HTTPException(404, "University not found")
    return item


@app.get("/api/v1/universities/{slug}", response_model=UniversityOut)
def university(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(university_query().where(University.slug == slug,
                                              University.is_demo.is_(False), University.status == "active"))
    if not item:
        raise HTTPException(404, "University not found")
    return item


@app.get("/api/v1/programs", response_model=list[ProgramOut])
def programs(degree: str | None = None, field: str | None = None, country: str | None = None,
             limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = program_query().join(University).where(Program.is_demo.is_(False),
        University.is_demo.is_(False), University.status == "active",
        Program.data_status == "verified_source")
    if degree:
        query = query.where(Program.degree == degree)
    if field:
        query = query.where(Program.field == field.replace("_", "-"))
    if country:
        query = query.where(University.country == country.upper())
    return db.scalars(query.order_by(Program.name).limit(limit).offset(offset)).all()


@app.get("/api/v1/programs/{program_id}", response_model=ProgramOut)
def program(program_id: int, db: Session = Depends(get_db)):
    item = db.scalar(program_query().join(University).where(Program.id == program_id,
        Program.is_demo.is_(False), University.is_demo.is_(False),
        University.status == "active", Program.data_status == "verified_source"))
    if not item:
        raise HTTPException(404, "Program not found")
    return item


@app.post("/api/v1/matching/evaluate", response_model=MatchResponse)
def match(profile: StudentProfile, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50),
          db: Session = Depends(get_db)):
    if profile.field == "custom":
        return MatchResponse(results=[], total=0, page=page, page_size=page_size,
                             no_match_reason="custom_field_unmapped")
    field_slug = profile.field.replace("_", "-")
    field = db.scalar(select(AcademicField).where(AcademicField.slug == field_slug,
                                                   AcademicField.level == "specific"))
    related = {}
    if field:
        related = dict(db.execute(select(AcademicFieldRelation.target_field_id,
                                         AcademicFieldRelation.similarity_weight).where(
            AcademicFieldRelation.source_field_id == field.id)).all())
    field_ids = ([field.id] if field else []) + list(related)
    filters = [Program.degree == profile.degree, Program.is_demo.is_(False),
               Program.data_status == "verified_source", University.is_demo.is_(False),
               University.status == "active",
               or_(Program.academic_field_id.in_(field_ids), Program.field == field_slug)]
    if profile.countries:
        filters.append(University.country.in_(profile.countries))
    if profile.university_id:
        filters.append(University.id == profile.university_id)
    total = db.scalar(select(func.count(Program.id)).join(University).where(*filters)) or 0
    rows = db.scalars(program_query().join(University).where(*filters)
                      .order_by(Program.id).limit(page_size).offset((page - 1) * page_size)).all()
    results = []
    for row in rows:
        exact = (field and row.academic_field_id == field.id) or row.field == field_slug
        result = evaluate(profile, row, subject_match="exact" if exact else "related",
                          similarity=1.0 if exact else related.get(row.academic_field_id, .6))
        if result:
            results.append(result)
    results.sort(key=lambda item: item.score, reverse=True)
    reason = None
    if total == 0:
        catalog_count = db.scalar(select(func.count(Program.id)).where(
            Program.is_demo.is_(False), Program.data_status == "verified_source")) or 0
        degree_count = db.scalar(select(func.count(Program.id)).where(
            Program.degree == profile.degree, Program.is_demo.is_(False),
            Program.data_status == "verified_source")) or 0
        field_count = db.scalar(select(func.count(Program.id)).where(
            Program.degree == profile.degree, Program.is_demo.is_(False),
            Program.data_status == "verified_source",
            or_(Program.academic_field_id.in_(field_ids), Program.field == field_slug))) or 0
        reason = ("catalog_empty" if not catalog_count else "degree_unavailable" if not degree_count else
                  "field_unavailable" if not field_count else "country_unavailable" if profile.countries else
                  "university_unavailable" if profile.university_id else "insufficient_data")
    return MatchResponse(results=results, total=total, page=page, page_size=page_size, no_match_reason=reason)


@app.get("/api/v1/scholarships", response_model=list[ScholarshipOut])
def scholarships(country: str | None = None, degree: str | None = None, db: Session = Depends(get_db)):
    query = select(Scholarship).where(Scholarship.is_demo.is_(False),
        Scholarship.verification_status.in_(["verified_current", "verified_historical"]))
    if country:
        query = query.where((Scholarship.country == country.upper()) | (Scholarship.country.is_(None)))
    if degree:
        query = query.where((Scholarship.degree == degree) | (Scholarship.degree.is_(None)))
    return db.scalars(query.order_by(Scholarship.name)).all()


@app.get("/api/v1/scholarships/{scholarship_id}", response_model=ScholarshipOut)
def scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    item = db.get(Scholarship, scholarship_id)
    if not item or item.is_demo or item.verification_status not in {"verified_current", "verified_historical"}:
        raise HTTPException(404, "Scholarship not found")
    return item


def require_admin(x_admin_token: str | None = Header(default=None)):
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(403, "Administrator access required")


@app.get("/api/v1/admin/summary", dependencies=[Depends(require_admin)])
def admin_summary(db: Session = Depends(get_db)):
    return {"universities": db.scalar(select(func.count(University.id))),
            "programs": db.scalar(select(func.count(Program.id))),
            "requirements": db.scalar(select(func.count(Requirement.id))),
            "scholarships": db.scalar(select(func.count(Scholarship.id)))}


@app.post("/api/v1/ai/chat")
async def ai_chat(payload: dict, db: Session = Depends(get_db)):
    message = str(payload.get("message", "")).strip()[:1000]
    if not message:
        raise HTTPException(422, "Message is required")
    program_id = payload.get("program_id")
    context = ""
    sources = []
    if program_id:
        item = db.scalar(program_query().join(University).where(
            Program.id == program_id, Program.is_demo.is_(False),
            Program.data_status == "verified_source", University.is_demo.is_(False),
            University.status == "active"))
        if item:
            req = item.requirements[0] if item.requirements else None
            context = f"Program: {item.name}. Tuition: {item.tuition_eur}. Teaching language: {item.teaching_language}. Requirement: {req.academic_year if req else 'unknown'}, IELTS {req.ielts_min if req else 'unknown'}, status {req.status if req else 'unknown'}."
            if req and req.source_url:
                sources.append(req.source_url)
            elif item.official_url:
                sources.append(item.official_url)
    if not settings.openai_api_key:
        fallback = {
            "az": "AI xidməti qoşulmayıb. Proqram məlumatlarına və mənbələrə baxın; müraciətdən əvvəl tələbləri universitetlə təsdiqləyin.",
            "en": "AI is not configured. Explore the program details and source links; verify requirements with the university before applying.",
            "ru": "ИИ не подключён. Изучите сведения о программе и источники; перед подачей заявки уточните требования в университете.",
        }
        return {"answer": fallback.get(payload.get("locale"), fallback["az"]), "sources": sources, "configured": False}
    import httpx
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://api.openai.com/v1/responses", headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                                     json={"model": settings.openai_model, "instructions": "You are AbroMap. Answer in the user's language. Use only supplied context for factual admission claims. State uncertainty. Never invent requirements or admission chances.",
                                           "input": f"Context: {context or 'No verified program data available.'}\nQuestion: {message}"})
        response.raise_for_status()
        data = response.json()
    answer = "".join(part.get("text", "") for output in data.get("output", []) for part in output.get("content", []) if part.get("type") == "output_text")
    return {"answer": answer or "No answer available.", "sources": sources, "configured": True}
