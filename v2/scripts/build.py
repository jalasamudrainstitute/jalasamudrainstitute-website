from pathlib import Path
import json,re,shutil,html,os
root=Path(__file__).resolve().parents[2]
src=root/'v2'
out=root/'v2-dist'
if out.exists(): shutil.rmtree(out)
shutil.copytree(src,out,ignore=shutil.ignore_patterns('scripts','README.md','RELEASE-CHECKLIST.md','WORDPRESS-PARITY-AUDIT.md'))
legacy_assets=root/'assets'/'original'
if legacy_assets.is_dir(): shutil.copytree(legacy_assets,out/'assets'/'original',dirs_exist_ok=True)
records=json.loads((src/'data/publications.json').read_text())['publications']
source_map=[]
for p in records:
    legacy=(root/'articles'/p['slug']/'index.html').read_text()
    body=re.search(r'<article[^>]*>(.*?)</article>',legacy,re.S|re.I)
    if not body: raise ValueError(p['slug'])
    title=html.escape(p['title'])
    seo_title=html.escape(p.get('seo_title') or p['title'])
    original_body=body.group(1)
    original_body=re.sub(r'<!--\s*/?wp:[\s\S]*?-->', '', original_body)
    # WordPress embed wrappers contain a bare YouTube URL, not a playable player.
    # Replace only the YouTube wrapper with a privacy-enhanced iframe; preserve all other content.
    def youtube_player(match):
        wrapper=match.group(0)
        video=re.search(r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})',wrapper)
        if not video: return wrapper
        video_id=video.group(1)
        return ('<div class="video-embed"><iframe loading="lazy" '
                'src="https://www.youtube-nocookie.com/embed/'+video_id+'" '
                'title="Video publikasi JSI" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')
    original_body=re.sub(r'<figure\b[^>]*class="[^"]*wp-block-embed[^"]*"[^>]*>[\s\S]*?</figure>',youtube_player,original_body,flags=re.I)

    original_body=original_body.replace('https://jalasamudrainstitute.pages.dev/assets/','/assets/')
    original_body=re.sub(r'<img(?![^>]*\bloading=)', '<img loading="lazy"', original_body, flags=re.I)
    summary=html.unescape(re.sub(r'<[^>]+>',' ',original_body))
    summary=' '.join(summary.split())[:155]
    description=html.escape(summary,quote=True)
    source_link=re.search(r'<a href="(https://jalasamudrainstitute.wordpress.com/[^\"]+)">Lihat publikasi asli',legacy)
    source_note=('<p class="source-link"><a href="'+html.escape(source_link.group(1),quote=True)+'">Lihat publikasi asli di WordPress</a></p>') if source_link else ''
    if not source_link: raise ValueError('Missing original WordPress URL: '+p['slug'])
    source_map.append({'original_wordpress_url':source_link.group(1),'v2_path':p['url'],'slug':p['slug']})
    page='<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta name="description" content="'+description+'"><title>'+seo_title+' — JSI</title><link rel="stylesheet" href="../../assets/site.css"><link rel="stylesheet" href="../../assets/article.css"></head><body><header class="masthead"><a href="../../">Jala Samudra Institute</a></header><nav class="nav" aria-label="Navigasi utama"><div class="wrap"><a href="../../">Home</a><a href="../../publications/">Publications</a><a href="../../research/">Research</a><a href="../../about/">About</a><a href="../../contact/">Contact</a></div></nav><main id="main-content" class="reading"><header class="article-heading"><p class="eyebrow">Publikasi JSI</p><h1>'+title+'</h1><p class="article-meta"><time datetime="'+html.escape(p.get('published',''))+'">'+html.escape(p.get('published',''))+'</time></p></header><article class="article-body">'+original_body+'</article><div class="article-end">'+source_note+'<p><a href="../../publications/">← Kembali ke arsip publikasi</a></p></div></main><footer><div class="wrap"><span>Jala Samudra Institute</span><a href="mailto:jalasamudrainstitute@gmail.com">Hubungi kami</a></div></footer></body></html>'
    target=out/'articles'/p['slug']/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(page,encoding='utf-8')
    # Verify that the migration wrapper preserves the complete legacy article body.
    generated=target.read_text(encoding='utf-8')
    rendered=re.search(r'<article class="article-body">(.*?)</article>',generated,re.S|re.I)
    if not rendered or rendered.group(1)!=original_body:
        raise ValueError('Article body parity failed for '+p['slug'])
    if '<h1>'+title+'</h1>' not in generated or '<time datetime="'+html.escape(p.get('published',''))+'">' not in generated:
        raise ValueError('Article metadata mismatch for '+p['slug'])

# Preserve explicit historical URL mapping for launch planning; do not redirect WordPress yet.
(out/'data'/'source-url-map.json').write_text(json.dumps({'mappings':source_map},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Render a usable archive in HTML before JavaScript enhances search and filters.
archive_file=out/'publications'/'index.html'
archive_html=archive_file.read_text(encoding='utf-8')
static_cards=[]
for p in sorted(records,key=lambda p:p.get('published',''),reverse=True):
    static_cards.append('<article class="story"><h3><a href="'+html.escape(p['url'],quote=True)+'">'+html.escape(p['title'])+'</a></h3><p>'+html.escape(' · '.join(p.get('domains',[])))+'</p><time datetime="'+html.escape(p.get('published',''),quote=True)+'">'+html.escape(p.get('published',''))+'</time></article>')
archive_html=archive_html.replace('<p>Memuat arsip publikasi…</p>',''.join(static_cards))
archive_file.write_text(archive_html,encoding='utf-8')

# Render homepage publication links into the initial HTML for crawlers and readers.
home_file=out/'index.html'
home_html=home_file.read_text(encoding='utf-8')
if '<p>Memuat arsip publikasi…</p>' not in home_html:
    raise ValueError('Homepage publication placeholder missing')
home_html=home_html.replace('<p>Memuat arsip publikasi…</p>',''.join(static_cards))
home_file.write_text(home_html,encoding='utf-8')

# Consistent keyboard skip navigation across the complete static preview.
for page_file in out.rglob('index.html'):
    page_html=page_file.read_text(encoding='utf-8')
    if '<main' not in page_html: continue
    main_tag=re.search(r'<main\b[^>]*>',page_html)
    main_id=re.search(r'\bid="([^"]+)"',main_tag.group(0)) if main_tag else None
    if not main_id:
        page_html=page_html.replace('<main','<main id="main-content"',1)
    skip_target='#'+(main_id.group(1) if main_id else 'main-content')
    page_html=page_html.replace('<body>','<body><a class="skip-link" href="'+skip_target+'">Langsung ke konten</a>',1)
    if 'name="description"' not in page_html:
        plain=' '.join(html.unescape(re.sub(r'<[^>]+>',' ',re.search(r'<main\b[^>]*>(.*?)</main>',page_html,re.S|re.I).group(1))).split()) if re.search(r'<main\b[^>]*>(.*?)</main>',page_html,re.S|re.I) else 'Jala Samudra Institute — independent research, analysis and ideas.'
        page_html=page_html.replace('</title>','</title><meta name="description" content="'+html.escape(plain[:155],quote=True)+'">',1)
    page_file.write_text(page_html,encoding='utf-8')

# Generate a private-preview sitemap manifest and RSS feed for prelaunch validation.
# These files are deliberately not advertised to crawlers while noindex is active.
from xml.etree import ElementTree as ET
production=os.environ.get('CF_PAGES_PROJECT_NAME')=='jalasamudrainstitute' or os.environ.get('JSI_PRODUCTION')=='1'
site_origin='https://jalasamudrainstitute.pages.dev' if production else 'https://jsi-v2-review.pages.dev'
# Add stable canonical URLs and machine-readable page metadata.
for html_file in out.rglob('index.html'):
    relative=html_file.relative_to(out)
    route='/' if str(relative)=='index.html' else '/'+relative.parent.as_posix()+'/'
    page_html=html_file.read_text(encoding='utf-8')
    canonical=site_origin+route
    # The same JSI icon is used on all pages, including article routes.
    favicon_tags=('<link rel="icon" href="/favicon.ico" sizes="any">'
                  '<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png">'
                  '<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96.png">')
    page_html=page_html.replace('</head>',favicon_tags+'</head>',1)
    page_html=page_html.replace('</head>','<link rel="canonical" href="'+html.escape(canonical,quote=True)+'"></head>',1)
    # Social preview metadata is also useful to AI link readers and sharing crawlers.
    title_match=re.search(r'<title>(.*?)</title>',page_html,re.S|re.I)
    desc_match=re.search(r'<meta name="description" content="([^"]*)"',page_html,re.I)
    if title_match:
        social_title=title_match.group(1)
        social_desc=desc_match.group(1) if desc_match else ''
        social_type='article' if route.startswith('/articles/') else 'website'
        social_tags=(
            '<meta property="og:type" content="'+social_type+'">'
            '<meta property="og:site_name" content="Jala Samudra Institute">'
            '<meta property="og:title" content="'+social_title+'">'
            '<meta property="og:description" content="'+social_desc+'">'
            '<meta property="og:url" content="'+html.escape(canonical,quote=True)+'">'
            '<meta name="twitter:card" content="summary">'
            '<meta name="twitter:title" content="'+social_title+'">'
            '<meta name="twitter:description" content="'+social_desc+'">'
        )
        page_html=page_html.replace('</head>',social_tags+'</head>',1)

    if production:
        if route=='/':
            structured={'@context':'https://schema.org','@type':'WebSite','name':'Jala Samudra Institute','url':canonical,'inLanguage':'id-ID'}
        elif route.startswith('/articles/'):
            pub=next((p for p in records if p['url']==route),None)
            if pub is None: raise ValueError('Missing article record: '+route)
            structured={'@context':'https://schema.org','@type':'Article','headline':pub['title'],'datePublished':pub['published'],'inLanguage':'id-ID','mainEntityOfPage':canonical,'url':canonical,'publisher':{'@type':'Organization','name':'Jala Samudra Institute','url':site_origin+'/'}}
        else:
            structured={'@context':'https://schema.org','@type':'WebPage','url':canonical,'inLanguage':'id-ID','isPartOf':{'@type':'WebSite','name':'Jala Samudra Institute','url':site_origin+'/'}}
        if route.startswith('/articles/'):
            structured['isAccessibleForFree']=True
            structured['description']=html.unescape(desc_match.group(1)) if desc_match else ''
            structured['author']={'@type':'Organization','name':'Jala Samudra Institute'}
            structured['isPartOf']={'@type':'WebSite','name':'Jala Samudra Institute','url':site_origin+'/'}
        page_html=page_html.replace('</head>','<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')+'</script></head>',1)
    html_file.write_text(page_html,encoding='utf-8')

if production:
    for html_file in out.rglob('index.html'):
        page_html=html_file.read_text(encoding='utf-8')
        page_html=re.sub(r'<meta name="robots" content="noindex(?:,nofollow)?">','<meta name="robots" content="index,follow">',page_html)
        html_file.write_text(page_html,encoding='utf-8')
urlset=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
for rel in ['/', '/publications/', '/research/', '/about/', '/contact/']+[p['url'] for p in records]:
    node=ET.SubElement(urlset,'url')
    ET.SubElement(node,'loc').text=site_origin+rel
ET.ElementTree(urlset).write(out/'sitemap.xml',encoding='utf-8',xml_declaration=True)
from email.utils import format_datetime
from datetime import datetime, timezone
rss=ET.Element('rss',version='2.0')
channel=ET.SubElement(rss,'channel')
for tag,value in [('title','Jala Samudra Institute — Publications'),('link',site_origin+'/publications/'),('description','Independent research, analysis and ideas.')]:
    ET.SubElement(channel,tag).text=value
for p in sorted(records,key=lambda x:x.get('published',''),reverse=True):
    item=ET.SubElement(channel,'item')
    for tag,value in [('title',p['title']),('link',site_origin+p['url']),('guid',site_origin+p['url'])]:
        ET.SubElement(item,tag).text=value
    try: ET.SubElement(item,'pubDate').text=format_datetime(datetime.fromisoformat(p['published']).replace(tzinfo=timezone.utc))
    except (ValueError,KeyError): pass
ET.ElementTree(rss).write(out/'feed.xml',encoding='utf-8',xml_declaration=True)

# Private preview only: block indexing until editorial and deployment sign-off.
(out/'robots.txt').write_text(('User-agent: *\nAllow: /\nSitemap: '+site_origin+'/sitemap.xml\n') if production else 'User-agent: *\nDisallow: /\n',encoding='utf-8')
# Provide a short, machine-readable discovery guide without replacing the actual HTML.
if production:
    llms_lines=[
        '# Jala Samudra Institute',
        '',
        '> Independent Indonesian research, analysis and ideas across capital markets, law, geopolitics and society.',
        '',
        'Website: '+site_origin+'/',
        'Publication archive: '+site_origin+'/publications/',
        'Sitemap: '+site_origin+'/sitemap.xml',
        'RSS: '+site_origin+'/feed.xml',
        '',
        '## Publications',
    ]
    for p in sorted(records,key=lambda p:p.get('published',''),reverse=True):
        llms_lines.append('- ['+p['title'].replace(']','')+']('+site_origin+p['url']+')')
    llms_lines.extend(['','## Editorial note','Read each original article for its full argument, evidence and references. This guide is not a substitute for the articles.',''])
    (out/'llms.txt').write_text('\\n'.join(llms_lines),encoding='utf-8')

print('Generated',len(records),'articles')
