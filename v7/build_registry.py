"""Canonical derived routing index; original preregistrations stay immutable."""
from pathlib import Path
import hashlib,json
from final_controls import build,sha,source_record
ROOT=Path(__file__).resolve().parent.parent;V7=ROOT/'v7';O=V7/'experiments/output'
def main():
    control=build()
    hand=V7/'evidence/handoffs/07-results.json';h=json.loads(hand.read_text())
    assert h['primary_evidence']=='corrected_overlay' and h['status']=='complete'
    regs={name:source_record('v7/evidence/corrected/'+file) for name,file in {
        'discovery':'discovery_registration.json','holdout':'holdout_registration.json',
        'depth_control':'depth_control_registration.json','h9':'corrected_h9_registration.json',
        'finite_lineage':'corrected_evolution_registration.json'}.items()}
    for item in h['corrected_inventory'].values():assert sha(ROOT/item['path'])==item['sha256']
    inputs=[source_record(p) for p in ['v7/evidence/handoffs/07-results.json','v7/evidence/hypothesis_ledger.json',
        'v7/experiments/output/corrected/dashboard_replays.json.gz','v7/experiments/output/final_controls.json']]
    inputs += [source_record(item['path']) for item in h['corrected_inventory'].values()]
    registry={'schema_version':1,'kind':'derived_canonical_index_not_a_new_preregistration','primary_evidence':'corrected_overlay',
              'registrations':regs,'source_freeze':source_record('v7/evidence/corrected/freeze_variant/manifest.json'),
              'corrected_raw':h['corrected_inventory'],'additional_controls':control['sources'],
              'historical_registry':source_record('v7/experiments/output/run_manifest.json'),
              'historical_registry_scope':'Invalidated original frozen ecology; provenance only. Its bytes have not been rewritten.',
              'postfreeze_registry':source_record('v7/experiments/output/postfreeze_registration.json'),
              'dashboard_inputs':inputs,'completion_label_rule':'Only in derived metadata: running+seasons_completed==registered horizon means complete_horizon; raw remains unchanged.',
              'archive_classification':{
                  'original_frozen_ecology':'INVALIDATED: phantom no-teacher tutor exposed hidden z',
                  'recovery_causal_v2_adults':'Prescribed trajectories, not acquired training; not accepted as learning evidence',
                  'recovery_causal_v2_labels':'Trait contrasts; label and d confounded, not label-only ITT',
                  'recovery_causal_v3_labels':'Accepted structural label-neutral decision control; not demographic ITT',
                  'recovery_causal_v3_adults':'Actual histories but changing training truths pooled into one belief; superseded by coherent belief_control',
                  'recovery_culture_v1_v2_and_matched':'Abstract skill-income toys; no closed resource account; not demographic evidence',
                  'recovery_culture_v3':'Resource stock balanced but discovery can exhaust four tokens before additional harvest; superseded by strict resource_control',
                  'recovery_comparator_v2':'Two-unit computation assumption; actor-local counters omit dead actors; superseded by execution_planner'},
              'scientific_status':'PARTIAL; ecological provenance, global learner equivalence, age optimization and historical adaptation remain unestablished.'}
    reg=O/'corrected_primary_registry.json';reg.write_text(json.dumps(registry,indent=2)+'\n')
    routing={'schema_version':1,'kind':'dashboard_source_contract','primary_evidence':'corrected_overlay',
             'registry':source_record(str(reg.relative_to(ROOT))),'dashboard_inputs':inputs,
             'views':{'decision_microscope':'corrected passive focal decisions','policy_map':'corrected discovery rows; observed four-seed cells',
                      'regime_map':'corrected discovery; sample leader only','life_course':'corrected passive cohorts and real-event sampled genealogy',
                      'intervention':'belief_control; carrier_control separately','evolution':'corrected T=80 lineage contrasts, not exponent',
                      'research_ledger':'original check ledger plus final registered controls'},
             'obsolete_path_migration':'Legacy run_manifest remains provenance-only; this summary route and derived registry are the current reporting contract.'}
    (O/'summary.json').write_text(json.dumps(routing,indent=2)+'\n')
    print(json.dumps({'status':'verified','registry_sha256':sha(reg),'dashboard_input_count':len(inputs),'controls_signature':control['signature']},indent=2))
if __name__=='__main__':main()
