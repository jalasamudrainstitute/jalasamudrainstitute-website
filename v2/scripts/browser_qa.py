#!/usr/bin/env python3
"""Browser QA for the JSI V2 static build, run in GitHub Actions."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import os

ROOT=Path(__file__).resolve().parents[2]/'v2-dist'
SCREENSHOTS=Path('qa-screenshots')
SCREENSHOTS.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base=os.environ.get('JSI_QA_BASE_URL',f'http://127.0.0.1:{server.server_port}').rstrip('/')
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width in (360,390,768,1024,1440):
            page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
            for route,name in (('/','home'),('/publications/','publications'),('/about/','about'),('/research/','research'),('/contact/','contact')):
                page.goto(base+route,wait_until='networkidle')
                assert page.locator('main').count()==1,(width,route,'missing main')
                assert page.locator('h1').count()>=1,(width,route,'missing h1')
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2'),(width,route,'horizontal overflow')
                page.screenshot(path=str(SCREENSHOTS/f'{name}-{width}.png'),full_page=True)
            # Inspect every migrated article, not just the five landing pages.
            import json
            catalog=json.loads((ROOT/'data'/'publications.json').read_text(encoding='utf-8'))['publications']
            for publication in catalog:
                page.goto(base+publication['url'],wait_until='networkidle')
                assert ' '.join(page.locator('h1').inner_text().split())==' '.join(publication['title'].split()),(width,publication['slug'],'wrong article title')
                assert page.locator('article.article-body').count()==1,(width,publication['slug'],'article body missing')
                assert page.locator('article.article-body').inner_text().strip(),(width,publication['slug'],'empty article')
                if publication['published'].startswith('2024'):
                    assert page.locator('article.article-body iframe[src^="https://www.youtube-nocookie.com/embed/"]').count()==1,(width,publication['slug'],'missing video player')
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2'),(width,publication['slug'],'article horizontal overflow')
                broken=page.locator('article.article-body img').evaluate_all('(images) => images.filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)')
                assert not broken,(width,publication['slug'],'broken article images',broken)
                missing_links=page.locator('article.article-body a[href^="/"]').evaluate_all('(links) => links.filter(a => !a.getAttribute("href").startsWith("//")).map(a => a.getAttribute("href"))')
                for href in missing_links:
                    from urllib.parse import urlsplit
                    relative=urlsplit(href).path.lstrip('/')
                    target=ROOT/relative
                    assert target.is_file() or (target/'index.html').is_file(),(publication['slug'],'broken local article link',href)
                if width in (390,1440):
                    page.screenshot(path=str(SCREENSHOTS/f"article-{publication['slug'][:36]}-{width}.png"),full_page=True)
            page.goto(base+'/publications/',wait_until='networkidle')
            assert page.locator('#stories article').count()==10,(width,'archive count')
            page.locator('#search').fill('no-match-zzzz')
            assert page.locator('#stories article').count()==0,(width,'search not filtering')
            assert page.locator('#empty').is_visible(),(width,'empty state missing')
            page.locator('#search').fill('')
            assert page.locator('#stories article').count()==10,(width,'search reset')
            page.locator('#topic').select_option(index=1)
            assert 0<page.locator('#stories article').count()<=10,(width,'topic filter')
            page.close()
        browser.close()
finally:
    server.shutdown()
print('PASS: 5 widths, 5 core pages, 10 article pages, archive search and filtering.')
