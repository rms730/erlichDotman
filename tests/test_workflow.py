import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from engineering_cascade.adapters import ManualAdapter
from engineering_cascade.contracts import validate
from engineering_cascade.handoff import build_packet
from engineering_cascade.routing import route
from engineering_cascade.workflow import check_workflow

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def cases():
    return json.loads((ROOT / 'evals/workflow_reliability/cases.json').read_text())


@pytest.mark.parametrize('family', ['stream', 'priority', 'integration'])
def test_supplied_workflow_families_pass_without_mutation(cases, family):
    record = cases[family]
    original = deepcopy(record)
    check_workflow(record)
    assert record == original


def test_stream_with_passing_components_still_needs_diagnostic_owner(cases):
    record = cases['stream']
    record['journey']['owner'] = None
    with pytest.raises(ValueError, match='owner'):
        check_workflow(record)


@pytest.mark.parametrize('kind', ['transport', 'component', 'unknown'])
def test_http_or_component_success_cannot_close_application_journey(cases, kind):
    journey = cases['stream']['journey']
    journey.update(state='accepted', outcome='passed', outcome_kind=kind,
                   outcome_ref='local://demo/component-checks',
                   captured_evidence=[{'requirement': 'terminal-event', 'ref': 'local://demo/event'}])
    with pytest.raises(ValueError, match='Component'):
        check_workflow(cases['stream'])


def test_journey_acceptance_requires_terminal_capture_and_application_result(cases):
    record = cases['stream']
    record['journey'].update(state='accepted', outcome='passed', outcome_kind='application',
                             outcome_ref='local://demo/usable-answer')
    with pytest.raises(ValueError, match='required evidence'):
        check_workflow(record)
    record['journey']['captured_evidence'] = [
        {'requirement': 'terminal-event', 'ref': 'local://demo/event'}]
    check_workflow(record)


def test_explained_application_failure_is_a_valid_diagnostic_result(cases):
    record = cases['stream']
    record['journey'].update(state='failed', outcome='failed', outcome_kind='application',
                             outcome_ref='local://demo/sanitized-terminal-error',
                             captured_evidence=[{'requirement': 'terminal-event',
                                                 'ref': 'local://demo/sanitized-terminal-error'}])
    check_workflow(record)
    assert record['journey']['state'] != 'accepted'


def test_owner_stays_responsible_until_transfer_is_accepted(cases):
    record = cases['stream']
    record['journey']['transfer'] = {
        'from_owner': 'journey-owner', 'to_owner': 'new-owner', 'accepted': False}
    check_workflow(record)
    record['journey']['owner'] = 'new-owner'
    with pytest.raises(ValueError, match='transfer'):
        check_workflow(record)
    record['journey']['transfer']['accepted'] = True
    check_workflow(record)


def test_priority_interruption_cannot_multiply_active_tasks_or_forget_continuation(cases):
    record = cases['priority']
    interrupted = record['priority']['after'][0]
    interrupted['state'] = 'active'
    with pytest.raises(ValueError, match='WIP'):
        check_workflow(record)
    interrupted['state'] = 'paused'
    for key in ['checkpoint_ref', 'next_step']:
        value = interrupted[key]
        interrupted[key] = None
        with pytest.raises(ValueError, match='checkpoint'):
            check_workflow(record)
        interrupted[key] = value
    check_workflow(record)


def test_displaced_task_must_remain_in_priority_inventory(cases):
    record = cases['priority']
    record['priority']['after'][0]['state'] = 'displaced'
    check_workflow(record)
    record['priority']['after'].pop(0)
    with pytest.raises(ValueError, match='drops'):
        check_workflow(record)


def test_priority_cannot_fake_completion_to_free_capacity(cases):
    record = cases['priority']
    record['priority']['after'][0].update(state='completed', checkpoint_ref=None)
    with pytest.raises(ValueError, match='outcome checkpoint'):
        check_workflow(record)


@pytest.mark.parametrize('change', ['missing', 'failed', 'unchecked', 'stale'])
def test_new_feature_tests_cannot_hide_lost_earlier_repair(cases, change):
    record = cases['integration']
    checks = record['integration']['candidate_checks']
    if change == 'missing':
        checks.clear()
    elif change == 'failed':
        checks[0]['status'] = 'failed'
    elif change == 'unchecked':
        checks[0].update(status='not_checked', revision=None, evidence_ref=None)
    else:
        checks[0]['revision'] = 'repair-r2'
    with pytest.raises(ValueError):
        check_workflow(record)


def test_explicit_exclusion_discloses_impact_and_separate_acceptance(cases):
    record = cases['integration']
    item = record['integration']['candidate_checks'][0]
    item.update(status='excluded', evidence_ref=None, exclusion={
        'reason': 'The candidate is limited to already-onboarded synthetic accounts.',
        'impact': 'Fresh onboarding remains unavailable.', 'acceptance': 'pending'})
    with pytest.raises(ValueError, match='disclose'):
        check_workflow(record)
    record['integration']['acceptance'] = 'pending'
    check_workflow(record)
    record['integration']['acceptance'] = 'accepted_with_exclusions'
    with pytest.raises(ValueError, match='unresolved'):
        check_workflow(record)
    item['exclusion']['acceptance'] = 'accepted'
    check_workflow(record)
    del item['exclusion']['impact']
    with pytest.raises(ValueError):
        check_workflow(record)


def test_executable_assembly_regression_is_checked_on_final_candidate(tmp_path, cases):
    source = tmp_path / 'gate.py'
    validator = tmp_path / 'check.py'
    validator.write_text('from gate import allowed\nassert allowed("initial", False)\n'
                         'assert not allowed("neighbor", False)\n')
    repaired = 'def allowed(route, consent):\n    return route == "initial" or consent\n'
    source.write_text(repaired)
    assert subprocess.run([sys.executable, str(validator)], cwd=tmp_path,
                          capture_output=True).returncode == 0
    # Candidate assembly takes the baseline guard and a passing unrelated new feature.
    source.write_text('def allowed(route, consent):\n    return consent\n')
    feature = tmp_path / 'feature.py'
    feature.write_text('assert "preferences".startswith("pref")\n')
    assert subprocess.run([sys.executable, str(feature)], cwd=tmp_path,
                          capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, str(validator)], cwd=tmp_path,
                          capture_output=True).returncode != 0
    record = cases['integration']
    record['integration']['candidate_checks'][0]['status'] = 'failed'
    with pytest.raises(ValueError, match='failed or unchecked'):
        check_workflow(record)
    source.write_text(repaired)
    assert subprocess.run([sys.executable, str(validator)], cwd=tmp_path,
                          capture_output=True).returncode == 0
    record['integration']['candidate_checks'][0]['status'] = 'passed'
    check_workflow(record)


def routing_inputs(record):
    task = json.loads((ROOT / 'examples/task.json').read_text())
    task.update(project_id=record['project_id'], task_id=record['task_id'])
    policy = json.loads((ROOT / 'examples/policy.json').read_text())
    return task, policy


def test_capture_retry_is_allowed_without_inventing_effective_controls(cases):
    record = cases['stream']
    task, policy = routing_inputs(record)
    decision = route(task, policy, workflow=record)
    assert decision['tier'] == 1
    assert decision['status'] == 'ready'
    assert 'capture_failure_evidence' in decision['reason_codes']
    assert record['retry']['effective_tier'] is None
    record['retry']['completed_attempts'] = 0
    assert route(task, policy, workflow=record)['status'] == 'ready'
    record['retry']['capture_blocked_reason'] = None
    with pytest.raises(ValueError, match='Retry needs'):
        route(task, policy, workflow=record)


@pytest.mark.parametrize(('kind', 'tier', 'budget'), [
    ('ownership', 1, 2000), ('tooling_access', 1, 2000), ('context', 1, 4000),
    ('implementation', 3, 8000), ('reasoning', 3, 8000),
])
def test_stall_classification_drives_remedy_before_capability_escalation(cases, kind, tier, budget):
    record = cases['stream']
    record['retry'].update(stall_kind=kind, purpose='implement', effective_tier=2,
                           failure_evidence_ref='local://demo/failure')
    task, policy = routing_inputs(record)
    decision = route(task, policy, {'validation_failed': True}, workflow=record)
    assert decision['tier'] == tier
    assert decision['context_budget_tokens'] == budget
    assert f'stall:{kind}' in decision['reason_codes']


def test_new_retry_boundary_keeps_limits_and_risk_floors(cases):
    record = cases['stream']
    task, policy = routing_inputs(record)
    task['risk'] = 'critical'
    assert route(task, policy, workflow=record)['tier'] == 4
    record['retry']['completed_attempts'] = policy['max_attempts']
    assert route(task, policy, workflow=record)['status'] == 'needs_human'


def test_retry_count_and_observed_tier_cannot_be_overridden_or_reset(cases):
    record = cases['stream']
    task, policy = routing_inputs(record)
    for evidence in [{'attempts': 0}, {'previous_tier': 2}]:
        with pytest.raises(ValueError, match='differs'):
            route(task, policy, evidence, workflow=record)
    record['retry']['effective_tier'] = 2
    route(task, policy, {'previous_tier': 2, 'attempts': 1}, workflow=record)


def test_empty_hypothesis_and_whitespace_owner_are_not_actionable(cases):
    record = cases['stream']
    for target, key in [(record['retry'], 'hypothesis'), (record['journey'], 'owner')]:
        previous = target[key]
        target[key] = '  '
        with pytest.raises(ValueError):
            check_workflow(record)
        target[key] = previous


def packet_and_decision(record):
    task, policy = routing_inputs(record)
    decision = route(task, policy)
    project = json.loads((ROOT / 'examples/project.json').read_text())
    project.update(project_id=task['project_id'], revision=record['revision'], repository=str(ROOT))
    details = json.loads((ROOT / 'examples/packet-details.json').read_text())
    packet = build_packet(task, project, decision, [], **details)
    validate(packet, 'packet')
    return packet, decision


def test_dispatch_preserves_workflow_and_unknown_usage_without_mutating_inputs(cases):
    record = cases['stream']
    packet, decision = packet_and_decision(record)
    previous = deepcopy((packet, decision, record))
    _, policy = routing_inputs(record)
    result = ManualAdapter().prepare(packet, decision, record, policy)
    assert (packet, decision, record) == previous
    assert result['effective_tier'] is None and result['usage'] is None
    assert not any(result['capabilities'].values())
    assert result['retry_attempt_limit'] == policy['max_attempts']
    result['workflow']['journey']['owner'] = 'different'
    assert record['journey']['owner'] == 'journey-owner'


def test_worker_dispatch_rejects_parent_priority_state_and_foreign_binding(cases):
    record = cases['priority']
    packet, decision = packet_and_decision(record)
    with pytest.raises(ValueError, match='orchestrator'):
        ManualAdapter().prepare(packet, decision, record)
    record = cases['stream']
    packet, decision = packet_and_decision(record)
    for key in ['project_id', 'task_id', 'revision']:
        changed = deepcopy(record)
        changed[key] = 'foreign'
        with pytest.raises(ValueError, match='binding'):
            ManualAdapter().prepare(packet, decision, changed)


def test_duplicate_critical_behavior_or_candidate_check_is_rejected(cases):
    for key in ['critical_behaviors', 'candidate_checks']:
        record = deepcopy(cases['integration'])
        record['integration'][key].append(deepcopy(record['integration'][key][0]))
        with pytest.raises(ValueError, match='Duplicate'):
            check_workflow(record)


def test_retry_dispatch_cannot_use_old_ready_decision_to_bypass_exhaustion(cases):
    record = cases['stream']
    packet, earlier_decision = packet_and_decision(record)
    task, policy = routing_inputs(record)
    with pytest.raises(ValueError, match='active policy'):
        ManualAdapter().prepare(packet, earlier_decision, record)
    record['retry']['completed_attempts'] = policy['max_attempts']
    assert route(task, policy, workflow=record)['status'] == 'needs_human'
    with pytest.raises(ValueError, match='limit exhausted'):
        ManualAdapter().prepare(packet, earlier_decision, record, policy)
    record['retry']['completed_attempts'] = 1
    foreign_policy = deepcopy(policy)
    foreign_policy['policy_id'] = 'different'
    with pytest.raises(ValueError, match='policy differs'):
        ManualAdapter().prepare(packet, earlier_decision, record, foreign_policy)
