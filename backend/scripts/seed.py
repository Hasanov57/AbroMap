from app.db import Base, SessionLocal, engine
from app.seed import seed

Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed(db)
print("Demo data seeded (idempotent).")
