import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.catalog import initialize_catalog
from app.db import Base, get_db
from app.main import app
from app.models import AcademicField, ExamRequirement, Program, Requirement, University, UniversityAlias


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)
    with factory() as session:
        initialize_catalog(session)
        yield session
    engine.dispose()


@pytest.fixture
def client(db: Session):
    cs = db.query(AcademicField).filter_by(slug="computer-science").one()
    info = db.query(AcademicField).filter_by(slug="information-systems").one()
    first = University(slug="fixture-university-de", name="Fixture University", normalized_name="fixture university",
                       city="Berlin", country="DE", ror_id="https://ror.org/02kkvpp62",
                       website="https://example.org", is_demo=False, status="active")
    first.aliases.append(UniversityAlias(name="Fixture Hochschule", locale="de",
                                         normalized_name="fixture hochschule"))
    first.programs.extend([
        Program(name="Computer Science MSc", degree="master", field="computer-science", academic_field_id=cs.id,
                teaching_language="English", is_demo=False, data_status="verified_source",
                official_url="https://example.org/cs", source_publisher="Fixture", tuition_eur=None),
        Program(name="Information Systems MSc", degree="master", field="information-systems", academic_field_id=info.id,
                teaching_language="English", is_demo=False, data_status="verified_source",
                official_url="https://example.org/is", tuition_eur=None),
    ])
    first.programs[0].requirements.append(Requirement(
        academic_year="2025/2026", applicant_category="international", status="verified_historical",
        source_url="https://example.org/requirements/2025", min_gpa=None, ielts_min=6.5,
    ))
    first.programs[0].requirements.append(Requirement(
        academic_year="2027/2028", applicant_category="international", status="verified_current",
        source_url="https://example.org/requirements/2027", min_gpa=None,
        previous_study_notes="Prior coursework is evaluated individually.",
    ))
    first.programs[0].requirements[-1].exams.append(ExamRequirement(
        exam_type="hsk", minimum_level="5", minimum_score=180, status="verified_current",
        waiver_possible=True,
    ))
    catalog_only = University(slug="fixture-university-cn", name="Catalog Only University",
                              normalized_name="catalog only university", city="Beijing", country="CN",
                              ror_id="https://ror.org/03cve4549", is_demo=False, status="active")
    demo = University(slug="demo-berlin-institute", name="Demo Berlin Institute",
                      normalized_name="demo berlin institute", city="Berlin", country="DE", is_demo=True,
                      status="active")
    demo.programs.append(Program(name="Demo MSc", degree="master", field="computer-science",
                                 academic_field_id=cs.id, teaching_language="English", is_demo=True,
                                 data_status="verified_source"))
    db.add_all([first, catalog_only, demo])
    db.commit()

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
