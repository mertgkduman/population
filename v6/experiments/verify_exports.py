"""Compare browser-exported numbers against full-precision simulation NPZ arrays."""
import csv,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;V6=ROOT.parent
def main():
    config=json.loads((V6/'v6-configuration.json').read_text());cid=config['context_id'];checks=[]
    with np.load(ROOT/(cid+'.npz')) as raw:
        cells=np.flatnonzero((raw['d']==config['d'])&np.isclose(raw['tau'],config['tau'],rtol=0,atol=1e-8));i=int(cells[0])
        rows=list(csv.DictReader((V6/'v6-timeseries.csv').open()))
        for key in ['N','F','A','B','D','M','private_F','belief_A','public_F']:
            sample=np.array([float(row[key+'_sample']) for row in rows]);mean=np.array([float(row[key+'_mean']) for row in rows]);sd=np.array([float(row[key+'_sd']) for row in rows])
            errors={'sample':float(np.max(abs(sample-raw[key][0,i]))),'mean':float(np.max(abs(mean-raw[key][:,i].mean(0)))),'sd':float(np.max(abs(sd-raw[key][:,i].std(0,ddof=1))))}
            checks.append({'name':key+' browser export equals full-precision raw data','pass':max(errors.values())<5e-8,'absolute_errors':errors})
        checks.append({'name':'export time axis equals raw times','pass':np.array_equal(np.array([float(row['time']) for row in rows]),raw['t'])})
    sweep=list(csv.DictReader((V6/'v6-sweep.csv').open()))
    checks.append({'name':'all sweep cells and run labels exported','pass':len(sweep)==99 and all(row['run_id']==config['run_id'] and row['label']=='simulation data' for row in sweep)})
    report={'pass':all(x['pass'] for x in checks),'checks':checks,'configuration':config,'tolerance':'5e-8 absolute; dashboard JSON rounds to 9 decimals; raw NPZ is full precision'}
    (V6/'export_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':len(checks)},indent=2))
    if not report['pass']:raise SystemExit(1)
if __name__=='__main__':main()
