"""Displayed current-case quantities versus exact full-resolution raw histories."""
from pathlib import Path
import csv,json,numpy as np
ROOT=Path(__file__).resolve().parent;APP=ROOT.parent
config=json.loads((APP/'v6-configuration.json').read_text());rows=list(csv.DictReader((APP/'v6-timeseries.csv').open()));checks=[]
with np.load(ROOT/(config['context_id']+'.npz')) as raw:
 i=int(np.flatnonzero((raw['d']==config['d'])&np.isclose(raw['tau'],config['tau'],atol=1e-8,rtol=0))[0])
 for key in ['N','F','A','B','D','M','local_private','belief_A','public_F','local_advice']:
  actual=np.array([float(row[key+'_sample']) for row in rows]);expected=raw[key][0,i,::2];err=float(np.max(abs(actual-expected)));checks.append({'name':key+' displayed values match original raw observations','pass':err<5e-8,'max_abs':err})
 checks.append({'name':'display time is exact eight-unit subset','pass':np.array_equal(np.array([float(r['time']) for r in rows]),raw['t'][::2])})
checks.append({'name':'private context quality exceeds adult context quality','pass':config['parameters']['context_F']>config['parameters']['context_A']})
r={'pass':all(c['pass'] for c in checks),'checks':checks,'configuration':config,'tolerance':'5e-8 display serialization; raw NPZ keeps full precision'};(APP/'export_verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'checks':len(checks)},indent=2))
if not r['pass']:raise SystemExit(1)
