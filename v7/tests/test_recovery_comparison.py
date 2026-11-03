import unittest
from v7.experiments.model import KeyedRNG, PolicyObservation
from v7.experiments.recovery_comparators import MatchedActionConditionalPolicy, comparator_contract
from v7.experiments.recovery_culture import run_cell
from v7.experiments.recovery_culture_v2 import run_cell as run_cell_v2
from v7.experiments.recovery_culture_matched import run_pair

def test_matched_query_hardware_and_truth_firewall():
    contract=comparator_contract(); assert contract["query_expected_accuracy"] == contract["query_executed_accuracy"] == .8
    decision=MatchedActionConditionalPolicy().decide(PolicyObservation.contract_fixture(),128,KeyedRNG.fixture("recovery"))
    assert decision.operation_count <= 128

def test_demographic_blank_birth_costs_and_storage_off():
    row=run_cell(82001,"carrier_loss_storage_off",no_innovation_after_loss=True)
    assert row["storage_items_end"] == 0 and row["work_paid"] >= row["private_work"]
    assert row["knowledge_immediately_after_loss"] is not None

def test_equal_work_is_per_person_feasible():
    row=run_cell(82001,"equal_work_independent")
    assert row["work_paid"] >= 0 and row["population"] <= row["population_cap"]

def test_v2_forced_cap_is_explicit_stop_not_census_suppression():
    row=run_cell_v2(82100,"transmission_innovation",population_cap=2,start_population=2,birth_probability=1.)
    assert row["status"]=="cap_censored" and row["cap_events"]==1 and row["population"]==2

def test_matched_work_is_exact_and_nonpooled():
    row=run_pair(82201)
    assert row["ti_realized_work"]==row["independent_realized_work"]==row["offered_work_total"]
    assert not row["any_infeasible"]

class RecoveryComparisonTests(unittest.TestCase):
    def test_hardware_and_firewall(self): test_matched_query_hardware_and_truth_firewall()
    def test_blank_birth_costs_storage(self): test_demographic_blank_birth_costs_and_storage_off()
    def test_equal_work_feasible(self): test_equal_work_is_per_person_feasible()
    def test_v2_forced_cap(self): test_v2_forced_cap_is_explicit_stop_not_census_suppression()
    def test_matched_work(self): test_matched_work_is_exact_and_nonpooled()
