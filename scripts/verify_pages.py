#!/usr/bin/env python3
"""Verify publication assets, source-byte archives, links and build limits."""
import hashlib,json,re,zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'docs';checks=[]
def check(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ('href','src') and value:self.links.append(value)
def validate_links(text,base):
 parser=Links();parser.feed(text)
 for raw in parser.links:
  u=urlsplit(raw)
  if u.scheme or raw.startswith('#'):continue
  p=(base/unquote(u.path)).resolve()
  if not p.exists():yield str(p.relative_to(ROOT)) if ROOT in p.parents else str(p)
def main():
 missing=[]
 for p in SITE.rglob('*.html'):missing.extend(validate_links(p.read_text(),p.parent))
 portal=(SITE/'index.html').read_text();embedded=re.search(r'<script id="versions-data" type="application/json">(.*?)</script>',portal,re.S)
 versions=json.loads(embedded.group(1))
 for v in versions:
  for key in ('model','results','changes','shortcomings'):missing.extend(validate_links(v[key],SITE))
 check('all local links resolve',not missing,missing[:20])
 check('six versions plus proposals in requested order',[v['id'] for v in versions]==['v1','v2','v3','v4','v5','future','v6'])
 check('no fabricated future results','No new simulation results' in next(v for v in versions if v['id']=='future')['results'])
 check('four nested sections have content',all(all(v[k] for k in ('model','results','changes','shortcomings')) for v in versions))
 packages=0;files=0
 for manifest in (SITE/'downloads').glob('*/manifest.json'):
  for row in json.loads(manifest.read_text()):
   p=manifest.parent/row['url']
   if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise AssertionError('Package hash '+str(p))
   with zipfile.ZipFile(p) as z:
    if z.testzip():raise AssertionError('Archive CRC '+str(p))
    for item in json.loads(z.read('DATASET.json'))['files']:
     if hashlib.sha256(z.read(item['path'])).hexdigest()!=item['sha256']:raise AssertionError('Source bytes '+item['path'])
     files+=1
   packages+=1
 check('all reference archives preserve source bytes',True,{'packages':packages,'source_entries':files})
 size=sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file())
 check('Pages site below 1GB',size<1_000_000_000,size)
 check('every published file below 100MiB',all(p.stat().st_size<100*1024*1024 for p in SITE.rglob('*') if p.is_file()))
 for v in ('v1','v2','v3','v4','v5','v6'):
  text=(SITE/'apps'/(v+'.html')).read_text()
  check(v+' download adapter present','plot-downloads.js' in text and 'PUBLICATION_PACKAGES' in text)
  check(v+' shared local Plotly','../assets/plotly.min.js' in text)
 for p in SITE.glob('payload/*/*.bin'):check('payload chunk '+str(p.relative_to(SITE)),p.stat().st_size<=24*1024*1024)
 report={'pass':all(c['pass'] for c in checks),'checks':checks}
 (ROOT/'publication/verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if not report['pass']:raise SystemExit(1)
if __name__=='__main__':main()
