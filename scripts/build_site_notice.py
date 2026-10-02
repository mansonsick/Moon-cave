"""Build the static site notice and shared access labels from locally rendered PNGs.

Render first with render_story_text.py --story legal --source legal/content.json.
No password or font is copied by this builder.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/'legal/assets/text/text.json').read_text(encoding='utf-8'))

def label(key):
    entry = manifest['labels'][key]
    return '<span class="bpmf" role="img" aria-label="'+html.escape(entry['text'], quote=True)+'">'+''.join(
        '<img src="./assets/text/'+part['src']+'" alt="" width="'+str(part['width'])+'" height="'+str(part['height'])+'">'
        for part in entry['parts'])+'</span>'

def p(key): return '<p>'+label(key)+'</p>'
def h(key): return '<h2>'+label(key)+'</h2>'
def link(key,url): return '<a href="'+html.escape(url,quote=True)+'">'+label(key)+'</a>'

body = h('purpose-heading')+p('purpose')+'<p class="english">Personal learning / vibe coding experiment · Non-commercial</p>'+p('ai')
body += h('rights-heading')+p('rights')+link('rights-source','https://www.tipo.gov.tw/tw/copyright/767-4893.html')+p('music')
body += '''<p class="english credit">“Come Play with Me” — Kevin MacLeod (<a href="https://incompetech.com/music/royalty-free/index.html?Search=Search&amp;isrc=USUAN1400042">incompetech.com</a>).<br>
Licensed under <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0</a>.<br>
User-supplied Chosic MP3 copied unchanged; playback volume and temporary voice ducking only.</p>'''
body += p('letters')+link('letters-link','../stories/story-05/assets/audio/letters/review.html')+p('art')
body += h('privacy-heading')+p('privacy')+p('camera')+p('hosting')
body += h('access-heading')+p('access')+link('access-source','https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages')
body += h('safety-heading')+p('safety')+h('contact-heading')+p('contact')+link('contact-link','https://github.com/mansonsick/Moon-cave/issues/new')
body += '<footer>'+p('updated')+link('home','../')+'</footer>'
page = '''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=yes"><meta name="robots" content="noindex"><title>網站使用與素材說明</title>
<style>:root{font:23px/1.8 system-ui,sans-serif;color:#30283e;background:#f5eddc}*{box-sizing:border-box}body{margin:0}main{max-width:940px;margin:auto;padding:30px clamp(18px,4vw,44px) 48px}h1{font-size:30px}h2{font-size:25px;margin-top:32px}p{margin:16px 0}.bpmf{display:inline-flex;flex-wrap:wrap;gap:2px 4px;max-width:100%;align-items:center}.bpmf img{width:auto;height:1.12em;max-width:100%;object-fit:contain}a{color:#245a78;display:inline-block;min-height:44px;padding:6px 0;text-underline-offset:5px}a:focus-visible{outline:3px solid #245a78;outline-offset:4px}.english{font-size:18px;overflow-wrap:anywhere}.credit{padding:16px;background:#fffaf0;border-radius:14px}footer{border-top:1px solid #cbbfa5;margin-top:36px;padding-top:14px}@media(max-width:480px){:root{font-size:21px}h1{font-size:26px}h2{font-size:23px}}</style></head>
<body><main><nav>'''+link('home','../')+'</nav><h1>'+label('title')+'</h1>'+body+'</main></body></html>\n'
(ROOT/'legal/index.html').write_text(page,encoding='utf-8')
print('Built site notice with licensed music credit and shared Zhuyin labels; no font published.')
