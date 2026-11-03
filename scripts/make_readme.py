"""Generate the version overview and complete typeset equation guides."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
versions=json.loads((ROOT/'publication/versions.json').read_text())
table='| Version | Scientific question / change | Data and specification |\n|---|---|---|\n'
for v in versions:
 folder=v['id'] if v['id']!='future' else 'proposals'
 table+='| '+v['title']+' | '+v['summary']+' | ['+folder+'/]('+folder+'/) |\n'
text=(ROOT/'publication/README_HEADER.md').read_text().replace('VERSION_TABLE_PLACEHOLDER',table)
text=text.replace('seven-tab site','eight-tab site').replace('The tabs are V1–V5, Further work and V6, in that order.','The tabs are V1–V5, Further work, V6 and V7, in that order. V7 is local and unpublished.')
text+='\n## Equations and definitions\n\nThe equations below use mathematical notation. Time and density units are hypothetical; cognitive substates do not add biological stages. Full original specifications remain in each version folder.\n'
for v in versions:
 if v['id']=='future':continue
 text+='\n## '+v['title']+' equations\n\n'+ '\n'.join((ROOT/path).read_text() for path in v['model_files'])+'\n'
 for source in v['source_specifications']:text+='\nOriginal source: ['+source+']('+source+').\n'
text+='\n## Further work\n\nSee [research proposals](proposals/RESEARCH_PROPOSALS.md). These are proposed, unexecuted investigations.\n'
(ROOT/'README.md').write_text(text)
