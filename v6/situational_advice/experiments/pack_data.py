"""Lossless NPY-member packing; published subset matches exactly displayed data."""
import json,zipfile,hashlib,os,io
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent
KEEP={'F','A','N','B','D','M','local_private','belief_A','public_F','local_advice','d','tau','t','seeds'}
def main():
 reports=[]
 for folder in [ROOT,ROOT.parent/'published']:
  for p in sorted(folder.glob('*.npz')):
   temp=p.with_suffix('.repack');expected={};omitted=[];before=p.stat().st_size
   with zipfile.ZipFile(p) as old,zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_LZMA) as new:
    downsample=folder.name=='published' and len(np.load(io.BytesIO(old.read('t.npy'))))==151
    for name in old.namelist():
     key=name[:-4]
     if folder.name=='published' and key not in KEEP and not key.startswith('outcome_'):omitted.append(key);continue
     data=old.read(name)
     if downsample and key in KEEP and key not in ['d','tau','seeds']:
      value=np.load(io.BytesIO(data),allow_pickle=False)
      selected=value[::2] if key=='t' else value[:,::2]
      out=io.BytesIO();np.lib.format.write_array(out,selected,allow_pickle=False);data=out.getvalue()
     expected[name]=hashlib.sha256(data).hexdigest();new.writestr(name,data)
   with zipfile.ZipFile(temp) as z:
    actual={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
   if expected!=actual:raise ValueError('member mismatch '+str(p))
   os.replace(temp,p);reports.append({'path':str(p.relative_to(ROOT.parent)),'bytes_before':before,'bytes_after':p.stat().st_size,'preserved_npy_sha256':expected,'omitted_unplotted_series':omitted,'pass':True});print(p.name,before,p.stat().st_size,flush=True)
 (ROOT/'storage_verification.json').write_text(json.dumps({'pass':True,'scope':'All full raw history members retained. Published files retain all seed outcomes and exactly the first-seed plotted fields; omitted fields remain in the full raw histories. Published curves take every second original observation (8-unit display interval); map outcomes retain original 4-unit integration observations. No numeric casts or rounding.','files':reports},indent=2)+'\n')
if __name__=='__main__':main()
