from app.catalog import initialize_catalog
from app.db import SessionLocal


def main() -> None:
    with SessionLocal() as db:
        print(initialize_catalog(db))


if __name__ == "__main__":
    main()
