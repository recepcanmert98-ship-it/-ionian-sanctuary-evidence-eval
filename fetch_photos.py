#!/usr/bin/env python3
"""Download four licensed public Wikimedia photo thumbnails (no credentials).

Smaller JPEGs are preferred to original multi-megabyte files so the final
hackathon ZIP remains below 50 MiB. Manual downloads are supported and retained.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
PHOTO_DIR = ROOT / "photos"
MANIFEST = PHOTO_DIR / "manifest.json"
MAX_BYTES = 12 * 1024 * 1024  # cap unattended thumbnail downloads
MAX_LOCAL_BYTES = 45 * 1024 * 1024  # allow manually saved originals
MIN_BYTES = 12_000


def image_is_valid(data: bytes, max_bytes: int = MAX_LOCAL_BYTES) -> bool:
    # Reject HTML errors or truncated/empty bodies in place of real JPEGs.
    return (MIN_BYTES <= len(data) <= max_bytes and
            data.startswith(b"\xff\xd8\xff") and data.rstrip().endswith(b"\xff\xd9"))


def candidate_urls(entry: dict) -> list[str]:
    """Try two official Wikimedia thumbnail CDNs, then its file redirect.

    Thumbnail downloads use 960 pixels to avoid Claros's 28 MB original.
    """
    src = entry["url"]
    parsed = urlsplit(src)
    rel = parsed.path.split("/commons/", 1)[1]
    directory, filename = rel.rsplit("/", 1)
    # Quote commas/parentheses, using the same filename as stored on Commons.
    filename = quote(unquote(filename), safe="_-.()")
    thumb_suffix = f"commons/thumb/{directory}/{filename}/960px-{filename}"
    return [
        f"https://upload.wikimedia.org/wikipedia/{thumb_suffix}",
        f"https://thumb.wikimedia.org/wikipedia/{thumb_suffix}",
        f"https://commons.wikimedia.org/wiki/Special:Redirect/file/{filename}?width=960",
    ]


def retrieve(url: str) -> bytes:
    req = Request(url, headers={
        "User-Agent": "IonianSanctuaryResearchEvaluation/1.3.1 (licensed image reuse; Wikimedia source URLs credited)",
        "Accept": "image/jpeg,image/*;q=0.9,*/*;q=0.5",
    })
    with urlopen(req, timeout=25) as result:
        typ = result.headers.get("Content-Type", "").lower()
        data = result.read(MAX_BYTES + 1)
    if "text/html" in typ or not image_is_valid(data, max_bytes=MAX_BYTES):
        raise ValueError("response is not a complete JPEG under 12 MB")
    return data


def get_photos(manifest_path: Path = MANIFEST, dest: Path = PHOTO_DIR, pause: bool = True) -> bool:
    photos = json.loads(manifest_path.read_text(encoding="utf-8"))["photos"]
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    failures = []
    blocked = False
    for item in photos:
        target = dest / item["filename"]
        if target.exists() and image_is_valid(target.read_bytes()):
            data = target.read_bytes()
            print("READY:", target.name, f"({len(data):,} bytes; existing JPEG)")
        else:
            data = None
            problems = []
            for url in ([] if blocked else candidate_urls(item)):
                try:
                    fresh = retrieve(url)
                    pending = target.with_suffix(target.suffix + ".part")
                    pending.write_bytes(fresh)
                    pending.replace(target)
                    data = fresh
                    print("SAVED:", target.name, f"({len(data):,} bytes)")
                    break
                except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
                    code = getattr(error, "code", None)
                    problems.append(f"{code or type(error).__name__}: {error}")
                    print("  Alternative failed for", target.name, ":", problems[-1], file=sys.stderr)
                    if code == 429:
                        blocked = True
                        print("HTTP 429 rate limit: stopping automatic Wikimedia requests. Use IMPORT_PHOTOS_WINDOWS.cmd instead.", file=sys.stderr)
                        break
                    if pause:
                        time.sleep(0.2)
            if data is None:
                failures.append(item)
                print("FAILED:", item["filename"], file=sys.stderr)
                # Only print concise errors; URLs/credits are in the manifest.
        if data is not None:
            records.append({"id": item["id"], "filename": target.name,
                            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                            "source": item["source"]})

    (dest / "download_integrity.json").write_text(json.dumps({
        "retrieved": records, "count": len(records), "needed": len(photos),
        "format": "JPEG", "note": "Files may be 960-pixel Commons thumbnails or user-saved licensed JPEGs."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(records)}/{len(photos)} licensed photographs available locally.")
    if blocked:
        print("Automated download paused on HTTP 429 to respect Wikimedia rate limits.")
    if failures:
        print("\nIf your connection blocks Wikimedia automatic downloads:")
        print("  1. Open each Commons link listed below in your browser.")
        print("  2. Open the 960-pixel JPEG preview and save the image in photos\\")
        print("  3. Rename each file to its exact required name, then rerun this script.")
        print("  4. Only after 4/4 photos are ready, run BUILD_OFFLINE_WINDOWS.cmd.\n")
        for p in failures:
            print(f"  {p['filename']}: {p['source']}")
        print("\nSee PHOTO_RECOVERY.md for clickable links and screenshots instructions.")
    return not failures


if __name__ == "__main__":
    raise SystemExit(0 if get_photos() else 1)
