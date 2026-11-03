"""Re-run accepted DAG science into temporary files without rewriting registrations.

The historical CLI registration functions intentionally preserve their initial
source freezes; they reject the later disclosed source corrections on a second
invocation. This adapter verifies final accepted hashes and unchanged scientific
configuration, then calls the frozen runner's execution API with output paths
redirected. No policy, seed, setting, or scientific function is patched.
"""
from pathlib import Path
import argparse, hashlib, importlib, json, tempfile
ROOT=Path(__file__).resolve().parent.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replay(name):
    summary=json.loads((ROOT/f'v7/evidence/{name}/summary.json').read_text())
    registration=json.loads((ROOT/f'v7/evidence/{name}/registration.json').read_text())['config']
    for rel,digest in summary['source_sha256'].items():
        if sha(ROOT/rel)!=digest:raise RuntimeError('Accepted frozen source changed: '+rel)
    runner=importlib.import_module('v7.experiments.run_'+name)
    config=runner.configuration() if name=='cumulative_dag' else runner.config()
    if {k:v for k,v in config.items() if k!='source_sha256'}!={k:v for k,v in registration.items() if k!='source_sha256'}:
        raise RuntimeError('Scientific configuration differs from registration')
    old_output,old_evidence=runner.OUTPUT,runner.EVIDENCE
    records=[]
    try:
        with tempfile.TemporaryDirectory(prefix='v7-registered-replay-') as td:
            runner.OUTPUT=Path(td)/'raw';runner.EVIDENCE=Path(td)/'evidence'
            runner.OUTPUT.mkdir();runner.EVIDENCE.mkdir()
            if name=='cumulative_dag':runner.execute(runner.SEEDS,'confirmation')
            else:runner.run_all()
            for p in sorted(runner.OUTPUT.iterdir()):
                reference=old_output/p.name
                records.append({'file':p.name,'sha256':sha(p),'reference_sha256':sha(reference),'equal':sha(p)==sha(reference)})
    finally:runner.OUTPUT,runner.EVIDENCE=old_output,old_evidence
    result={'control':name,'pass':bool(records) and all(r['equal'] for r in records),
            'source_verified':True,'scientific_configuration_verified':True,'original_registrations_and_raw_unchanged':True,
            'runner_source_sha256':summary['source_sha256'],'files':records,'adapter_sha256':sha(Path(__file__))}
    (ROOT/f'v7/evidence/{name}/replay.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['pass']:raise RuntimeError('Replay does not match accepted raw bytes')
    return result
if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control',choices=['cumulative_dag','cumulative_dag_matched'],required=True)
    print(json.dumps(replay(p.parse_args().control),indent=2))
