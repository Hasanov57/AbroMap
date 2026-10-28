"""Build a reproducible Europe/China/US university snapshot from the latest official ROR dump."""

import argparse
import hashlib
import json
import tempfile
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

import httpx

from app.catalog import DATA_DIR, load_data
from app.ingestion.ror import iter_ror_dump, normalize_ror_record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DATA_DIR / "ror_europe_china.zip")
    parser.add_argument("--manifest", type=Path, default=DATA_DIR / "ror_snapshot_manifest.json")
    args = parser.parse_args()
    allowed = {item["iso_code"] for item in load_data("countries.json")["countries"] if item["enabled"]}
    headers = {"User-Agent": "AbroMap/0.2 (research catalog; https://github.com/Hasanov57/AbroMap)"}
    with httpx.Client(headers=headers, follow_redirects=True, timeout=120) as client:
        response = client.get("https://zenodo.org/api/records/6347574")
        response.raise_for_status()
        release = response.json()
        source = next(item for item in release["files"] if item["key"].endswith(".zip"))
        expected_hash = source["checksum"].removeprefix("md5:")
        with tempfile.TemporaryDirectory() as temp:
            download = Path(temp) / source["key"]
            digest = hashlib.md5()
            with client.stream("GET", source["links"]["self"]) as stream:
                stream.raise_for_status()
                with download.open("wb") as target:
                    for chunk in stream.iter_bytes(1024 * 1024):
                        target.write(chunk)
                        digest.update(chunk)
            if digest.hexdigest() != expected_hash:
                raise ValueError("ROR release checksum does not match Zenodo metadata")
            processed = accepted = 0
            countries = Counter()
            seen = set()
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                with archive.open("ror-selected.json", "w") as target:
                    target.write(b"[")
                    for payload in iter_ror_dump(download):
                        processed += 1
                        record = normalize_ror_record(payload, allowed)
                        if record is None or record.ror_id in seen:
                            continue
                        seen.add(record.ror_id)
                        target.write((b"," if accepted else b"") +
                                     json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
                        accepted += 1
                        countries[record.country] += 1
                    target.write(b"]")
    if accepted < 1000:
        args.output.unlink(missing_ok=True)
        raise ValueError(f"Only {accepted} institutions passed filtering; review the ROR format")
    manifest = {
        "source": "ROR data dump", "release_doi": f"https://doi.org/{release['doi']}",
        "release_date": release["metadata"]["publication_date"],
        "source_file": source["key"], "source_md5": expected_hash,
        "built_on": date.today().isoformat(), "license": "CC0 1.0",
        "source_records": processed, "selected_institutions": accepted,
        "countries": dict(sorted(countries.items())),
        "selection": "active education records with a university or equivalent name cue in supported countries",
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"release": release["doi"], "processed": processed,
                      "selected": accepted, "snapshot_bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
