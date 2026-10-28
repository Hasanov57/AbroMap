"""Extract ROR records for the source-checked program sample from the bundled snapshot."""

import json

from app.catalog import DATA_DIR, load_data
from app.ingestion.ror import iter_ror_dump


def main() -> None:
    ids = {item["ror_id"] for item in load_data("official_sample.json")["programs"]}
    rows = [row for row in iter_ror_dump(DATA_DIR / "ror_europe_china.zip") if row.get("id") in ids]
    if {row["id"] for row in rows} != ids:
        raise ValueError("Official sample ROR IDs missing from bundled ROR release")
    target = DATA_DIR / "ror_official_sample.json"
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} ROR records to {target}")


if __name__ == "__main__":
    main()
