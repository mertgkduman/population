#!/usr/bin/env python3
"""Build the self-contained, corrected-evidence-only V7 dashboard and source ZIP."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,re,zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent;CORRECTED=ROOT/'experiments'/'output'/'corrected';OUTPUT=ROOT/'experiments'/'output';EVIDENCE=ROOT/'evidence';MAX_GZIP=4_000_000;MAX_HTML=8_000_000
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def read_rows(p:Path)->list[dict[str,Any]]:
    with gzip.open(p,'rt',newline='') as h:raw=list(csv.DictReader(h))
    out=[]
    for r in raw:
        q={}
        for k,v in r.items():
            if v in ('',None):q[k]=None
            elif v in ('True','False'):q[k]=v=='True'
            else:
                try:q[k]=int(v) if v.isdigit() else float(v)
                except ValueError:q[k]=v
        out.append(q)
    return out
def traits(policy:str)->tuple[float|None,float|None]:
    m=re.fullmatch(r'vector_(0|0_5|1)_(0|0_5|1)',policy)
    return ({'0':0.,'0_5':.5,'1':1.}[m.group(1)],{'0':0.,'0_5':.5,'1':1.}[m.group(2)]) if m else (None,None)
def handoff(p:Path)->tuple[dict[str,Any],dict[str,Any]]:
    if not p.is_file():raise RuntimeError('FAIL CLOSED: handoff 07 is absent; corrected evidence is not accepted')
    h=json.loads(p.read_text());inventory=h.get('corrected_inventory')
    if h.get('primary_evidence')!='corrected_overlay' or not isinstance(inventory,dict) or h.get('status')!='complete' or h.get('data_quality_status')!='passed':raise RuntimeError('FAIL CLOSED: completed corrected primary handoff required')
    if not {'discovery','holdout','depth_reliability_control','evolution','h9'}<=set(inventory):raise RuntimeError('FAIL CLOSED: corrected inventory incomplete')
    return h,json.loads((EVIDENCE/'hypothesis_ledger.json').read_text())
def checked_contract(h:dict[str,Any])->dict[str,Any]:
    """Accept only the current derived corrected registry and its enumerated inputs.

    The old frozen manifest is deliberately not consulted: it is provenance-only,
    whereas summary.json is the source-audited reporting route.
    """
    summary_path=OUTPUT/'summary.json'; registry_path=OUTPUT/'corrected_primary_registry.json'
    if not summary_path.is_file() or not registry_path.is_file():
        raise RuntimeError('FAIL CLOSED: canonical summary/registry missing')
    summary=json.loads(summary_path.read_text())
    if summary.get('kind')!='dashboard_source_contract' or summary.get('primary_evidence')!='corrected_overlay':
        raise RuntimeError('FAIL CLOSED: summary is not corrected-overlay dashboard contract')
    registry=summary.get('registry',{})
    if registry.get('path')!='v7/experiments/output/corrected_primary_registry.json' or registry.get('sha256')!=sha(registry_path):
        raise RuntimeError('FAIL CLOSED: canonical registry SHA mismatch')
    if h.get('canonical_reporting_registry')!=registry['path'] or h.get('dashboard_source_contract')!='v7/experiments/output/summary.json':
        raise RuntimeError('FAIL CLOSED: handoff does not match canonical reporting route')
    listed=summary.get('dashboard_inputs')
    if not isinstance(listed,list) or not listed:raise RuntimeError('FAIL CLOSED: dashboard input ledger absent')
    for item in listed:
        rel=item.get('path'); p=REPO/str(rel)
        if not rel or not p.is_file() or item.get('sha256')!=sha(p) or item.get('bytes')!=p.stat().st_size:
            raise RuntimeError(f'FAIL CLOSED: dashboard input hash/byte mismatch: {rel}')
    if not any(x.get('path')=='v7/experiments/output/final_controls.json' for x in listed):
        raise RuntimeError('FAIL CLOSED: accepted final controls absent from contract')
    return summary
def average(rows:list[dict[str,Any]],field:str)->float|None:
    xs=[float(r[field]) for r in rows if isinstance(r.get(field),(int,float))]
    return sum(xs)/len(xs) if xs else None
def policy_class(rows:list[dict[str,Any]])->str:
    # This is deliberately support-only: equal means/ties are kept as ties, and
    # no single net-stock outcome is relabelled as fitness.
    scores=defaultdict(list)
    for r in rows:scores[str(r['policy'])].append(float(r['mean_population']))
    if not scores:return 'UNRESOLVED'
    best=max(sum(v)/len(v) for v in scores.values());w=[k for k,v in scores.items() if abs(sum(v)/len(v)-best)<1e-12]
    return 'TIE: '+', '.join(sorted(w)) if len(w)>1 else w[0]
def data(h:dict[str,Any],ledger:dict[str,Any])->dict[str,Any]:
    summary=checked_contract(h)
    names={'discovery':'discovery.csv.gz','holdout':'holdout.csv.gz','depth_reliability_control':'depth_reliability_control.csv.gz','evolution':'corrected_evolution.csv.gz','h9':'corrected_h9.csv.gz'}
    paths={k:CORRECTED/v for k,v in names.items()}
    rows={k:read_rows(p) for k,p in paths.items()}
    for k,p in paths.items():
        if not p.is_file() or sha(p)!=h['corrected_inventory'][k]['sha256'] or len(rows[k])!=h['corrected_inventory'][k]['rows']:raise RuntimeError(f'FAIL CLOSED: corrected {k} hash/row parity failure')
    replay_path=CORRECTED/'dashboard_replays.json.gz'
    with gzip.open(replay_path,'rt') as f:replays=json.load(f)
    if len(replays.get('cells',[]))!=81 or not replays.get('parity',{}).get('all_digest_and_summary_match'):raise RuntimeError('FAIL CLOSED: 81 digest-checked passive replays required')
    persistence_path=OUTPUT/'persistence.csv.gz';persistence=read_rows(persistence_path)
    controls_path=OUTPUT/'final_controls.json'
    controls=json.loads(controls_path.read_text())
    if controls.get('signature')!=h.get('final_controls_signature') or controls.get('schema_version')!=1:
        raise RuntimeError('FAIL CLOSED: accepted final-controls signature/schema mismatch')
    discovery=rows['discovery'];policy=[]
    for r in discovery:
        dp,dl=traits(str(r.get('policy','')))
        if dp is not None:policy.append({k:r.get(k) for k in ('seed','regime','policy','mean_population','net_energy_per_agent_season','evidence_accuracy','stored_knowledge','birth_flux','death_flux')}|{'d_procedure':dp,'d_local':dl,'observed':True})
    # One L9 row per ecological regime; points retain D/cost/context/volatility
    # and show the best supported class or a literal tie based on mean N.
    regime=[]
    for number in sorted({int(r['regime']) for r in discovery}):
        group=[r for r in discovery if int(r['regime'])==number]
        probe=group[0];regime.append({'regime':number,'depth':probe['depth'],'verification_price':probe['verification_price'],'chi':probe['chi'],'q_theta':probe['q_theta'],'best_supported_class':policy_class(group),'mean_population':average(group,'mean_population'),'net_energy':average(group,'net_energy_per_agent_season'),'n_rows':len(group),'dynamics_kind':'L9 ecological screen; interactions aliased'})
    evolution=[];seen=set()
    for r in rows['evolution']:
        q={k:r.get(k) for k in ('seed','regime','directed_pair','arm','horizon','born_id','parent_id','blank_acquired_state','total_descendants','living_descendants','dead_descendants','extinct','cap_censored','no_birth_censored')};key=(r.get('regime'),r.get('directed_pair'))
        q['frequency_trajectory']=r.get('frequency_trajectory') if key not in seen else None;seen.add(key);evolution.append(q)
    replay_cells=[]
    for cell in replays['cells']:
        replay_cells.append({'regime':cell['regime'],'policy':cell['policy'],'seed':cell['seed'],'params':cell['params'],'summary':{k:cell['summary'].get(k) for k in ('replay_digest','mean_population','net_energy_per_agent_season')},'observed':cell['observed'],'series':cell['series']})
    freeze_path=EVIDENCE/'corrected'/'freeze_variant'/'manifest.json'
    sources=[{'label':'canonical dashboard contract','path':'v7/experiments/output/summary.json','sha256':sha(OUTPUT/'summary.json')},{'label':'canonical corrected registry','path':'v7/experiments/output/corrected_primary_registry.json','sha256':sha(OUTPUT/'corrected_primary_registry.json')},{'label':'corrected source/config freeze','path':str(freeze_path.relative_to(REPO)),'sha256':sha(freeze_path)}]+[{'label':k,'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in paths.items()]+[{'label':'accepted final controls','path':str(controls_path.relative_to(REPO)),'sha256':sha(controls_path),'signature':controls['signature']},{'label':'adult persistence archive (superseded in dashboard)','path':str(persistence_path.relative_to(REPO)),'sha256':sha(persistence_path)},{'label':'passive replay cache','path':str(replay_path.relative_to(REPO)),'sha256':sha(replay_path)},{'label':'corrected results handoff','path':'v7/evidence/handoffs/07-results.json','sha256':sha(EVIDENCE/'handoffs'/'07-results.json')}]
    return {'contract':{'primary_evidence':'corrected_overlay','handoff_status':'complete','fixed_tau':5,'corrected_freeze_sha256':sha(freeze_path),'scientific_verdict':h.get('scientific_verdict'),'frozen_archive':'provenance_only','replay_contract':'passive observer, no policy truth input or RNG; observed/unobserved digest parity','plotly_bundle':'plotly.js v4.1.1','canonical_summary_sha256':sha(OUTPUT/'summary.json'),'canonical_registry_sha256':sha(OUTPUT/'corrected_primary_registry.json'),'unsupported_metrics':['asymptotic invasion lambda','dogmatism','stable polymorphism']},'sources':sources,'views':{'decision_microscope':{'rows':[c['observed']['focal']|{'label':c['observed']['focal_label']} for c in replay_cells if c['observed'].get('focal')]},'policy_map':{'rows':policy},'regime_map':{'rows':regime},'life_course':{'rows':replay_cells},'genealogy':{'bounded_representative_cells':[(1,'vector_0_0'),(5,'vector_0_5_0'),(9,'vector_1_1')]},'intervention':{'rows':persistence,'h9_rows':rows['h9']},'evolution':{'rows':h.get('corrected_selection_contrasts',[]),'raw_rows':evolution},'research_ledger':{'rows':ledger.get('hypotheses',[])+h.get('checks',[])},'execution_control':controls['execution'],'resource_control':controls['resource'],'belief_control':controls['belief'],'carrier_control':controls['carrier'],'label_control':controls['labels'],'r4_control':controls['r4']}}
def paths_for_zip()->list[Path]:
    required=[REPO/'V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md',REPO/'README.md',REPO/'LICENSE',REPO/'docs'/'assets'/'plotly.min.js']
    found=[p for p in required if p.is_file()]
    # A reproducibility bundle must never include its own output; excluding ZIP
    # artifacts also makes an isolated rebuild independent of stale prior bundles.
    found += [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.zip' and p not in {EVIDENCE/'handoffs'/'08-dashboard.json',ROOT/'export_verification.json'}]
    for base in (REPO/'.planning'/'spikes',REPO/'.planning'/'quick'):
        # The official final GSD attestation hashes this ZIP. Keeping it outside
        # avoids a recursive ZIP -> attestation -> ZIP checksum. All scientific
        # verification, browser results, independent review, plans and manifests
        # remain bundled; the release attestation is delivered alongside it.
        found += [p for p in base.rglob('*') if p.is_file() and p.name!='261102-hyn-VERIFICATION.md' and ('015-' in str(p) or '016-' in str(p) or '017-' in str(p) or '018-' in str(p) or '019-' in str(p) or '261102-hyn-' in str(p))]
    return sorted(set(found),key=lambda p:str(p))
def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--handoff',type=Path,default=EVIDENCE/'handoffs'/'07-results.json');parser.add_argument('--output',type=Path,required=True);parser.add_argument('--source-zip',type=Path,required=True);args=parser.parse_args()
    hand,ledger=handoff(args.handoff);d=data(hand,ledger);packed=gzip.compress(json.dumps(d,separators=(',',':'),allow_nan=False).encode(),mtime=0)
    if len(packed)>MAX_GZIP:raise RuntimeError(f'dashboard scientific gzip {len(packed)} exceeds {MAX_GZIP}')
    bundle=REPO/'docs'/'assets'/'plotly.min.js';plotly=bundle.read_text()
    if 'plotly.js v4.1.1' not in plotly[:300]:raise RuntimeError('unexpected local Plotly bundle')
    encoded=__import__('base64').b64encode(packed).decode()
    decoder="(async()=>JSON.parse(new TextDecoder().decode(await new Response(new Blob([Uint8Array.from(atob('"+encoded+"'),c=>c.charCodeAt(0))]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer())))()"
    html=(ROOT/'dashboard_template.html').read_text().replace('/*__PLOTLY__*/',plotly).replace('/*__DATA__*/',decoder)
    if len(html.encode())>MAX_HTML:raise RuntimeError('published V7 addition exceeds 8,000,000 bytes')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(html)
    with zipfile.ZipFile(args.source_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths_for_zip():z.write(p,p.relative_to(REPO))
    print(json.dumps({'output':str(args.output),'html_bytes':len(html.encode()),'data_gzip_bytes':len(packed),'plotly_bundle':'plotly.js v4.1.1','source_zip':str(args.source_zip),'sha256':sha(args.output)}))
if __name__=='__main__':main()
