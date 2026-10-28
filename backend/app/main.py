from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .config import settings
from .db import Base, SessionLocal, engine, get_db
from .matching import evaluate
from .models import Program, Requirement, Scholarship, University
from .schemas import MatchResponse, ProgramOut, ScholarshipOut, StudentProfile, UniversityOut
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            seed(db)
    yield


app = FastAPI(title="AbroMap API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True,
                   allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "X-Admin-Token"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/countries")
def countries(db: Session = Depends(get_db)):
    rows = db.execute(select(University.country, func.count(Program.id)).join(Program).group_by(University.country)).all()
    return [{"code": code, "program_count": count} for code, count in rows]


def university_query():
    return select(University).options(selectinload(University.programs).selectinload(Program.requirements))


def program_query():
    return select(Program).options(selectinload(Program.requirements), selectinload(Program.university).selectinload(University.programs).selectinload(Program.requirements))


@app.get("/api/v1/universities", response_model=list[UniversityOut])
def universities(country: str | None = None, search: str | None = None, limit: int = Query(30, ge=1, le=100),
                 offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = university_query()
    if country:
        query = query.where(University.country == country.upper())
    if search:
        query = query.where(University.name.ilike(f"%{search}%"))
    return db.scalars(query.order_by(University.name).limit(limit).offset(offset)).all()


@app.get("/api/v1/universities/{slug}", response_model=UniversityOut)
def university(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(university_query().where(University.slug == slug))
    if not item:
        raise HTTPException(404, "University not found")
    return item


@app.get("/api/v1/programs", response_model=list[ProgramOut])
def programs(degree: str | None = None, field: str | None = None, country: str | None = None,
             limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = program_query().join(University)
    if degree:
        query = query.where(Program.degree == degree)
    if field:
        query = query.where(Program.field == field)
    if country:
        query = query.where(University.country == country.upper())
    return db.scalars(query.order_by(Program.name).limit(limit).offset(offset)).all()


@app.get("/api/v1/programs/{program_id}", response_model=ProgramOut)
def program(program_id: int, db: Session = Depends(get_db)):
    item = db.scalar(program_query().where(Program.id == program_id))
    if not item:
        raise HTTPException(404, "Program not found")
    return item


@app.post("/api/v1/matching/evaluate", response_model=MatchResponse)
def match(profile: StudentProfile, db: Session = Depends(get_db)):
    rows = db.scalars(program_query()).all()
    results = [result for row in rows if (result := evaluate(profile, row))]
    results.sort(key=lambda item: item.score, reverse=True)
    reason = None
    if not results:
        by_degree = [row for row in rows if row.degree == profile.degree]
        by_field = [row for row in by_degree if row.field == profile.field]
        by_country = [row for row in by_field if not profile.countries or row.university.country in profile.countries]
        if not rows:
            reason = "catalog_empty"
        elif not by_degree:
            reason = "degree_unavailable"
        elif not by_field:
            reason = "field_unavailable"
        elif not by_country:
            reason = "country_unavailable"
        elif profile.university_id:
            reason = "university_unavailable"
    return MatchResponse(results=results, total=len(results), no_match_reason=reason)


@app.get("/api/v1/scholarships", response_model=list[ScholarshipOut])
def scholarships(country: str | None = None, degree: str | None = None, db: Session = Depends(get_db)):
    query = select(Scholarship)
    if country:
        query = query.where((Scholarship.country == country.upper()) | (Scholarship.country.is_(None)))
    if degree:
        query = query.where((Scholarship.degree == degree) | (Scholarship.degree.is_(None)))
    return db.scalars(query.order_by(Scholarship.name)).all()


@app.get("/api/v1/scholarships/{scholarship_id}", response_model=ScholarshipOut)
def scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    item = db.get(Scholarship, scholarship_id)
    if not item:
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
        item = db.scalar(program_query().where(Program.id == program_id))
        if item:
            req = item.requirements[0] if item.requirements else None
            context = f"Program: {item.name}. Tuition: {item.tuition_eur}. Teaching language: {item.teaching_language}. Requirement: {req.academic_year if req else 'unknown'}, IELTS {req.ielts_min if req else 'unknown'}, status {req.status if req else 'unknown'}. Demo: {item.is_demo}."
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
