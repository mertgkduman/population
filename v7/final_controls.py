"""One reporting/data contract for final V7 controls; never runs physics."""
from pathlib import Path
from collections import defaultdict
from statistics import mean,stdev
from math import sqrt,isfinite
import csv,gzip,hashlib,json
ROOT=Path(__file__).resolve().parent.parent;V7=ROOT/'v7';OUT=V7/'experiments/output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(path):return json.loads((ROOT/path).read_text())
def atom(v):
    if v in ('',None,'None'):return None
    if v in ('True','False'):return v=='True'
    if v.startswith('['):
        try:return json.loads(v)
        except ValueError:return v
    try:
        x=float(v)
        if not isfinite(x):raise RuntimeError('nonfinite control value')
        return int(x) if x.is_integer() else x
    except ValueError:return v

def rows(path):
    with gzip.open(ROOT/path,'rt',newline='') as f:return [{k:atom(v) for k,v in r.items()} for r in csv.DictReader(f)]
def stats(xs):return {'mean':mean(xs),'mcse':stdev(xs)/sqrt(len(xs)) if len(xs)>1 else None,'n':len(xs)}
def source_record(path):
    p=ROOT/path;return {'path':path,'bytes':p.stat().st_size,'sha256':sha(p)}
def build():
    active=('execution_planner','resource_control','belief_control','carrier_control','information_controls','cumulative_dag','cumulative_dag_matched')
    paths=['v7/final_controls.py']
    for name in active:
        reg=f'v7/evidence/{name}/registration.json';summary=f'v7/evidence/{name}/summary.json';paths.extend([reg,summary])
        config=obj(reg)['config']
        record=obj(summary);expected_raw=record['raw_sha256']
        if isinstance(expected_raw,str):
            expected_raw={f'v7/experiments/output/{name}/confirmation.csv.gz':expected_raw}
        for rel,digest in expected_raw.items():
            if sha(ROOT/rel)!=digest:raise RuntimeError('Frozen control raw mismatch: '+rel)
            paths.append(rel)
        # DAG runtime/held-out corrections are separately archived and disclosed;
        # the original registration remains immutable, not silently rewritten.
        for rel,digest in record.get('source_sha256',config['source_sha256']).items():
            if sha(ROOT/rel)!=digest:raise RuntimeError('Frozen control source mismatch: '+rel)
            paths.append(rel)
        paths += [str(p.relative_to(ROOT)) for p in (V7/'evidence'/name).glob('*correction.json')]
        for p in (OUT/name).glob('*.gz'):paths.append(str(p.relative_to(ROOT)))
    paths+=['v7/experiments/output/recovery_causal_v3/confirmation_raw.csv.gz','v7/evidence/recovery_causal_v3/machine_verification.json']
    sources=[source_record(p) for p in sorted(set(paths))]
    signature=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest();cache=OUT/'final_controls.json'
    if cache.exists():
        data=json.loads(cache.read_text())
        if data.get('signature')==signature:return data
    execution=rows('v7/experiments/output/execution_planner/confirmation.csv.gz')
    comparisons=[]
    for regime in (1,5,9):
        base={r['seed']:r for r in execution if r['regime']==regime and r['policy']=='ordinary'}
        for policy in ('vector_0_5_0','execution_evi'):
            group=[r for r in execution if r['regime']==regime and r['policy']==policy]
            comparisons.append({'regime':regime,'policy':policy,**stats([r['mean_population']-base[r['seed']]['mean_population'] for r in group])})
    resources=rows('v7/experiments/output/resource_control/endpoints.csv.gz');pairs=rows('v7/experiments/output/resource_control/pairs.csv.gz')
    res_stats=[]
    for phase,group in [('core',[r for r in resources if r['phase']=='core']),('paired',pairs)]:
        for arm in sorted({r['arm'] for r in group}):
            rs=[r for r in group if r['arm']==arm]
            res_stats.append({'phase':phase,'arm':arm,'mean_population':stats([r['mean_population'] for r in rs]),'functional':stats([r['functional'] for r in rs])})
    pair_deltas=[]
    for seed in sorted({r['seed'] for r in pairs}):
        a=next(r for r in pairs if r['seed']==seed and r['arm']=='transmission_innovation');b=next(r for r in pairs if r['seed']==seed and r['arm']=='independent')
        pair_deltas.append(a['mean_population']-b['mean_population'])
    seasons=rows('v7/experiments/output/resource_control/seasons.csv.gz')
    for seed in sorted({r['seed'] for r in pairs}):
        groups=defaultdict(dict)
        for r in seasons:
            if r['seed']==seed and r['arm'].startswith('paired_'):groups[r['season']][r['arm']]=r
        for group in groups.values():
            a,b=group['paired_transmission_innovation'],group['paired_independent']
            assert a['offered']==b['offered']==a['realized']==b['realized']
    belief=rows('v7/experiments/output/belief_control/adults.csv.gz');training=rows('v7/experiments/output/belief_control/training.csv.gz')
    bkeys=['seed','juvenile_d','hazard','arm','environment_change','step','truth','B','L','H0','H1','action_correct','posterior_correct','credit']
    thin=[{k:r[k] for k in bkeys} for r in belief]
    matched=defaultdict(dict)
    for r in belief:matched[(r['seed'],r['hazard'],r['arm'],r['environment_change'],r['step'])][r['juvenile_d']]=r
    max_b_difference=max(abs(g[0]['B']-g[.5]['B']) for g in matched.values())
    assert max_b_difference==0
    unique_private={(r['seed'],r['episode']):r for r in training}
    carrier=rows('v7/experiments/output/carrier_control/endpoints.csv.gz')
    assert all(r['knowledge_items']==0 for r in carrier if not r['storage_enabled'])
    for r in carrier:
        r['legacy_mean_population_div60'] = r.pop('mean_population')
        r['mean_population'] = r['mean_population_post']
        for k in ('work','innovations','transmissions','private_probes','correct_cues'):
            r['pre_and_post_restart_'+k] = r.pop(k)
    z=1.96
    endpoint_precision=[]
    for r in obj('v7/evidence/belief_control/summary.json')['endpoints']:
        n=r['n'];p=r['posterior_correct']/n
        half=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
        endpoint_precision.append({**r,'wilson95_half_width':half,'target_half_width':.10,'precision_resolved':half<=.10})
    labels=defaultdict(lambda:{'opportunities':0,'conflicts':0,'trait_changes':0,'label_pairs':0,'label_changes':0})
    bucket={};last=None
    def consume(k,records):
        if not records:return
        assert len(records)==4
        group=labels[(int(k[0]),int(k[1]))];group['opportunities']+=1
        a=records[('d0','peer')];b=records[('applicable_dhalf','peer')]
        group['conflicts']+=a['conflict']=='True';group['trait_changes']+=a['chosen_action']!=b['chosen_action']
        for trait in ('d0','applicable_dhalf'):
            group['label_pairs']+=1
            group['label_changes']+=records[(trait,'peer')]['chosen_action']!=records[(trait,'authority')]['chosen_action']
    with gzip.open(ROOT/'v7/experiments/output/recovery_causal_v3/confirmation_raw.csv.gz','rt',newline='') as f:
        for row in csv.DictReader(f):
            if row['assay']!='juvenile_role_label':continue
            k=(row['seed'],row['regime'],row['opportunity_id'])
            if last is not None and last!=k:consume(last,bucket);bucket={}
            bucket[(row['trait'],row['tested_label'])]=row;last=k
        consume(last,bucket)
    label_rows=[{'seed':s,'regime':r,**v} for (s,r),v in sorted(labels.items())]
    information=rows('v7/experiments/output/information_controls/authority_provenance_raw.csv.gz')
    memory=rows('v7/experiments/output/information_controls/memory_acceptance_raw.csv.gz')
    endpoints=[r for r in memory if r['assay']=='adult_memory_reuse' and r['step']==19]
    memory_stats=[]
    for accept in (0,1):
        for d in (0,.5):
            group=[r for r in endpoints if r['memory_acceptance']==accept and r['juvenile_d']==d]
            memory_stats.append({'memory_acceptance':accept,'juvenile_d':d,
                'posterior_true':stats([r['B_after'] if r['truth'] else 1-r['B_after'] for r in group]),
                'stored_reuse':stats([int(r['stored_memory_reused']) for r in group])})
    label_contrasts=[]
    cases=[r for r in information if r['assay']!='tutor_acquisition']
    for policy in sorted({r['policy'] for r in cases}):
        diffs=[]
        for seed in sorted({r['seed'] for r in cases}):
            group=[r for r in cases if r['seed']==seed and r['policy']==policy]
            roles={role:[r for r in group if r['role_label']==role] for role in ('authority','peer')}
            diffs.append(mean(int(r['action_correct']) for r in roles['authority'])-mean(int(r['action_correct']) for r in roles['peer']))
        label_contrasts.append({'policy':policy,'unconditional_accuracy_label_effect':stats(diffs)})
    dag_rows=rows('v7/experiments/output/cumulative_dag/endpoints.csv.gz')
    with gzip.open(OUT/'cumulative_dag/full_dag_seed82901.json.gz','rt') as f:dag=json.load(f)
    r4={'information_summary':obj('v7/evidence/information_controls/summary.json'),
        'information_rows':information,'unconditional_label_contrasts':label_contrasts,'memory_endpoints':endpoints,'memory_stats':memory_stats,
        'dag_summary':obj('v7/evidence/cumulative_dag/summary.json'),'dag_rows':dag_rows,
        'heldout_rows':rows('v7/experiments/output/cumulative_dag/heldout.csv.gz'),
        'matched_summary':obj('v7/evidence/cumulative_dag_matched/summary.json'),
        'matched_rows':rows('v7/experiments/output/cumulative_dag_matched/endpoints.csv.gz'),
        'representative_paid_edges':dag['heldout']['edges'],
        'representative_receipts':[r for r in dag['receipts'] if r['receipt_id'] in {e['source_receipt_id'] for e in dag['heldout']['edges']}],
        'configs':{n:obj(f'v7/evidence/{n}/registration.json')['config'] for n in ('information_controls','cumulative_dag','cumulative_dag_matched')},
        'scope':'Separate registered mechanism controls. No ecological authority-adaptation, maturation optimum, or novelty claim. DAG gate corrections retain original archives and reused seeds; they are not independent replications.'}
    data={'schema_version':1,'signature':signature,'sources':sources,
          'execution':{'rows':execution,'contrasts':comparisons,'config':obj('v7/evidence/execution_planner/registration.json')['config']},
          'resource':{'rows':resources,'pairs':pairs,'stats':res_stats,'paired_population_delta':stats(pair_deltas),
                      'representative_seasons':[r for r in seasons if r['seed'] in (82501,82601)],'config':obj('v7/evidence/resource_control/registration.json')['config']},
          'belief':{'rows':thin,'config':obj('v7/evidence/belief_control/registration.json')['config'],'summary':obj('v7/evidence/belief_control/summary.json'),
                    'max_matched_d_B_difference':max_b_difference,'unique_training_private_correct':sum(r['private']==r['truth'] for r in unique_private.values()),'unique_training_private_n':len(unique_private),'endpoint_precision':endpoint_precision,'independent_seed_blocks':24},
          'carrier':{'field_caveats':'mean_population uses20 post-restart steps; legacy_mean_population_div60 preserves the incorrectly scaled raw field; pre_and_post_restart counters are cumulative, not post-only.','rows':carrier,'summary':obj('v7/evidence/carrier_control/summary.json'),'config':obj('v7/evidence/carrier_control/registration.json')['config']},
          'labels':{'rows':label_rows,'scope':'Real juvenile decision counterfactuals. Role-label effect is structural null for these label-neutral policies; repeated decisions cluster within72 worlds.'},
          'r4':r4,
          'scientific_status':'PARTIAL; no distinct evolutionary adaptation or irrational dogmatism established.'}
    cache.write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n');return data

def report(data):
    lines=['\n\n## Final registered controls and source audit','',
           'These additional experiments address the independent verification. They retain separate model labels and fresh seeds; they do not replace or rescore the corrected primary data. The canonical reporting route is `experiments/output/corrected_primary_registry.json` and `experiments/output/summary.json`.','',
           '### Execution-priced bounded planner','',
           'All 216 runs complete 240 seasons. The planner uses shared Q0, actual remaining work, .8/.9 query/verification accuracy, and twelve declared abstract deliberation units paid on every option. It is not full-horizon optimal RL. Counts are durable world totals, including actors that later die.','',
           '| Regime | Policy | Paired mean N difference | MCSE | Seeds |','|---|---|---:|---:|---:|']
    for r in data['execution']['contrasts']:lines.append(f"| {r['regime']} | {r['policy']} | {r['mean']:.4f} | {r['mcse']:.4f} | {r['n']} |")
    lines+=['','### Closed-resource knowledge transmission','',
            'All gains come from finite-resource harvest; teacher and pupil both spend actual tokens. Maximum person-work is 4 and maximum stock residual is below1e-10. Core 60-season outcomes include extinction as zero for the remaining horizon. These controls test ordinary reusable knowledge, with no claim of a distinct authority adaptation.','',
            '| Control | Mean population | MCSE | Seeds |','|---|---:|---:|---:|']
    for r in data['resource']['stats']:
        if r['phase']=='core':
            s=r['mean_population'];lines.append(f"| {r['arm']} | {s['mean']:.3f} | {s['mcse']:.3f} | {s['n']} |")
    p=data['resource']['paired_population_delta']
    lines += ['',f"The separate shared-work control has 24 pairs with exactly equal offered and realized effort in every saved season. Transmission minus independent mean population is {p['mean']:.3f} ± {p['mcse']:.3f} MCSE. No knowledge, people or resources cross the pair. The six discoveries need at least 48 work units, while an individual's harvest-reserved lifetime ceiling is 54: these parameters do **not** establish that culture exceeds feasible individual acquisition.",'',
              'After complete carrier removal, a separately registered experiment restarts ten truly blank agents with an explicitly recorded external 80 energy units in each arm. Storage-off retains no recipe; all 24 storage-on recoveries trace to paid artifacts. This external-restart assay is not natural growth or invasion fitness.','',
              '### Coherent belief and habit controls','',
              'The final cognitive assay fixes the proposition during each 40-episode childhood and saves actual learning histories. Adults continue with the same .8 private sensor and zero inherited override for 20 updates. Baseline, audience removal, free audit, and independent reliable evidence have actual transition/cost differences. The reliable audit has.95 accuracy, other audits.8; this is a labeled information-quality control. The presumed environmental hazard is 0 or .01 per episode, held fixed within each comparison. Psychological approval affects learned values and never enters material credits.','',
              'Across matched d=0 and d=.5 information histories, the maximum factual-posterior difference is exactly 0. Learned action values may differ. This is an algebraic consequence of information equalization, not a discovery that deference is biologically irrelevant. A static-world prior can retain old beliefs after a surprise reversal; this alone is not irrational dogmatism. The switching-prior control distinguishes that explanation from an imposed adult-rigidity trait.','',
              'The assay has 24 independent seed blocks, 3840 training rows and 15360 adult rows (768 cloned sequences), not 15360 independent organisms. The 3840 training rows replay 960 unique private tapes, with 766 correct; they are not 3840 independent trials. Static-reversal 4/24 and reliable-audit 22/24 Wilson half-widths are .146 and .118, so their original .10 precision target remains unresolved at the fixed cap. The juvenile role-label control has 211066 matched label pairs with zero label-only changes; its huge repeated-event count is not an independent-binomial sample size.','',
              '### Preserved failed or limited variants','',
              'Earlier recovery variants remain an investigation trail. Abstract skill-income toys are not resource-accounted demographic evidence; the old capacity 40 toy suppresses births; the v3 culture draft overruns its four-token limit by harvesting after exhausting discovery time; older adult state trajectories were prescribed or integrated changing truths incoherently; older role labels were confounded with d; the comparator-v2 purchase totals retain surviving actors only and use a two-unit cost model. These are not accepted substitutes for the final controls. Distinct source IDs still do not establish independent information histories: PROV-01 remains partial.','',
              '### Final information and cumulative-DAG controls','',
              'The formerly missing AUTH-02, PROV-01, AUTH-03 and ACCUM-01 designs now have actual separately registered controls. See `information_controls.md`, `cumulative_dag.md`, and `cumulative_dag_matched.md`; earlier failed attempts and gate corrections remain archived. These assays close the design omissions within their declared scope, not the wider biological claims.','',
              'Two blank tutors acquire convictions from independent private .8 tapes. A copied message shares its literal innovation root; hidden provenance is an explicit .5 mixture. Exact tutor reliability is .896. Conditional on two positive messages and equal prior, duplicate evidence gives posterior .896, independent evidence .986707, and the mixture .936693. These are exact conditional posteriors, not demographic growth or observed accuracy. Randomized uninformative role labels affect an explicitly authority-sensitive policy but not label-neutral policies; that positive control imposes sensitivity rather than demonstrating its evolution.','',
              'The memory-acceptance × immediate-override factorial has 24 independent blocks, 3840 actual childhood rows and 1920 adult reuse rows. Accepted memory and action override are separate interventions; adults have zero inherited override. Memory acceptance changes information storage and must not be interpreted as a pure deference effect.','',
              'The additional eight-module branching/merging DAG has120 core full-horizon populations plus48 originally paired arms from24 fresh seeds. A second24-pair control uses independent seeds82925–82948. Transmission+innovation+retention yields 22.833 complete-program holders (MCSE .567), while private-only, no-bootstrap transmission and no-retention yield zero. Its declared solo physical-acquisition protocol needs 64 work units, leaving at most 8 harvests: available energy 20 is below the maintenance-plus-learning requirement 21.8. This bound applies to the specified protocol, not every possible individual learner. The changed prerequisite graph gives identical endpoints and establishes no causal-sensitivity advantage.','',
              'Held-out paid source→B→C transfer succeeds in 23/24 blocks; the failed chain at seed82909 remains. Fresh matched-work pairs use seeds82925–82948: all1440 paired seasons have exactly equal offered and realized effort. Complete holders average2.083±.574 MCSE with transmission versus0 independently. This supports ordinary cultural accumulation under the stated costs, not a necessity or advantage of additional authority override. Full receipt DAGs and physical prerequisite/parameter failures are exported.','',
              'The primary limits remain: fixed maturation age, lexical tutor content, finite lineage horizon, partial provenance identification, no global-optimal-RL or ESS claim, and no demonstrated historical adaptation.']
    return '\n'.join(lines)+'\n'
if __name__=='__main__':
    d=build();print(json.dumps({'status':'verified','signature':d['signature'],'paired_population_delta':d['resource']['paired_population_delta'],'max_matched_B_difference':d['belief']['max_matched_d_B_difference']},indent=2))
