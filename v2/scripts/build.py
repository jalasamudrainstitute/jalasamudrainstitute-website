from pathlib import Path
import json,re,shutil,html
root=Path(__file__).resolve().parents[2]
src=root/'v2'
out=root/'v2-dist'
if out.exists(): shutil.rmtree(out)
shutil.copytree(src,out,ignore=shutil.ignore_patterns('scripts','README.md','RELEASE-CHECKLIST.md'))
legacy_assets=root/'assets'/'original'
if legacy_assets.is_dir(): shutil.copytree(legacy_assets,out/'assets'/'original',dirs_exist_ok=True)
records=json.loads((src/'data/publications.json').read_text())['publications']
for p in records:
    legacy=(root/'articles'/p['slug']/'index.html').read_text()
    body=re.search(r'<article[^>]*>(.*?)</article>',legacy,re.S|re.I)
    if not body: raise ValueError(p['slug'])
    title=html.escape(p['title'])
    original_body=body.group(1)
    original_body=re.sub(r'<!--\s*/?wp:[\s\S]*?-->', '', original_body)
    original_body=original_body.replace('https://jalasamudrainstitute.pages.dev/assets/','/assets/')
    original_body=re.sub(r'<img(?![^>]*\bloading=)', '<img loading="lazy"', original_body, flags=re.I)
    source_link=re.search(r'<a href="(https://jalasamudrainstitute.wordpress.com/[^\"]+)">Lihat publikasi asli',legacy)
    source_note=('<p class="source-link"><a href="'+html.escape(source_link.group(1),quote=True)+'">Lihat publikasi asli di WordPress</a></p>') if source_link else ''
    page='<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>'+title+' — JSI</title><link rel="stylesheet" href="../../assets/site.css"><link rel="stylesheet" href="../../assets/article.css"></head><body><header class="masthead"><a href="../../">Jala Samudra Institute</a></header><nav class="nav"><div class="wrap"><a href="../../">Home</a><a href="../../publications/">Publications</a><a href="../../research/">Research</a><a href="../../about/">About</a><a href="../../contact/">Contact</a></div></nav><main id="main-content" class="reading"><header class="article-heading"><p class="eyebrow">Publikasi JSI</p><h1>'+title+'</h1><p class="article-meta"><time datetime="'+html.escape(p.get('published',''))+'">'+html.escape(p.get('published',''))+'</time></p></header><article class="article-body">'+original_body+'</article><div class="article-end">'+source_note+'<p><a href="../../publications/">← Kembali ke arsip publikasi</a></p></div></main><footer><div class="wrap"><span>Jala Samudra Institute</span><a href="mailto:jalasamudrainstitute@gmail.com">Hubungi kami</a></div></footer></body></html>'
    target=out/'articles'/p['slug']/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(page,encoding='utf-8')

# Consistent keyboard skip navigation across the complete static preview.
for page_file in out.rglob('index.html'):
    page_html=page_file.read_text(encoding='utf-8')
    if '<main' not in page_html: continue
    if 'id="main-content"' not in page_html:
        page_html=re.sub(r'<main(\s|>)',r'<main id="main-content"\1',page_html,count=1)
    skip_target='#main-content' if 'id="main-content"' in page_html else '#home'
    page_html=page_html.replace('<body>','<body><a class="skip-link" href="'+skip_target+'">Langsung ke konten</a>',1)
    page_file.write_text(page_html,encoding='utf-8')

# Private preview only: block indexing until editorial and deployment sign-off.
(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
print('Generated',len(records),'articles')
