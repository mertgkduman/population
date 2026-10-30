"""Merge browser verification, update provenance hashes, and package the spike."""
from __future__ import annotations
import hashlib, json, zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def write(path,data): path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def main():
    verification=json.loads((HERE/'verification.json').read_text())
    browser=json.loads((HERE/'browser_verification.json').read_text())
    verification['browser_ui']={'status':'PASS' if browser['pass'] else 'FAIL','browser':browser['browser'],'mode':browser['mode'],'checks':browser['checks'],'console_errors':browser['console_errors'],'remote_requests':browser['remote_requests']}
    verification['overall_status']='PASS' if verification['status']=='PASS' and browser['pass'] else 'FAIL'
    write(HERE/'verification.json',verification)
    manifest=json.loads((HERE/'run_manifest.json').read_text())
    manifest['finalized_utc']=datetime.now(timezone.utc).isoformat()
    manifest['workflow']={'name':'gsd-spike','mode':'--quick','installed_gsd_core':'1.14.0','interface':'Codex installed skill adapter, executed inline','commit':'unavailable: workspace has no Git repository'}
    manifest['verification_status']=verification['overall_status']
    files=[ROOT/'DEFERENCE_GSD_SPIKE_PROMPT.md',ROOT/'.planning/spikes/MANIFEST.md',ROOT/'.planning/spikes/CONVENTIONS.md']
    files += sorted(p for p in HERE.iterdir() if p.is_file() and p.name!='run_manifest.json')
    manifest['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    write(HERE/'run_manifest.json',manifest)
    archive=ROOT/'deference_gsd_spike.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[HERE/'run_manifest.json']:
            z.write(p,arcname=str(p.relative_to(ROOT)))
    print(json.dumps({'overall_status':verification['overall_status'],'scientific_checks':len(verification['checks']),'browser_checks':len(browser['checks']),'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__': main()
