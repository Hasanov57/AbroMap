"""Import ROR v2 records by a few IDs or from the official bulk dump."""

import argparse
from pathlib import Path

from app.db import SessionLocal
from app.ingestion.import_service import import_ror
from app.ingestion.ror import fetch_ror_ids, iter_ror_dump


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["ror"], default="ror")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids", nargs="+", help="Small validation sample of ROR IDs")
    group.add_argument("--dump", type=Path, help="Official ROR v2 JSON or ZIP data dump")
    parser.add_argument("--country", help="Restrict imported records to ISO country code")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--source-version")
    parser.add_argument("--execute", action="store_true", help="Write records; default is dry run")
    args = parser.parse_args()
    if args.batch_size < 1 or (args.limit is not None and args.limit < 1):
        parser.error("--batch-size and --limit must be positive")
    if args.dump and not args.dump.is_file():
        parser.error("Dump file does not exist")
    payloads = fetch_ror_ids(args.ids) if args.ids else iter_ror_dump(args.dump)
    if args.country:
        code = args.country.upper()
        payloads = (item for item in payloads if any(
            loc.get("geonames_details", {}).get("country_code") == code
            for loc in item.get("locations") or []))
    with SessionLocal() as db:
        print(import_ror(db, payloads, dry_run=not args.execute, limit=args.limit,
                         batch_size=args.batch_size, source_version=args.source_version))


if __name__ == "__main__":
    main()
