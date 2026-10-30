"""Refresh standalone v1 verification and provenance hashes."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent

def write(name,data): (HERE/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def main():
    checks=json.loads((HERE/'verification.json').read_text())
    browser=json.loads((HERE/'browser_verification.json').read_text())
    checks['browser_ui']={'status':'PASS' if browser['pass'] else 'FAIL','browser':browser['browser'],'mode':browser['mode'],'checks':browser['checks'],'console_errors':browser['console_errors'],'remote_requests':browser['remote_requests']}
    checks['overall_status']='PASS' if checks['status']=='PASS' and browser['pass'] else 'FAIL'
    write('verification.json',checks)
    manifest=json.loads((HERE/'run_manifest.json').read_text())
    manifest['snapshot']='v1 baseline';manifest['finalized_utc']=datetime.now(timezone.utc).isoformat();manifest['verification_status']=checks['overall_status']
    manifest['sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file() and p.name!='run_manifest.json'}
    write('run_manifest.json',manifest)
    print(checks['overall_status'],len(checks['checks']),'scientific checks',len(browser['checks']),'browser checks')
if __name__=='__main__': main()
