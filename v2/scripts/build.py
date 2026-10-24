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
    original_body=re.sub(r'(src|href)="/assets/',r'\\1="/assets/',original_body)
    page='<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>'+title+' — JSI</title><link rel="stylesheet" href="../../assets/site.css"><link rel="stylesheet" href="../../assets/article.css"></head><body><header class="masthead"><a href="../../">Jala Samudra Institute</a></header><nav class="nav"><div class="wrap"><a href="../../">Home</a><a href="../../publications/">Publications</a><a href="../../research/">Research</a><a href="../../about/">About</a><a href="../../contact/">Contact</a></div></nav><main class="reading"><h1>'+title+'</h1><p>'+html.escape(p.get('published',''))+'</p><article class="article-body">'+original_body+'</article><p><a href="../../publications/">Back to publications</a></p></main></body></html>'
    target=out/'articles'/p['slug']/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(page)
print('Generated',len(records),'articles')
