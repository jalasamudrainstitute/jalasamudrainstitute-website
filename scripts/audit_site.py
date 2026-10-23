#!/usr/bin/env python3
"""Fail CI when local site links/assets or publication sitemap entries are missing."""
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, unquote

root = Path(__file__).resolve().parents[1]
site = "jalasamudrainstitute.pages.dev"
issues = []
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for k in ("src", "href"):
            if k in d:
                self.links.append(d[k])

pages = list(root.glob("**/index.html"))
for page in pages:
    parser = Links()
    parser.feed(page.read_text(encoding="utf-8"))
    for url in parser.links:
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or url.startswith(("#", "mailto:", "tel:", "data:", "//")):
            continue
        path = unquote(parts.path)
        if not path:
            continue
        target = root / path.lstrip("/") if path.startswith("/") else page.parent / path
        if target.is_dir():
            target = target / "index.html"
        elif not target.suffix:
            target = target / "index.html"
        if not target.is_file():
            issues.append(f"{page.relative_to(root)}: missing local link {url}")
manifest = json.loads((root / "data/asset-migration-manifest.json").read_text(encoding="utf-8"))
entries = [manifest["logo"], *manifest["featured_images"], *manifest["documents"]]
for item in entries:
    if item["status"] == "local_original_verified":
        target = root / item["local_target"].lstrip("/")
        if not target.is_file() or target.stat().st_size == 0:
            issues.append(f"Missing migrated asset: {target.relative_to(root)}")
sitemap = ET.parse(root / "sitemap.xml")
urls = {n.text for n in sitemap.iter() if n.tag.endswith("}loc") or n.tag == "loc"}
for page in pages:
    relative = page.relative_to(root).parent.as_posix()
    url = "https://" + site + ("/" if relative == "." else "/" + relative + "/")
    if url not in urls:
        issues.append(f"Missing sitemap URL: {url}")
print(f"Checked {len(pages)} pages, {len(entries)} media entries, {len(urls)} sitemap URLs.")
for issue in issues:
    print("ERROR:", issue)
sys.exit(bool(issues))
