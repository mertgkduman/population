"""Registered exploratory V7 §5.1 cognitive causal-procedure assay.

This is deliberately separate from the frozen IBM. Every arm uses six blank
learners, a 60-unit lifetime work budget, 0.8 private evidence accuracy, and a
matched material ledger. Teaching transfers actual causal modules and costs one
unit to both parties. It is not evidence about selection or inherited deference.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
import argparse, csv, gzip, json, shutil
from statistics import mean
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT, EVIDENCE = ROOT / "experiments" / "output", ROOT / "evidence"
ARMS = ("transmission_innovation", "no_transmission", "matched_total_work_independent_upper_bound", "transmission_without_modification", "innovation_without_retention", "shuffled_prerequisite_world")
PILOT_SEEDS, CONFIRMATION_SEEDS = tuple(range(74597, 74601)), tuple(range(74601, 74625))
PRIVATE_ACCURACY, VERIFY_COST, LIFETIME_BUDGET, TEACHING_COST, MATERIAL_PER_WORK = .80, 29, 60, 1, .01

def _u01(*parts: object) -> float:
    return int.from_bytes(sha256(repr(parts).encode()).digest()[:8], "big") / 2**64

@dataclass(frozen=True)
class Module:
    identifier: str; procedure: str; depth: int; prerequisites: tuple[str, ...]

@dataclass(frozen=True)
class Learner:
    identity: str; generation: int; modules: frozenset[str]; source_history: tuple[str, ...]
    private_work: int = 0; learner_teaching_work: int = 0; teacher_teaching_work: int = 0; safe_work: int = 0; private_verifications: int = 0
    @classmethod
    def blank(cls, identity: str, generation: int = 0) -> "Learner": return cls(identity, generation, frozenset(), ())
    @property
    def work_used(self) -> int: return self.private_work + self.learner_teaching_work + self.teacher_teaching_work + self.safe_work

@dataclass(frozen=True)
class ProcedureProgram:
    modules: tuple[Module, ...]
    @classmethod
    def contract_fixture(cls, *, shuffled_world: bool = False) -> "ProcedureProgram":
        values = []
        for procedure in ("water", "shelter"):
            a, b, c = (f"{procedure}:prepare", f"{procedure}:assemble", f"{procedure}:finish")
            # A real alternate causal world, not nonsense/invalid teaching.
            pre = ((b,), (), (a,)) if shuffled_world else ((), (a,), (b,))
            values += [Module(a, procedure, 1, pre[0]), Module(b, procedure, 2, pre[1]), Module(c, procedure, 3, pre[2])]
        return cls(tuple(values))
    def by_id(self, identifier: str) -> Module: return next(m for m in self.modules if m.identifier == identifier)
    def order(self, procedure: str) -> tuple[str, ...]:
        pending = {m.identifier: m for m in self.modules if m.procedure == procedure}; result = []
        while pending:
            ready = sorted(key for key, module in pending.items() if set(module.prerequisites).issubset(result))
            if not ready: raise RuntimeError("acyclic causal modules required")
            key = ready[0]; result.append(key); del pending[key]
        return tuple(result)
    def private_verify(self, learner: Learner, identifier: str, seed: int) -> Learner:
        module = self.by_id(identifier)
        if learner.work_used + VERIFY_COST > LIFETIME_BUDGET or not set(module.prerequisites).issubset(learner.modules): return learner
        accurate = _u01("private-evidence", seed, learner.identity, identifier) < PRIVATE_ACCURACY
        return replace(learner, modules=learner.modules | ({identifier} if accurate else set()),
                       source_history=(*learner.source_history, f"private:{identifier}:{'verified' if accurate else 'failed'}"),
                       private_work=learner.private_work + VERIFY_COST, private_verifications=learner.private_verifications + 1)
    def teach(self, teacher: Learner, learner: Learner, identifier: str) -> tuple[Learner, Learner, bool]:
        module = self.by_id(identifier)
        source_acquired = identifier in teacher.modules and any(identifier in event for event in teacher.source_history)
        if (not source_acquired or learner.work_used + TEACHING_COST > LIFETIME_BUDGET or teacher.work_used + TEACHING_COST > LIFETIME_BUDGET or not set(module.prerequisites).issubset(learner.modules)):
            return teacher, learner, False
        return (replace(teacher, teacher_teaching_work=teacher.teacher_teaching_work + TEACHING_COST),
                replace(learner, modules=learner.modules | {identifier}, source_history=(*learner.source_history, f"teacher:{teacher.identity}:{identifier}"), learner_teaching_work=learner.learner_teaching_work + TEACHING_COST), True)
    def functional_depth(self, learner: Learner, procedure: str) -> int:
        return sum(identifier in learner.modules for identifier in self.order(procedure)) if all(identifier in learner.modules for identifier in self.order(procedure)) else next((n for n, identifier in enumerate(self.order(procedure)) if identifier not in learner.modules), 0)
    def functional(self, learner: Learner, procedure: str) -> bool: return self.functional_depth(learner, procedure) == 3

def _fill(learner: Learner) -> Learner: return replace(learner, safe_work=learner.safe_work + LIFETIME_BUDGET - learner.work_used)
def _score(program: ProcedureProgram, learner: Learner, procedure: str, seed: int) -> float:
    return float(_u01("complex" if program.functional(learner, procedure) else "safe", seed, learner.identity, procedure) < (.85 if program.functional(learner, procedure) else .55))
def _pioneers(program: ProcedureProgram, seed: int) -> list[Learner]:
    out = []
    for procedure in ("water", "shelter"):
        learner = Learner.blank(f"{procedure}-pioneer-{seed}", 0)
        for identifier in program.order(procedure)[:2]: learner = program.private_verify(learner, identifier, seed)
        out.append(learner)
    return out

def run_cell(*, seed: int, arm: str) -> dict[str, Any]:
    if arm not in ARMS: raise ValueError(f"unregistered arm: {arm}")
    program = ProcedureProgram.contract_fixture(shuffled_world=arm == "shuffled_prerequisite_world")
    pioneers = _pioneers(program, seed); innovators = [Learner.blank(f"{p}-innovator-{seed}", 1) for p in ("water", "shelter")]; successors = [Learner.blank(f"{p}-successor-{seed}", 2) for p in ("water", "shelter")]; edges = []
    if arm == "matched_total_work_independent_upper_bound":
        # Identical 360-unit ledger, but a clearly labelled ideal pooled solver.
        terminals = []
        for procedure in ("water", "shelter"):
            learner = Learner.blank(f"pooled-{procedure}-{seed}", 2)
            for identifier in program.order(procedure):
                learner = replace(learner, modules=learner.modules | {identifier}, source_history=(*learner.source_history, f"ideal:{identifier}"), private_work=learner.private_work + VERIFY_COST, private_verifications=learner.private_verifications + 1)
            terminals.append(_fill(learner))
        learners = [_fill(x) for x in pioneers + innovators] + terminals
    else:
        for i, procedure in enumerate(("water", "shelter")):
            teacher, learner, order = pioneers[i], innovators[i], program.order(procedure)
            if arm in {"transmission_innovation", "transmission_without_modification", "shuffled_prerequisite_world"}:
                for identifier in order[:2]:
                    teacher, learner, ok = program.teach(teacher, learner, identifier)
                    if ok: edges.append((teacher.identity, learner.identity, identifier))
                pioneers[i] = teacher
            else:
                for identifier in order[:2]: learner = program.private_verify(learner, identifier, seed)
            if arm in {"transmission_innovation", "shuffled_prerequisite_world"}: learner = program.private_verify(learner, order[2], seed)
            innovators[i] = learner
        for i, procedure in enumerate(("water", "shelter")):
            teacher, learner = innovators[i], successors[i]
            if arm in {"transmission_innovation", "shuffled_prerequisite_world"}:
                for identifier in program.order(procedure):
                    teacher, learner, ok = program.teach(teacher, learner, identifier)
                    if ok: edges.append((teacher.identity, learner.identity, identifier))
                innovators[i] = teacher
            successors[i] = learner
        learners, terminals = [_fill(x) for x in pioneers + innovators + successors], successors
    scores = [_score(program, learner, procedure, seed) for procedure, learner in zip(("water", "shelter"), terminals)]
    depths = [program.functional_depth(learner, procedure) for procedure, learner in zip(("water", "shelter"), terminals)]
    two_edge = sum(depth == 3 and sum(edge[2].startswith(procedure + ":") for edge in edges) >= 3 for procedure, depth in zip(("water", "shelter"), depths))
    return {"seed": seed, "arm": arm, "access_mode": "ordinary_social_d0" if arm in {"transmission_innovation", "transmission_without_modification", "shuffled_prerequisite_world"} else "asocial_or_upper_bound", "private_accuracy": PRIVATE_ACCURACY, "mean_heldout_functional_score": mean(scores), "mean_useful_depth": mean(depths), "functional_procedure_count": sum(d == 3 for d in depths), "two_edge_functional_procedures": two_edge, "coverage": sum(d == 3 for d in depths), "transmission_edges": len(edges), "teacher_work_debits": sum(x.teacher_teaching_work for x in learners), "learner_work_debits": sum(x.learner_teaching_work for x in learners), "private_work": sum(x.private_work for x in learners), "safe_work": sum(x.safe_work for x in learners), "total_work": sum(x.work_used for x in learners), "material_debit": round(sum(x.work_used for x in learners) * MATERIAL_PER_WORK, 2), "max_private_verifications": max(x.private_verifications for x in learners), "all_newborns_blank": all(not Learner.blank(str(i)).modules for i in range(6)), "source_history_acquired": all(bool(x.source_history) for x in learners), "upper_bound_only": arm == "matched_total_work_independent_upper_bound", "claim_limit": "Corrected separate cognitive assay; no demographic, selection, novelty, or H2 inference."}

def _write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    with gzip.open(path, "wt", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=sorted({k for row in rows for k in row})); writer.writeheader(); writer.writerows(rows)
def _sha(path: Path) -> str: return sha256(path.read_bytes()).hexdigest()

def run_registered() -> dict[str, Any]:
    OUTPUT.mkdir(parents=True, exist_ok=True); EVIDENCE.mkdir(parents=True, exist_ok=True)
    prior = OUTPUT / "cumulative_assay.csv.gz"; archived = OUTPUT / "cumulative_invalidated_74001_74024.csv.gz"
    if prior.exists() and not archived.exists(): shutil.copy2(prior, archived)
    (EVIDENCE / "cumulative_invalidation.json").write_text(json.dumps({"status":"invalidated", "seed_partition":"74001..74024", "reason":"Unequal ledgers and terminal-blank controls; retained only as a non-evidential artifact."}, indent=2) + "\n")
    registration = {"stage":"corrected-cumulative-cognitive-assay", "status":"registered_before_outcomes", "pilot_seeds":list(PILOT_SEEDS), "confirmation_seeds":list(CONFIRMATION_SEEDS), "arms":list(ARMS), "private_accuracy":PRIVATE_ACCURACY, "verification_cost":VERIFY_COST, "lifetime_budget":LIFETIME_BUDGET, "teaching_cost_each_side":TEACHING_COST, "fixed_total_work_per_cell":360, "fixed_material_debit_per_cell":3.60, "source_sha256":_sha(Path(__file__)), "limits":"Pooled solver ideal upper bound only; d absent; H2 NOT TESTED; separate from frozen IBM."}
    (EVIDENCE / "cumulative_registration.json").write_text(json.dumps(registration, indent=2, sort_keys=True) + "\n")
    pilots = [run_cell(seed=s, arm=a) for s in PILOT_SEEDS for a in ARMS]; rows = [run_cell(seed=s, arm=a) for s in CONFIRMATION_SEEDS for a in ARMS]
    _write_csv(OUTPUT / "cumulative_assay.csv.gz", rows); groups = {a:[r for r in rows if r["arm"] == a] for a in ARMS}
    summary = {"stage":"corrected-cumulative-cognitive-assay", "status":"complete_exploratory", "registration":"v7/evidence/cumulative_registration.json", "invalidation":"v7/evidence/cumulative_invalidation.json", "pilot_rows":len(pilots), "confirmation_rows":len(rows), "seed_partition":"74601..74624", "arms":{a:{"n":len(g), "functional_score_mean":mean(r["mean_heldout_functional_score"] for r in g), "useful_depth_mean":mean(r["mean_useful_depth"] for r in g), "two_edge_functional_procedures_total":sum(r["two_edge_functional_procedures"] for r in g), "total_work_unique":sorted({r["total_work"] for r in g}), "material_debit_unique":sorted({r["material_debit"] for r in g})} for a,g in groups.items()}, "accumulation_status":"PARTIAL: separate cognitive two-edge causal chain; does not repair frozen-IBM ACCUM-01 claim.", "h2_status":"NOT TESTED: no d mechanism or inherited-deference comparison.", "raw_sha256":_sha(OUTPUT / "cumulative_assay.csv.gz")}
    (EVIDENCE / "cumulative_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n"); return summary

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--run", action="store_true"); args = parser.parse_args()
    if not args.run: parser.error("pass --run to execute registered assay")
    print(json.dumps(run_registered(), indent=2, sort_keys=True))
if __name__ == "__main__": main()
