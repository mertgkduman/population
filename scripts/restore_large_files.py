#!/usr/bin/env python3
"""Restore original oversized research artifacts from version-local chunks."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def restore():
 manifest=ROOT/'publication/large_files.json'
 if not manifest.exists():print('No chunked research files in this checkout.');return
 for row in json.loads(manifest.read_text()):
  target=(ROOT/row['path']).resolve()
  if ROOT not in target.parents:raise ValueError('Unsafe output path')
  if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256']:continue
  target.parent.mkdir(parents=True,exist_ok=True);temporary=target.with_name(target.name+'.restore-tmp');h=hashlib.sha256()
  with temporary.open('wb') as out:
   for rel in row['chunks']:
    p=(ROOT/rel).resolve()
    if ROOT not in p.parents:raise ValueError('Unsafe chunk path')
    with p.open('rb') as stream:
     for b in iter(lambda:stream.read(1024*1024),b''):out.write(b);h.update(b)
  if h.hexdigest()!=row['sha256']:temporary.unlink();raise ValueError('Hash mismatch: '+row['path'])
  temporary.replace(target);print('Restored',row['path'])
if __name__=='__main__':restore()
