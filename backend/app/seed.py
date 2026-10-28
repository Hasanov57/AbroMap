from sqlalchemy.orm import Session
from .models import Program, Requirement, Scholarship, University


DEMO_UNIVERSITIES = [
    ("demo-berlin-institute", "Demo Berlin Institute", "Berlin", "DE", "Computer Science", "computer_science", 0),
    ("demo-milan-academy", "Demo Milan Academy", "Milan", "IT", "Artificial Intelligence", "artificial_intelligence", 4000),
    ("demo-budapest-college", "Demo Budapest College", "Budapest", "HU", "Data Science", "data_science", 2800),
    ("demo-hamburg-school", "Demo Hamburg School", "Hamburg", "DE", "Software Engineering", "software_engineering", 6500),
    ("demo-rome-institute", "Demo Rome Institute", "Rome", "IT", "Business Administration", "business_administration", 9000),
]


def seed(db: Session) -> None:
    for slug, university_name, city, country, program_name, field, tuition in DEMO_UNIVERSITIES:
        university = db.query(University).filter_by(slug=slug).first()
        if university is None:
            university = University(slug=slug, name=university_name, city=city, country=country,
                                    description="Synthetic demonstration institution. All associated program details are examples, not admission facts.", is_demo=True)
            db.add(university)

        for degree, prefix in (("bachelor", "BSc"), ("master", "MSc"), ("phd", "PhD")):
            title = f"{prefix} {program_name}"
            if any(program.name == title and program.degree == degree for program in university.programs):
                continue
            program = Program(name=title, degree=degree, field=field,
                              tuition_eur=tuition if degree == "master" else None,
                              duration_months=24 if degree == "master" else None,
                              teaching_language="English", is_demo=True)
            if degree == "master":
                program.requirements.append(Requirement(academic_year="2025/2026", ielts_min=6.5 if country != "HU" else 6.0,
                                                         min_gpa=3.0, gpa_scale=4.0, status="unverified"))
            university.programs.append(program)
    if not db.query(Scholarship).filter_by(name="Demo full scholarship").first():
        db.add(Scholarship(name="Demo full scholarship", country=None, degree="master", coverage="full",
                           description="Synthetic example used to demonstrate scholarship discovery. Eligibility and funding are not real.", is_demo=True))
    db.commit()
