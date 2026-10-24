#!/usr/bin/env python3
"""Static, dependency-free quality checks for the isolated JSI v2 website."""
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2] / 'v2-dist'
if not ROOT.is_dir():
    raise SystemExit('Run python3 v2/scripts/build.py before checking the generated site')
PAGES = sorted(ROOT.rglob('index.html'))
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set(); self.title=False; self.robots=False; self.images=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag in ('script','link','img'):
            k='src' if tag in ('script','img') else 'href'
            if a.get(k): self.links.append(a[k])
        if tag=='img': self.images.append(a)
        if tag=='title': self.title=True
        if tag=='meta' and a.get('name')=='robots' and 'noindex' in a.get('content',''): self.robots=True

errors=[]
for page in PAGES:
    parser=Parser(); parser.feed(page.read_text(encoding='utf-8'))
    if not parser.title: errors.append(f'{page}: missing title')
    if '<html lang="id"' not in page.read_text(encoding='utf-8'): errors.append(f'{page}: missing Indonesian language declaration')
    if 'name="viewport"' not in page.read_text(encoding='utf-8'): errors.append(f'{page}: missing mobile viewport')
    if page.is_relative_to(ROOT/'articles') and len(page.read_text(encoding='utf-8')) < 500: errors.append(f'{page}: article unexpectedly short')
    if not parser.robots: errors.append(f'{page}: prototype must remain noindex')
    if not any(link.startswith('#') and link[1:] in parser.ids for link in parser.links): errors.append(f'{page}: missing functional in-page navigation')
    if page.is_relative_to(ROOT/'articles') and '<article class="article-body">' not in page.read_text(encoding='utf-8'): errors.append(f'{page}: missing reading content')
    for image in parser.images:
        if 'alt' not in image: errors.append(f'{page}: image missing alt attribute')
    for link in parser.links:
        parsed=urlsplit(link)
        if parsed.scheme in ('http','https','mailto','tel','data') or link.startswith('//'): continue
        if link.startswith('#'):
            if parsed.fragment and unquote(parsed.fragment) not in parser.ids: errors.append(f'{page}: unresolved anchor {link}')
            continue
        target=((ROOT if parsed.path.startswith('/') else page.parent)/unquote(parsed.path).lstrip('/')).resolve() if parsed.path else page
        if ROOT not in target.parents and target!=ROOT: errors.append(f'{page}: link escapes v2 root: {link}'); continue
        if target.is_dir(): target=target/'index.html'
        if not target.is_file(): errors.append(f'{page}: missing local target {link}')

publications=json.loads((ROOT/'data/publications.json').read_text(encoding='utf-8'))['publications']
slugs=[p['slug'] for p in publications]
if len(slugs)!=len(set(slugs)): errors.append('duplicate publication slugs')
# Validate archive taxonomy, dates, article metadata and source traceability.
from datetime import date
catalog=json.loads((ROOT/'data/publications.json').read_text(encoding='utf-8'))
known_domains=set(catalog.get('domains',[]))
for p in publications:
    slug=p.get('slug','')
    if not p.get('title','').strip(): errors.append(f'{slug}: missing title')
    if not p.get('domains'): errors.append(f'{slug}: missing research domain')
    for domain in p.get('domains',[]):
        if domain not in known_domains: errors.append(f'{slug}: unlisted domain {domain}')
    try: date.fromisoformat(p.get('published',''))
    except ValueError: errors.append(f'{slug}: invalid publication date')
    article=ROOT/'articles'/slug/'index.html'
    if article.is_file():
        content=article.read_text(encoding='utf-8')
        if '<h1>'+__import__('html').escape(p['title'])+'</h1>' not in content: errors.append(f'{slug}: article heading mismatch')
        if '<time datetime="'+p.get('published','')+'">' not in content: errors.append(f'{slug}: article date mismatch')
        if 'Lihat publikasi asli di WordPress' not in content: errors.append(f'{slug}: missing original publication link')
urls=[p['url'] for p in publications]
if len(urls)!=len(set(urls)): errors.append('duplicate publication URLs')
for p in publications:
    if not p['url'].startswith('/articles/'): errors.append(f"unexpected canonical article URL: {p['url']}")
    if not (ROOT / 'articles' / p['slug'] / 'index.html').is_file(): errors.append(f"missing generated article: {p['slug']}")
if (ROOT/'robots.txt').read_text(encoding='utf-8')!='User-agent: *\nDisallow: /\n': errors.append('prototype robots.txt must block indexing')
if len(PAGES)!=len(publications)+5: errors.append(f'expected {len(publications)+5} built pages; found {len(PAGES)}')
print(f'Checked {len(PAGES)} pages and {len(publications)} publication records.')
if errors:
    print('\n'.join('FAIL: '+e for e in errors));sys.exit(1)
print('PASS: internal routes, assets, prototype indexing, publication uniqueness.')
