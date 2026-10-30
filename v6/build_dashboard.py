"""Build V6's standalone offline HTML with embedded Plotly and simulation data."""
import base64,gzip,json,hashlib
from pathlib import Path
import plotly
ROOT=Path(__file__).resolve().parent
def main():
    source=ROOT/'experiments/dashboard_data.json.gz';data=json.loads(gzip.decompress(source.read_bytes()))
    data['followups']=json.loads((ROOT/'experiments/followups.json').read_text())
    embedded=gzip.compress(json.dumps(data,separators=(',',':'),allow_nan=False).encode(),mtime=0)
    template=(ROOT/'dashboard_template.html').read_text()
    replacements={'/*__PLOTLY__*/':(Path(plotly.__file__).parent/'package_data/plotly.min.js').read_text(),
                  '/*__DATA_GZIP_BASE64__*/':json.dumps(base64.b64encode(embedded).decode()),
                  '/*__PACKAGE_IDS__*/':json.dumps([c['id'] for c in data['contexts']]+['all','followups']),
                  '/*__DOWNLOAD_ADAPTER__*/':(ROOT.parent/'publication/assets/plot-downloads.js').read_text()}
    for key,value in replacements.items():
        if key not in template:raise ValueError('missing template marker '+key)
        template=template.replace(key,value)
    for name in ['index.html','research_dashboard.html']:(ROOT/name).write_text(template)
    print(json.dumps({'run_id':data['run_id'],'bytes':len(template.encode()),'sha256':hashlib.sha256(template.encode()).hexdigest()}))
if __name__=='__main__':main()
