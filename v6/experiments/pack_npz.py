"""Losslessly repack NPZ members with stdlib LZMA; numpy.load reads them normally."""
import hashlib,json,zipfile,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def repack(p):
    start=time.time();temp=p.with_suffix('.repack');before=p.stat().st_size;expected={}
    with zipfile.ZipFile(p) as old,zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_LZMA) as new:
        for name in old.namelist():
            data=old.read(name);expected[name]=hashlib.sha256(data).hexdigest();new.writestr(name,data)
    with zipfile.ZipFile(temp) as z:
        actual={name:hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()}
    if actual!=expected:raise ValueError('lossless member verification failed '+str(p))
    after=temp.stat().st_size
    if after<before:os.replace(temp,p)
    else:temp.unlink();after=before
    return {'file':p.name,'before':before,'after':after,'member_bytes_unchanged':True,'member_sha256':expected,'seconds':time.time()-start}
def main():
    rows=[]
    for p in sorted(ROOT.glob('*.npz')):
        rows.append(repack(p));print(p.name,rows[-1]['before'],rows[-1]['after'],flush=True)
    (ROOT/'storage_verification.json').write_text(json.dumps({'method':'lossless ZIP_LZMA NPZ, readable with numpy.load; exact NPY members SHA-256 checked','files':rows,'pass':all(r['member_bytes_unchanged'] for r in rows)},indent=2)+'\n')
if __name__=='__main__':main()
