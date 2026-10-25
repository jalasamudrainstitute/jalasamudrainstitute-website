#!/usr/bin/env python3
"""Static, dependency-free quality checks for the isolated JSI v2 website."""
from html.parser import HTMLParser
from pathlib import Path
import json
import html
import sys
import os
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
        if tag=='svg' and a.get('role')=='img' and not (a.get('aria-label') or a.get('aria-labelledby')): self.images.append({'src':'inline SVG','alt':None})
        if tag=='meta' and a.get('name')=='robots' and 'noindex' in a.get('content',''): self.robots=True

production=os.environ.get('CF_PAGES_PROJECT_NAME')=='jalasamudrainstitute' or os.environ.get('JSI_PRODUCTION')=='1'
site_origin='https://jalasamudrainstitute.pages.dev' if production else 'https://jsi-v2-review.pages.dev'
errors=[]
for page in PAGES:
    parser=Parser(); parser.feed(page.read_text(encoding='utf-8'))
    if not parser.title: errors.append(f'{page}: missing title')
    page_text=page.read_text(encoding='utf-8')
    if not page.is_relative_to(ROOT/'articles'):
        if 'aria-label="Navigasi utama"' not in page_text: errors.append(f'{page}: main navigation lacks accessible label')
        if '<h1' not in page_text: errors.append(f'{page}: missing primary heading')
    if page_text.count('class="skip-link"')!=1: errors.append(f'{page}: expected one keyboard skip link')
    if production:
        expected_route='/' if page==ROOT/'index.html' else '/'+page.parent.relative_to(ROOT).as_posix()+'/'
        expected_canonical=site_origin+expected_route
        if '<link rel="canonical" href="'+expected_canonical+'">' not in page_text:
            errors.append(f'{page}: missing or incorrect canonical URL')
        if 'application/ld+json' not in page_text:
            errors.append(f'{page}: missing JSON-LD structured data')
        if page.is_relative_to(ROOT/'articles'):
            if 'property="og:title"' not in page_text or 'property="og:url"' not in page_text:
                errors.append(f'{page}: missing Open Graph article metadata')
            if 'name="twitter:card"' not in page_text:
                errors.append(f'{page}: missing social preview metadata')
            from html.parser import HTMLParser as _HTMLParser
            class _JSONLD(_HTMLParser):
                def __init__(self): super().__init__(); self.active=False; self.data=[]
                def handle_starttag(self,tag,attrs):
                    if tag=='script' and dict(attrs).get('type')=='application/ld+json': self.active=True
                def handle_data(self,data):
                    if self.active: self.data.append(data)
                def handle_endtag(self,tag):
                    if tag=='script': self.active=False
            ld=_JSONLD();ld.feed(page_text)
            try:
                article_schema=json.loads(''.join(ld.data))
                for field in ('headline','datePublished','publisher','author','description','mainEntityOfPage','isAccessibleForFree'):
                    if field not in article_schema: errors.append(f'{page}: JSON-LD missing {field}')
            except (ValueError,TypeError):
                errors.append(f'{page}: invalid JSON-LD article metadata')
    if page==ROOT/'index.html':
        for pub in json.loads((ROOT/'data/publications.json').read_text(encoding='utf-8'))['publications']:
            if 'href="'+pub['url']+'"' not in page_text:
                errors.append(f'homepage missing static article link: {pub["slug"]}')
    if page.is_relative_to(ROOT/'publications'):
        from html.parser import HTMLParser as _HTMLParser
        class _Archive(_HTMLParser):
            def __init__(self): super().__init__(); self.urls=[]
            def handle_starttag(self,tag,attrs):
                if tag=='a':
                    href=dict(attrs).get('href','')
                    if href.startswith('/articles/'): self.urls.append(href)
        archive=_Archive();archive.feed(page_text)
        catalog=json.loads((ROOT/'data/publications.json').read_text(encoding='utf-8'))['publications']
        if sorted(archive.urls)!=sorted(p['url'] for p in catalog): errors.append('static archive links differ from publication catalog')
    if '<html lang="id"' not in page.read_text(encoding='utf-8'): errors.append(f'{page}: missing Indonesian language declaration')
    if 'name="viewport"' not in page.read_text(encoding='utf-8'): errors.append(f'{page}: missing mobile viewport')
    if page.is_relative_to(ROOT/'articles') and len(page.read_text(encoding='utf-8')) < 500: errors.append(f'{page}: article unexpectedly short')
    if production and parser.robots: errors.append(f'{page}: production page must be indexable')
    if not production and not parser.robots: errors.append(f'{page}: preview page must remain noindex')
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
        if '<h1>'+html.escape(p['title'])+'</h1>' not in content: errors.append(f'{slug}: article heading mismatch')
        if '<time datetime="'+p.get('published','')+'">' not in content: errors.append(f'{slug}: article date mismatch')
        if 'Lihat publikasi asli di WordPress' not in content: errors.append(f'{slug}: missing original publication link')
# Check one-to-one historical WordPress source mapping before any future redirects.
map_file=ROOT/'data/source-url-map.json'
if not map_file.is_file():
    errors.append('missing source URL map')
else:
    mapping=json.loads(map_file.read_text(encoding='utf-8')).get('mappings',[])
    old_urls=[m['original_wordpress_url'] for m in mapping]
    mapped_paths=[m['v2_path'] for m in mapping]
    if len(mapping)!=len(publications): errors.append('source URL map count mismatch')
    if len(set(old_urls))!=len(old_urls): errors.append('duplicate WordPress source URLs')
    if sorted(mapped_paths)!=sorted(p['url'] for p in publications): errors.append('source URL map differs from publication catalog')
    if any(not u.startswith('https://jalasamudrainstitute.wordpress.com/') for u in old_urls): errors.append('unexpected historical URL origin')
urls=[p['url'] for p in publications]
if len(urls)!=len(set(urls)): errors.append('duplicate publication URLs')
for p in publications:
    if not p['url'].startswith('/articles/'): errors.append(f"unexpected canonical article URL: {p['url']}")
    if not (ROOT / 'articles' / p['slug'] / 'index.html').is_file(): errors.append(f"missing generated article: {p['slug']}")
expected_robots=('User-agent: *\nAllow: /\nSitemap: '+site_origin+'/sitemap.xml\n') if production else 'User-agent: *\nDisallow: /\n'
if (ROOT/'robots.txt').read_text(encoding='utf-8')!=expected_robots: errors.append('robots.txt does not match deployment environment')
if len(PAGES)!=len(publications)+5: errors.append(f'expected {len(publications)+5} built pages; found {len(PAGES)}')
from xml.etree import ElementTree as ET
for filename in ('sitemap.xml','feed.xml'):
    try: ET.parse(ROOT/filename)
    except (OSError, ET.ParseError): errors.append('invalid XML: '+filename)
# Check that XML files actually cover the published preview routes.
try:
    sitemap_root=ET.parse(ROOT/'sitemap.xml').getroot()
    locations=[node.text for node in sitemap_root.findall('.//{*}loc')]
    expected_paths=['/','/publications/','/research/','/about/','/contact/']+[p['url'] for p in publications]
    expected_locations=[site_origin+p for p in expected_paths]
    if len(locations)!=len(expected_locations) or set(locations)!=set(expected_locations):
        errors.append('sitemap coverage does not match the 15 preview routes')
    rss_root=ET.parse(ROOT/'feed.xml').getroot()
    rss_items=rss_root.findall('./channel/item')
    rss_links=[item.findtext('link') for item in rss_items]
    expected_article_links=[site_origin+p['url'] for p in publications]
    if len(rss_links)!=len(expected_article_links) or set(rss_links)!=set(expected_article_links):
        errors.append('RSS feed does not match publication catalog')
except (OSError, ET.ParseError):
    pass
print(f'Checked {len(PAGES)} pages and {len(publications)} publication records.')
if errors:
    print('\n'.join('FAIL: '+e for e in errors));sys.exit(1)
print('PASS: internal routes, assets, prototype indexing, publication uniqueness.')
