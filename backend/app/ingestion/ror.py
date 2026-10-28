"""ROR v2 normalization and streaming dump reader."""

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import httpx
import ijson

from app.catalog import normalize_text


HIGHER_ED = re.compile(
    r"university|universit|universität|universidade|universidad|università|"
    r"hochschule|politecnico|polytechnic|institute of technology|"
    r"technical university|college|école|akademi|academy",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InstitutionRecord:
    ror_id: str
    name: str
    city: str
    country: str
    website: str | None
    aliases: tuple[tuple[str, str | None], ...]
    identifiers: tuple[tuple[str, str], ...]
    source_url: str
    institution_type: str = "higher_education"


def normalize_ror_record(payload: dict, allowed_countries: set[str]) -> InstitutionRecord | None:
    """Conservatively accept active ROR education records with an HEI name cue."""
    if payload.get("status") != "active" or "education" not in payload.get("types", []):
        return None
    names = payload.get("names") or []
    display = next((item for item in names if "ror_display" in item.get("types", [])), None)
    if not display or not HIGHER_ED.search(display.get("value", "")):
        return None
    location = next((item.get("geonames_details", {}) for item in payload.get("locations") or []
                     if item.get("geonames_details", {}).get("country_code")), {})
    country = location.get("country_code")
    if country not in allowed_countries:
        return None
    ror_id = str(payload.get("id", ""))
    if not re.fullmatch(r"https://ror\.org/[a-z0-9]{9}", ror_id):
        return None
    website = next((item.get("value") for item in payload.get("links") or []
                    if item.get("type") == "website" and item.get("value", "").startswith("https://")), None)
    aliases = tuple(dict.fromkeys((item["value"], item.get("lang")) for item in names
                                  if item.get("value") and normalize_text(item["value"]) != normalize_text(display["value"])))
    identifiers = [("ror", ror_id)]
    for external in payload.get("external_ids") or []:
        scheme = str(external.get("type", "")).lower()
        if scheme not in {"isni", "wikidata", "grid"}:
            continue
        identifiers.extend((scheme, str(value)) for value in external.get("all") or [] if value)
    return InstitutionRecord(ror_id=ror_id, name=display["value"], city=location.get("name") or "",
                             country=country, website=website, aliases=aliases,
                             identifiers=tuple(dict.fromkeys(identifiers)), source_url=ror_id)


def iter_ror_dump(path: Path) -> Iterator[dict]:
    """Stream a ROR JSON array from a JSON file or official release ZIP."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".json") and "schema_v1" not in name]
            if not names:
                raise ValueError("No ROR JSON file found in ZIP")
            with archive.open(sorted(names)[0]) as stream:
                yield from ijson.items(stream, "item", use_float=True)
    elif path.suffix.lower() == ".json":
        with path.open("rb") as stream:
            yield from ijson.items(stream, "item", use_float=True)
    else:
        raise ValueError("ROR dump must be .json or .zip")


def fetch_ror_ids(ids: list[str]) -> Iterator[dict]:
    """Fetch a small validation sample; bulk imports must use the dump."""
    with httpx.Client(timeout=30, follow_redirects=True,
                      headers={"User-Agent": "AbroMap/0.2 (catalog validation; ROR v2)"}) as client:
        for raw_id in ids:
            identifier = raw_id.removeprefix("https://ror.org/")
            if not re.fullmatch(r"[a-z0-9]{9}", identifier):
                raise ValueError(f"Invalid ROR identifier: {raw_id}")
            for attempt in range(5):
                try:
                    response = client.get(f"https://api.ror.org/v2/organizations/{identifier}")
                    if response.status_code in {429, 500, 502, 503, 504}:
                        raise httpx.HTTPStatusError("Temporary ROR error", request=response.request, response=response)
                    response.raise_for_status()
                    yield response.json()
                    break
                except (httpx.TransportError, httpx.HTTPStatusError):
                    if attempt == 4:
                        raise
                    import time
                    time.sleep(min(2 ** attempt, 16))
