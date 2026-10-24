#!/usr/bin/env python3
"""Report actual destinations of legacy TikTok video links; never substitute profile URLs."""
import re, pathlib, urllib.request, urllib.error, json
root=pathlib.Path('articles')
report=[]
for page in sorted(root.glob('*/index.html')):
    html=page.read_text(encoding='utf-8')
    for short in dict.fromkeys(re.findall(r'https?://vt\\.tiktok\\.com/[A-Za-z0-9]+/?',html)):
        request=urllib.request.Request(short,headers={'User-Agent':'Mozilla/5.0 (compatible; JSI-link-audit/1.0)'})
        try:
            with urllib.request.urlopen(request,timeout=12) as response:
                target=response.geturl()
                status=response.status
        except urllib.error.HTTPError as exc:
            target=exc.geturl();status=exc.code
        except Exception as exc:
            target='UNRESOLVED: '+type(exc).__name__;status='unknown'
        result={'article':page.parent.name,'short_url':short,'destination':target,'http_status':status,'video_id':re.search(r'/video/(\\d+)',target).group(1) if re.search(r'/video/(\\d+)',target) else None}
        report.append(result)
        print(json.dumps(result,ensure_ascii=False))
pathlib.Path('qa-tiktok-links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Audited {len(report)} TikTok short links; unresolved links require original video URL verification.')
