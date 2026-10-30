"""Readable summaries from saved measurements; no simulation or favorable filtering."""
import csv,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader(open(ROOT/'sweep.csv')));groups=defaultdict(list)
for row in rows:groups[(row['model'],row['scenario'])].append(row)
matched=[];optima=[]
for (model,scenario),rs in groups.items():
 ta=min(set(float(r['tau']) for r in rs),key=lambda x:abs(x-3.));pair={float(r['d']):r for r in rs if float(r['tau'])==ta};a,b=pair[0.],pair[1.]
 matched.append({'model':model,'scenario':scenario,'tau':ta,'N_d0':float(a['N']),'N_d1':float(b['N']),'relative_N_change':float(b['N'])/float(a['N'])-1,'adult_accuracy_d0':float(a['belief_A']),'adult_accuracy_d1':float(b['belief_A']),'debt_d1':float(b['accuracy_debt']),'recovery_d1':float(b['recovery']) if math.isfinite(float(b['recovery'])) else None})
 best=max(float(r['rT']) for r in rs);ties=[r for r in rs if best-float(r['rT'])<1e-10]
 optima.append({'model':model,'scenario':scenario,'rT':best,'d_active':model!='oracle','d_range':[min(float(r['d']) for r in ties),max(float(r['d']) for r in ties)],'tau_range':[min(float(r['tau']) for r in ties),max(float(r['tau']) for r in ties)],'tied_cells':len(ties),'tie_tolerance':1e-10})
mechanisms=list(csv.DictReader(open(ROOT/'mechanisms.csv')));factorial=[]
for scenario in ('stable','noisy','sparse','truth_reversal','misinformation','wrong_history','no_cost'):
 for variant in ('both','action_only','storage_only','neither','conflict_storage'):
  pp={float(r['d']):r for r in mechanisms if r['scenario']==scenario and r['variant']==variant and float(r['tau'])==3.}
  factorial.append({'scenario':scenario,'variant':variant,'tau':3.,'N_d0':float(pp[0.]['N']),'N_d1':float(pp[1.]['N']),'delta_rT':float(pp[1.]['rT'])-float(pp[0.]['rT']),'delta_adult_accuracy':float(pp[1.]['belief_A'])-float(pp[0.]['belief_A']),'delta_public_accuracy':float(pp[1.]['public_F'])-float(pp[0.]['public_F'])})
result={'matched':matched,'optima_with_ties':optima,'mechanism_factorial':factorial,'refined_abundance':json.load(open(ROOT/'refinement.json')),'refined_selection':json.load(open(ROOT/'selection_refinement.json')),'scope':'Hypothetical simulation measurements. Monomorphic finite-horizon abundance differs from conditional rare-mutant selection. A tied or inactive d dimension has no unique optimum.'}
(ROOT/'findings.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'matched_examples':[r for r in matched if r['model']=='retained' and r['scenario'] in ['stable','noisy','sparse','load']],'action_storage':[r for r in factorial if r['scenario']=='noisy']},indent=2))
