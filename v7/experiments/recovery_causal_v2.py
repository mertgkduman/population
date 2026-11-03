"""R2v2 juvenile identification and separate adult intervention arms.

The recorder is a behavioral no-op wrapper around the corrected ordinary policy. It
captures only observations that the live corrected IBM already presents to agents;
the captured list never enters the random stream, ledger, state, or action path.
"""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
from typing import Any

from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import KeyedRNG, OrdinarySocialPolicy, PolicyDecision, PolicyObservation
from v7.experiments.run_experiments import _regime

SEEDS = tuple(range(83101, 83125)); REGIMES = (1, 5, 9); TAU = 5; LIKELIHOOD = .80

def _sha(value: object) -> str: return sha256(repr(value).encode()).hexdigest()
def _with(obs: PolicyObservation, **changes: Any) -> PolicyObservation: return PolicyObservation(**{**asdict(obs), **changes})

class RecordingPolicy(OrdinarySocialPolicy):
    def __init__(self, recorder: list[dict[str, Any]], d_procedure: float, d_local: float, tau: int = TAU) -> None:
        super().__init__(d_procedure, d_local, tau=tau); self.recorder = recorder
    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision:
        decision = super().decide(observation, operation_cap, keyed_rng)
        if observation.age < self.tau and observation.advice is not None:
            self.recorder.append({"age": observation.age, "observation": observation, "live_decision": decision})
        return decision

class JuvenileRecorderRun(CorrectedEcologyRun):
    """Corrected run whose policy records juvenile teacher-present decisions passively."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.juvenile_records: list[dict[str, Any]] = []
        super().__init__(*args, **kwargs)
    def _make_policy(self, traits: tuple[tuple[str, float], ...] = ()) -> RecordingPolicy:
        values = dict(traits)
        return RecordingPolicy(self.juvenile_records, values.get("d_procedure", .5), values.get("d_local", .5), tau=self.TAU)

def _decision(obs: PolicyObservation, d_procedure: float, d_local: float, key: str) -> dict[str, Any]:
    d = OrdinarySocialPolicy(d_procedure, d_local, tau=TAU).decide(obs, 128, KeyedRNG("recovery-causal-v2", key, obs.season))
    return {"chosen_action": d.chosen_action, "neutral_action": d.neutral_action, "conflict": d.conflict, "override": d.override_applied,
            "charged_cost": d.charged_cost, "operation_count": d.operation_count, "pre_override_digest": d.pre_override_digest,
            "learning_digest": d.pre_override_learning_digest, "posterior_advice": d.posterior_advice}

def juvenile_seed(job: tuple[int, int]) -> dict[str, Any]:
    seed, regime = job; values = _regime(regime - 1)
    common = dict(depth=int(values["depth"]), chi=float(values["chi"]), q_theta=float(values["q_theta"]), verification_price=float(values["verification_price"]), graph_variant=1, initial_traits={"d_procedure": .5, "d_local": .5}, burn_in=60, measurement=120, label="recovery_causal_v2")
    recorded = JuvenileRecorderRun(seed, OrdinarySocialPolicy, **common)
    recorded_result = recorded.run()
    # Paired unobserved replay proves that recording did not alter corrected-world
    # behavior or its keyed exogenous stream. This is a verification world only.
    baseline = CorrectedEcologyRun(seed, OrdinarySocialPolicy, **common).run()
    rows: list[dict[str, Any]] = []
    for index, captured in enumerate(recorded.juvenile_records):
        obs: PolicyObservation = captured["observation"]
        for label in ("neutral", "authority"):
            # Label is randomized after the actual observation; content/state never
            # changes. The d=0 policy is an ITT null control; the applicable .5
            # coordinate is procedure or local according to the real domain.
            assignment = KeyedRNG(str(seed), "r2v2-label", obs.season).draw("observation", entity=f"{index}:{label}", event_type="r2v2-label") < .5
            d_proc, d_local = ((.5, 0.) if obs.domain == "procedure" else (0., .5)) if label == "authority" else (0., 0.)
            result = _decision(obs, d_proc, d_local, f"{seed}:{regime}:{index}:{label}")
            rows.append({"assay": "juvenile_authority_itt", "seed": seed, "regime": regime, "opportunity_id": index,
                         "age": captured["age"], "domain": obs.domain, "randomized_label": label, "random_assignment_bit": assignment,
                         "label_visible_to_agent": True, "message": obs.messages, "source_history": obs.source_history,
                         "B": obs.beliefs, "K": obs.procedures, "T": obs.trust, "H": obs.habits,
                         "same_observation_for_pair": True, "private_hardware_accuracy": .8,
                         "d_procedure": d_proc, "d_local": d_local, "actual_world_replay_digest": recorded_result["replay_digest"],
                         "unobserved_replay_digest": baseline["replay_digest"], "passive_digest_parity": recorded_result["replay_digest"] == baseline["replay_digest"],
                         "actual_paid_operations": recorded.losses["operations"], "actual_paid_teaching": recorded.losses["teaching"],
                         "actual_material_resource_used": recorded.initial_total_stock-recorded.resource-sum(p.energy for p in recorded.population.values()),
                         "purchase_opportunity": result["operation_count"] > 0, "no_teacher_opportunity": False,
                         "revision_opportunity": result["conflict"], **result})
    if not rows:
        rows.append({"assay":"juvenile_no_teacher_or_no_young", "seed":seed, "regime":regime, "opportunity_id":None,
                     "actual_world_replay_digest":recorded_result["replay_digest"], "unobserved_replay_digest":baseline["replay_digest"],
                     "passive_digest_parity":recorded_result["replay_digest"] == baseline["replay_digest"], "no_teacher_opportunity":True,
                     "purchase_opportunity":False, "conflict":False, "revision_opportunity":False,
                     "scope":"world-level lack of captured juvenile teacher-present opportunity"})
    return {"rows": rows, "recorded_digest": recorded_result["replay_digest"], "baseline_digest": baseline["replay_digest"]}

def _posterior(prior: float, direction: int) -> float:
    odds=prior/max(1e-12,1-prior); ratio=LIKELIHOOD/(1-LIKELIHOOD); result=odds*(ratio if direction>0 else 1/ratio); return result/(1+result)

def adult_arm(seed: int, arm: str, direction: int) -> list[dict[str, Any]]:
    """A cloned-history arm, never a renamed row of one combined intervention."""
    if arm not in {"baseline", "audience_removal", "free_audit", "evidence"}: raise ValueError(arm)
    B,K,H,T,material=.5,.62,.70,.60,12.
    audience = arm not in {"audience_removal", "evidence"}; free_audit = arm in {"free_audit", "evidence"}
    rows=[]
    for step in range(1,21):
        prior=B; B=_posterior(B,direction); T=(4*T+(1 if direction>0 else 0))/5; K=max(0,min(1,K+.01*direction)); H=max(0,min(1,H+.015*direction)); audit_cost=0 if free_audit else .05; material-=audit_cost
        rows.append({"assay":"adult_cloned_arm", "seed":seed, "arm":arm, "evidence_direction":"supporting" if direction>0 else "contrary", "step":step,
                     "cloned_training_history":_sha((seed,.5,.62,.70,.60,12.)), "audience_present":audience, "sanctions_present":False, "rewards_present":False,
                     "free_audit":free_audit, "likelihood_strength":LIKELIHOOD, "direct_adult_inherited_override":0., "rigidity_coefficient":None,
                     "B_prior":prior,"B_factual_belief":B,"K_acquired_procedure":K,"H_learned_action_value":H,"T_source_trust":T,"material_ledger":material,
                     "audit_cost":audit_cost,"action":"act" if .25*K+.75*H>=.5 else "withhold", "revision":abs(B-prior),"revision_opportunity":True,
                     "purchase_opportunity":False,"no_teacher_opportunity":True,"conflict":False})
    return rows
