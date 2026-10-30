#!/usr/bin/env python3
"""Create a clean main-branch GitHub snapshot without rewriting research history."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CHUNK=24*1024*1024;LIMIT=50*1024*1024
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'dist/github-repository');args=parser.parse_args();dest=args.output.resolve()
 if dest.exists():raise SystemExit('Output exists; choose a fresh export directory: '+str(dest))
 if dest==ROOT or ROOT not in dest.parents:raise ValueError('Export must be a fresh repository subdirectory')
 files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0');dest.mkdir(parents=True);existing=ROOT/'publication/large_files.json';large=json.loads(existing.read_text()) if existing.exists() else [];seen=set()
 for rel in sorted(set(files)-{''}):
  p=ROOT/rel
  if not p.is_file() or rel.startswith(('dist/','docs/','.git/')) or '__pycache__' in p.parts:continue
  if p.stat().st_size>LIMIT:
   sha=hashlib.sha256(p.read_bytes()).hexdigest();base=Path(rel).parts[0];base=base if base in ('v1','v2','v3','v4','v5','v6') else 'publication';folder=Path(base)/'.large-files'/sha;chunks=[]
   with p.open('rb') as f:
    n=0
    while b:=f.read(CHUNK):
     chunk=folder/('part-'+str(n).zfill(3)+'.bin');chunks.append(str(chunk))
     if str(chunk) not in seen:(dest/chunk).parent.mkdir(parents=True,exist_ok=True);(dest/chunk).write_bytes(b);seen.add(str(chunk))
     n+=1
   large.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha,'chunks':chunks})
  else:
   target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 (dest/'publication/large_files.json').write_text(json.dumps(large,indent=2)+'\n')
 ignore=dest/'.gitignore';ignore.write_text(ignore.read_text()+'\n# Reconstructed originals are generated from preserved version-local chunks.\n'+'\n'.join('/'+r['path'] for r in large)+'\n')
 for version in sorted(set(Path(r['path']).parts[0] for r in large)):
  (dest/version/'LARGE_FILES.md').write_text('# Restoring original large research artifacts\n\nAll original bytes are preserved in this version’s .large-files directory. From the repository root, run python scripts/restore_large_files.py. The manifest publication/large_files.json records original paths, sizes and SHA-256 checksums. The Pages workflow restores them automatically before building. Restored originals are ignored by Git to keep the publication snapshot pushable.\n')
 run=lambda *a:subprocess.run(a,cwd=dest,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 run('git','init','-b','main');run('git','add','.')
 # -c applies only to this snapshot commit; it does not alter the user's Git settings.
 run('git','-c','user.name=Research publication export','-c','user.email=publication@localhost','commit','-m','Publish version-isolated research snapshot')
 objects=run('git','rev-list','--objects','--all').stdout
 check=subprocess.run(['git','cat-file','--batch-check=%(objecttype) %(objectsize) %(rest)'],cwd=dest,input=objects,text=True,capture_output=True,check=True)
 oversized=[line for line in check.stdout.splitlines() if line.startswith('blob ') and int(line.split()[1])>=100*1024*1024]
 if oversized:raise RuntimeError('Oversized Git blobs: '+str(oversized))
 report={'path':str(dest),'branch':'main','chunked_originals':len(large),'max_chunk_bytes':CHUNK,'oversized_git_blobs':oversized,'research_history_rewritten':False,'remote_configured':False}
 (ROOT/'publication/github_export_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
