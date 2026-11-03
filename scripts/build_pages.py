#!/usr/bin/env python3
"""Build a version-isolated static Pages site without rerunning models."""
import argparse,base64,csv,gzip,hashlib,html,io,json,re,shutil,sys,zipfile
from payload_codec import pack,unpack,JS_UNPACK
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'publication/vendor'))
import markdown
CHUNK=24*1024*1024
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def md(text):
 maths=[]
 def keep(match):
  maths.append(match.group(0))
  return 'MATHPLACEHOLDER'+str(len(maths)-1)+'TOKEN'
 text=re.sub(r'\$\$[\s\S]*?\$\$|\$(?!\$)[^\n$]+?\$',keep,text)
 rendered=markdown.markdown(text,extensions=['markdown.extensions.tables','markdown.extensions.fenced_code','markdown.extensions.sane_lists'])
 for i,formula in enumerate(maths):
  rendered=rendered.replace('MATHPLACEHOLDER'+str(i)+'TOKEN','<span class="math-source">'+html.escape(formula)+'</span>')
 return rendered
def source_document(path):
 content=md((ROOT/path).read_text())
 def link(match):
  raw=html.unescape(match.group(1))
  if raw.startswith(('https:','http:','mailto:','#')):return match.group(0)
  resolved=((ROOT/path).parent/raw.split('#')[0]).resolve()
  try:rel=resolved.relative_to(ROOT)
  except ValueError:return 'href="#"'
  version=rel.parts[0] if rel.parts and rel.parts[0] in ('v1','v2','v3','v4','v5','v6','v7') else 'future'
  if resolved.suffix=='.html' and version!='future':target='apps/'+version+'.html'
  elif resolved.suffix=='.md' and resolved.exists():target='specifications/'+str(rel)
  elif resolved.suffix in ('.py','.js') and resolved.exists():target='sources/'+str(rel)
  else:target='downloads/'+version+'/index.html' if version!='future' else 'index.html#future/model'
  return 'href="'+target+'"'
 content=re.sub(r'href="([^"]*)"',link,content)
 return '<article>'+content+'</article><p class="document-source">Preserved source: '+html.escape(path)+'</p>'
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def raw_packages(version,out):
 folder=ROOT/version;data=folder/'experiments' if (folder/'experiments').exists() else folder;dest=out/'downloads'/version;dest.mkdir(parents=True,exist_ok=True)
 if version=='v7':
  corrected=data/'output'/'corrected'
  files=[corrected/name for name in ('discovery.csv.gz','holdout.csv.gz','depth_reliability_control.csv.gz','corrected_evolution.csv.gz','corrected_h9.csv.gz','dashboard_replays.json.gz')]+[folder/'experiments/output/final_controls.json',folder/'final_controls.md',folder/'evidence/execution_planner/registration.json',folder/'evidence/resource_control/registration.json',folder/'evidence/belief_control/registration.json',folder/'evidence/carrier_control/registration.json',folder/'parameter_schema.json',folder/'mathematical_model.md',folder/'results.md',folder/'research_contract.md',folder/'dashboard_replays.py',folder/'experiments/corrected_model.py',folder/'evidence/handoffs/07-results.json',folder/'evidence/hypothesis_ledger.json']
  for control in ('information_controls','cumulative_dag','cumulative_dag_matched'):
   files += [folder/'evidence'/control/'registration.json',folder/'evidence'/control/'summary.json']
   files += sorted((folder/'experiments/output'/control).glob('*.csv.gz'))
  files += [folder/'experiments/output/cumulative_dag/full_dag_seed82901.json.gz',folder/'experiments/output/cumulative_dag/full_dag_seed82902.json.gz']
  if any(not p.is_file() for p in files):raise RuntimeError('V7 corrected package input missing')
  expected=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'bytes':p.stat().st_size} for p in files]
  target=dest/'corrected-simulation-data.zip'
  with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
   for p in files:z.write(p,str(p.relative_to(ROOT)))
   z.writestr('DATASET.json',json.dumps({'version':'v7','dataset':'corrected-simulation-data','label':'simulation data','files':expected,'scope':'Corrected primary exports and dashboard observational replay; invalidated frozen raw histories and complete archives are in the local complete project package.'},indent=2))
  records=[{'id':'corrected-simulation-data','url':target.name,'bytes':target.stat().st_size,'sha256':digest(target)}]
  write(dest/'manifest.json',json.dumps(records,indent=2))
  write(dest/'index.html','<!doctype html><html lang="en"><meta charset="utf-8"><title>V7 simulation data</title><link rel="stylesheet" href="../../assets/site.css"><main><h1>V7 corrected simulation data</h1><p>Corrected primary exports, replay cache, accepted lightweight final controls (execution, resource, belief, carrier, information and cumulative-DAG endpoints/trajectories), registrations, model and hashes. Full audit histories and invalidated provenance remain in the local project package; the giant historical juvenile raw is intentionally not published here.</p><a download href="corrected-simulation-data.zip">Download corrected simulation data</a> · <a href="manifest.json">Package hashes</a></main></html>')
  return records
 raw=[p for p in data.iterdir() if p.is_file() and p.suffix in ('.csv','.json','.npz') and p.name!='project_manifest.json']
 groups={'all':[p for p in raw if p.suffix!='.npz']}
 if version in ('v4','v5','v6'):
  for p in raw:
   if p.suffix=='.npz':groups[p.stem]=[p]
  families={'followups':['followups','heldout'],'fixed_equilibria':['fixed_equilibria'],'volatility':['volatility'],'mechanisms':['mechanism'],'source_conditions':['source_conditions'],'histories':['histor'],'evolution':['architecture','pairwise','competition','dynamic','selection','reproductive','replacement','frozen_replacement'],'frozen_replacement':['frozen_replacement'],'repertoire':['repertoire.'],'repertoire_tutors':['repertoire_tutors'],'bayes_benchmark':['bayes_benchmark']}
  for key,prefixes in families.items():
   match=[p for p in raw if any(p.name.startswith(x) for x in prefixes)]
   if match:groups[key]=match
 else:groups={'all':raw}
 metadata=[p for p in [folder/'schema.json',folder/'parameter_schema.json',folder/'run_manifest.json',data/'run_manifest.json',data/'model.py',folder/'model.py'] if p.exists()]
 rows=None
 if version in ('v4','v5','v6'):
  with (data/'sweep.csv').open() as f:rows=list(csv.DictReader(f))
 records=[]
 for key,items in groups.items():
  target=dest/(key+'.zip');files=list(dict.fromkeys(items+metadata));expected=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'bytes':p.stat().st_size} for p in files]
  signature=hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest();side=target.with_suffix('.signature')
  if not target.exists() or not side.exists() or side.read_text()!=signature:
   with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
    for p in files:z.write(p,str(p.relative_to(ROOT)))
    if rows and any(p.suffix=='.npz' for p in items):
     subset=[r for r in rows if r.get('model','')+'_'+r.get('scenario','')==key]
     if subset:
      f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(subset[0]));w.writeheader();w.writerows(subset);z.writestr('selected-context-sweep.csv',f.getvalue())
    z.writestr('DATASET.json',json.dumps({'version':version,'dataset':key,'label':'simulation data','files':expected,'scope':'Reference tables/configuration; NPZ packages retain saved grids and time series. Separate displayed-plot ZIPs record exact current traces.'},indent=2))
    z.writestr('README.txt','Reference simulation data. Source paths/hashes are in DATASET.json. all.zip contains reference tables/configuration; full NPZ trajectories are separate catalogue entries. Use complete version source to reproduce.\n')
   side.write_text(signature)
  if target.stat().st_size>=100*1024*1024:raise RuntimeError('Oversize dataset: '+str(target))
  records.append({'id':key,'url':key+'.zip','bytes':target.stat().st_size,'sha256':digest(target)})
 write(dest/'manifest.json',json.dumps(records,indent=2))
 listing=''.join('<li><a download href="'+r['url']+'">'+r['id']+'</a> · '+str(round(r['bytes']/1e6,2))+' MB</li>' for r in records)
 write(dest/'index.html','<!doctype html><html lang="en"><meta charset="utf-8"><title>'+version+' raw data</title><link rel="stylesheet" href="../../assets/site.css"><main><h1>'+version.upper()+' simulation data</h1><p>Reference tables and full trajectory archives are separate. Packages contain source-byte hashes; exact displayed-plot ZIPs are available beneath interactive figures.</p><ul>'+listing+'</ul><a href="manifest.json">Package hashes</a></main></html>')
 return records
def local_packages(out):
 folder=ROOT/'v6/situational_advice';dest=out/'downloads/v6';records=[]
 metadata=[folder/'parameter_schema.json',folder/'experiments/run_manifest.json',folder/'experiments/model.py',folder/'mathematical_model.md']
 groups={p.stem:[p] for p in (folder/'published').glob('*.npz')}
 groups['local_all']=[folder/'experiments/sweep.csv',folder/'experiments/followups.json',folder/'research_contract.md',folder/'results.md']
 for key,items in groups.items():
  files=items+metadata;expected=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'bytes':p.stat().st_size} for p in files]
  signature=hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest();target=dest/(key+'.zip');side=target.with_suffix('.signature')
  if not target.exists() or not side.exists() or side.read_text()!=signature:
   with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
    for p in files:z.write(p,str(p.relative_to(ROOT)))
    z.writestr('DATASET.json',json.dumps({'version':'v6','dataset':key,'label':'simulation data','files':expected,'scope':'All-seed map outcomes and exact seed71001 plot trajectories. Full unused per-seed histories remain in the GitHub repository; no displayed data are omitted.'},indent=2))
    z.writestr('README.txt','Simulation data. Each context NPZ includes all-seed outcomes and the seed71001 histories displayed in the explorer. Full per-seed histories: https://github.com/mertgkduman/population/tree/main/v6/situational_advice/experiments\n')
   side.write_text(signature)
  records.append({'id':key,'url':key+'.zip','bytes':target.stat().st_size,'sha256':digest(target)})
 old=json.loads((dest/'manifest.json').read_text());write(dest/'manifest.json',json.dumps(old+records,indent=2))
 index=(dest/'index.html').read_text();extra='<h2>V6 situational-advice extension</h2><ul>'+''.join('<li><a download href="'+r['url']+'">'+r['id']+'</a></li>' for r in records)+'</ul>'
 write(dest/'index.html',index.replace('</main>',extra+'</main>'))
 return records

def dashboard(version,out,bundle,records,source_override=None,asset_key=None):
 asset_key=asset_key or version
 source=source_override or ROOT/version/('research_dashboard.html' if version in ('v4','v5','v6','v7') else 'index.html');page=source.read_text()
 page=re.sub(r'<!-- STANDALONE_DOWNLOADS_START -->.*?<!-- STANDALONE_DOWNLOADS_END -->','',page,flags=re.S)
 if bundle not in page:raise RuntimeError('Exact Plotly bundle missing: '+version)
 page=page.replace(bundle,'').replace('</head>','<link rel="icon" href="data:,"><script src="../assets/plotly.min.js"></script></head>',1)
 if version in ('v4','v5','v6'):
  match=re.search(r'const EMBEDDED_GZIP_BASE64=("[A-Za-z0-9+/=]+");',page)
  if not match:raise RuntimeError('Dataset marker absent: '+version)
  data=base64.b64decode(json.loads(match.group(1)));chunks=[]
  if version=='v6':
   original=json.loads(gzip.decompress(data));encoded,packing=pack(original)
   if unpack(encoded)!=original:raise ValueError('Payload round-trip mismatch')
   before=len(data);data=gzip.compress(json.dumps(encoded,separators=(',',':'),allow_nan=False).encode(),mtime=0)
   write(ROOT/'publication'/('packing-'+asset_key+'.json'),json.dumps({'pass':True,'before_gzip_bytes':before,'after_gzip_bytes':len(data),**packing},indent=2))
  shutil.rmtree(out/'payload'/asset_key,ignore_errors=True)
  for n,start in enumerate(range(0,len(data),CHUNK)):
   rel='payload/'+asset_key+'/part-'+str(n).zfill(3)+'.bin';p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data[start:start+CHUNK]);chunks.append('../'+rel+'?v='+hashlib.sha256(data[start:start+CHUNK]).hexdigest()[:12])
  page=page[:match.start()]+'const EMBEDDED_GZIP_BASE64=null;'+page[match.end():]
  rx=r'async function embeddedData\(\)\s*\{.*?return JSON\.parse\(await new Response\(stream\)\.text\(\)\)\s*;?\s*\}'
  replacement="async function embeddedData(){const parts=[];for(const path of "+json.dumps(chunks)+"){const r=await fetch(path);if(!r.ok)throw Error('Cannot load dataset: '+path);parts.push(await r.arrayBuffer())}const stream=new Blob(parts).stream().pipeThrough(new DecompressionStream('gzip'));return unpackPayload(JSON.parse(await new Response(stream).text()))}"+JS_UNPACK
  page,count=re.subn(rx,lambda _:replacement,page,count=1,flags=re.S)
  if count!=1:raise RuntimeError('Dataset loader substitution failed: '+version)
 page=re.sub(r' data-publication-version="[^"]*"','',page,count=1)
 page=page.replace('<html','<html data-publication-version="'+version+'"',1)
 adapter='<style>.publication-download{display:flex;gap:10px;flex-wrap:wrap;padding:9px 4px;font:13px/1.5 system-ui}.publication-download a{color:#85e4dd;text-decoration:underline}.publication-download button{font:inherit;padding:5px 9px}</style><script>window.PUBLICATION_PACKAGES='+json.dumps([r['id'] for r in records])+';'+('window.PUBLICATION_REFERENCE_OVERRIDE=()=>"corrected-simulation-data";' if version=='v7' else '')+'</script><script src="../assets/plot-downloads.js"></script>'
 write(out/'apps'/(asset_key+'.html'),page.replace('</body>',adapter+'</body>'))
 return {'source_sha256':digest(source),'hosted_bytes':len(page.encode())}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'docs');args=parser.parse_args();out=args.output.resolve()
 if out==ROOT or ROOT not in out.parents:raise ValueError('Output must be inside repository')
 out.mkdir(parents=True,exist_ok=True);(out/'.nojekyll').touch();(out/'assets').mkdir(exist_ok=True)
 for p in (ROOT/'publication/assets').iterdir():
  shutil.copytree(p,out/'assets'/p.name,dirs_exist_ok=True) if p.is_dir() else shutil.copy2(p,out/'assets'/p.name)
 import plotly
 bundle=(Path(plotly.__file__).parent/'package_data/plotly.min.js').read_text();write(out/'assets/plotly.min.js',bundle)
 for folder in ('v1','v2','v3','v4','v5','v6','v7','proposals'):
  for source in (ROOT/folder).rglob('*'):
   if source==ROOT/'v7/evidence/ecology_adversarial_review.md':continue
   if source.is_file() and '__pycache__' not in source.parts and source.suffix in ('.md','.py','.js'):
    target=out/('specifications' if source.suffix=='.md' else 'sources')/source.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 versions=json.loads((ROOT/'publication/versions.json').read_text());rendered=[];built=[]
 for v in versions:
  v=dict(v);v['model']=''.join(source_document(p) for p in v['model_files'])
  if v.get('parameter_file'):v['model']+='<details><summary>Saved parameters, units and scenarios</summary><pre>'+html.escape((ROOT/v['parameter_file']).read_text())+'</pre></details>'
  if v.get('source_specifications'):
   v['model']+='<details><summary>Original specifications and complete implementation notes</summary><ul>'+''.join('<li><a href="specifications/'+p+'">'+p+'</a></li>' for p in v['source_specifications'])+'</ul></details>'
  v['results']=''.join(source_document(p) for p in v['results_files']);v['changes']=md(v['changes']);v['shortcomings']=md(v['shortcomings'])
  if v['id']!='future':
   records=raw_packages(v['id'],out)
   if v['id']=='v6':records+=local_packages(out)
   built.append({'version':v['id'],'packages':len(records),**dashboard(v['id'],out,bundle,records)});v['app']='apps/'+v['id']+'.html?v='+digest(out/'apps'/(v['id']+'.html'))[:12]
   if v['id']=='v6':
    built.append({'version':'v6-situational',**dashboard('v6',out,bundle,records,ROOT/'v6/situational_advice/research_dashboard.html','v6-situational')})
    v['extra_app']='apps/v6-situational.html?v='+digest(out/'apps/v6-situational.html')[:12]
  else:v['results']='<h2>No new simulation results</h2><p>These investigations are proposals. Existing measurements and datasets remain in their numbered version folders.</p>'
  rendered.append(v);print('Built',v['id'],flush=True)
 page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Deference & cultural learning · versioned research</title><link rel="icon" href="data:,"><link rel="stylesheet" href="assets/site.css"><link rel="stylesheet" href="assets/katex/katex.min.css"><script defer src="assets/katex/katex.min.js"></script><script defer src="assets/katex/contrib/auto-render.min.js"></script></head><body><a class="skip" href="#panel">Skip to content</a><header><div class="eyebrow">Computational research archive · simulation data</div><h1>Deference, conviction & cultural learning</h1><p>Seven successive models, their equations, interactive results and open questions. Technical verification does not establish a historical adaptation.</p></header><nav id="version-tabs" role="tablist" aria-label="Versions"></nav><main><section class="intro"><h2 id="version-heading"></h2><p id="summary"></p></section><nav id="section-tabs" class="subtabs" role="tablist" aria-label="Version sections"></nav><section id="panel" class="content" role="tabpanel"></section></main><footer>Original scientific artifacts remain isolated by version. Simulation methods and results remain version-specific; proposals contain no new results.</footer><script id="versions-data" type="application/json">'+json.dumps(rendered).replace('</','<\\/')+'</script><script src="assets/site.js"></script></body></html>'
 page=page.replace('Seven successive models','Seven successive models').replace('assets/site.js','assets/site.js?v='+digest(out/'assets/site.js')[:12]).replace('assets/site.css','assets/site.css?v='+digest(out/'assets/site.css')[:12])
 write(out/'index.html',page)
 size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
 if size>=1_000_000_000:raise RuntimeError('Pages build exceeds 1GB: '+str(size))
 report={'bytes':size,'versions':built,'tabs':[v['title'] for v in rendered],'science_unchanged':True,'largest_file_bytes':max(p.stat().st_size for p in out.rglob('*') if p.is_file())}
 write(ROOT/'publication/build_report.json',json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
