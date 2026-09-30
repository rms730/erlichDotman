import copy
import json
from pathlib import Path

import pytest

from engineering_cascade.contracts import validate
from engineering_cascade.routing import route

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def task():
    return json.loads((ROOT / 'examples/task.json').read_text())


@pytest.fixture
def policy():
    return json.loads((ROOT / 'examples/policy.json').read_text())


def test_simple_known_work_starts_lightweight(task, policy):
    decision = route(task, policy)
    assert decision['tier'] == 1
    assert decision['status'] == 'ready'
    validate(decision, 'decision')


def test_safe_deterministic_operation_needs_no_model(task, policy):
    task.update(deterministic=True, stage='validation', mechanical=False)
    assert route(task, policy)['tier'] == 0


@pytest.mark.parametrize(('risk', 'tier'), [('medium', 2), ('high', 3), ('critical', 4)])
def test_mechanical_work_preserves_risk_floor(task, policy, risk, tier):
    task['risk'] = risk
    assert route(task, policy)['tier'] == tier


@pytest.mark.parametrize(('signal', 'tier'), [('security', 3), ('irreversible', 4), ('distributed', 3)])
def test_signals_raise_the_floor_even_if_declared_deterministic(task, policy, signal, tier):
    task.update(signals=[signal], deterministic=True)
    assert route(task, policy)['tier'] >= tier


def test_specified_implementation_can_downgrade_after_planning(task, policy):
    task.update(category='architecture', stage='planning', mechanical=False)
    assert route(task, policy)['tier'] == 3
    task.update(stage='implementation', mechanical=True)
    assert route(task, policy)['tier'] == 1


def test_unclear_work_cannot_downgrade(task, policy):
    task.update(ambiguity='high', mechanical=True)
    assert route(task, policy)['tier'] == 3


def test_security_category_cannot_disguise_risk_as_mechanical(task, policy):
    task.update(category='security')
    assert route(task, policy)['tier'] >= 3


def test_failed_attempt_escalates_above_the_attempted_tier(task, policy):
    decision = route(task, policy, {'attempts': 1, 'validation_failed': True, 'previous_tier': 2})
    assert decision['tier'] == 3
    assert 'validation_failure' in decision['reason_codes']


def test_context_expands_without_paying_for_a_stronger_model(task, policy):
    decision = route(task, policy, {'context_insufficient': True})
    assert decision['tier'] == 1
    assert decision['context_budget_tokens'] == 4000


def test_context_expansion_never_exceeds_policy_cap(task, policy):
    policy['max_context_tokens'] = 2100
    assert route(task, policy, {'context_insufficient': True})['context_budget_tokens'] == 2100


def test_retry_exhaustion_stops_execution(task, policy):
    result = route(task, policy, {'attempts': 3, 'previous_tier': 3, 'validation_failed': True})
    assert result['status'] == 'needs_human'
    assert 'attempt_limit' in result['reason_codes']


def test_unclear_root_cause_uses_advanced_debugging(task, policy):
    assert route(task, policy, {'root_cause_unclear': True})['tier'] == 3


def test_route_does_not_mutate_task_policy_or_evidence(task, policy):
    evidence = {'attempts': 1, 'validation_failed': True, 'previous_tier': 1}
    before = copy.deepcopy((task, policy, evidence))
    route(task, policy, evidence)
    assert (task, policy, evidence) == before


@pytest.mark.parametrize('evidence', [
    {'attempts': -1}, {'attempts': True}, {'previous_tier': 9},
    {'validation_failed': 'yes'}, {'pretend': True},
])
def test_malformed_evidence_cannot_change_routing(task, policy, evidence):
    with pytest.raises(ValueError):
        route(task, policy, evidence)


def test_schema_valid_integral_float_policy_is_normalized(task, policy):
    task['mechanical'] = False
    policy['category_tiers']['tiny_bug'] = 1.0
    policy['context_budgets']['1'] = 2000.0
    policy['skill_budget_tokens'] = 3000.0
    validate(policy, 'policy')
    decision = route(task, policy)
    assert decision['tier'] == 1
    assert type(decision['tier']) is int
    assert type(decision['context_budget_tokens']) is int
    assert type(decision['skill_budget_tokens']) is int
