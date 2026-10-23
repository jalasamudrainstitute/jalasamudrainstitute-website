#!/usr/bin/env python3
"""Migrate original WordPress media to local static assets; preserve originals."""
import json
import pathlib
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "asset-migration-manifest.json"
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entries = [manifest["logo"], *manifest["featured_images"], *manifest["documents"]]
downloaded = {}
for entry in entries:
    source = entry["source"]
    target = entry.get("local_target") or "/assets/original/" + source.rsplit("/", 1)[-1]
    entry["local_target"] = target
    path = ROOT / target.lstrip("/")
    if path.exists() and path.stat().st_size:
        downloaded[source] = target
        entry["status"] = "local_original_verified"
        continue
    try:
        req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0 (compatible; JSI-MediaMigration/1.0)"})
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = response.read(25_000_001)
            mime = response.headers.get("Content-Type", "").lower()
        if len(payload) > 25_000_000 or not payload:
            raise ValueError("Empty or oversized file")
        suffix = path.suffix.lower()
        allowed = {"png": ("image/png",), "jpg": ("image/jpeg",), "jpeg": ("image/jpeg",), "webp": ("image/webp",), "pdf": ("application/pdf",), "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/zip")}
        if not any(mime.startswith(m) for m in allowed.get(suffix.lstrip("."), ())):
            raise ValueError("Unexpected MIME type: " + mime)
        if suffix == ".png" and not payload.startswith(bytes.fromhex("89504e470d0a1a0a")):
            raise ValueError("Invalid PNG signature")
        if suffix == ".pdf" and not payload.startswith(b"%PDF"):
            raise ValueError("Invalid PDF signature")
        if suffix == ".docx" and not payload.startswith(b"PK"):
            raise ValueError("Invalid DOCX signature")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        downloaded[source] = target
        entry["status"] = "local_original_verified"
        print("Saved", target, len(payload), "bytes")
    except (urllib.error.URLError, ValueError, TimeoutError, OSError) as exc:
        entry["status"] = "remote_original_pending_binary_transfer"
        print("SKIP", source, str(exc))

if downloaded:
    for html_path in [ROOT / "index.html", *ROOT.glob("articles/**/index.html"), ROOT / "research/index.html"]:
        if not html_path.exists():
            continue
        html = html_path.read_text(encoding="utf-8")
        new = html
        for source, target in downloaded.items():
            new = new.replace(source, target)
        if new != html:
            html_path.write_text(new, encoding="utf-8")
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")
print("Migrated", len(downloaded), "of", len({e["source"] for e in entries}), "unique original assets")
