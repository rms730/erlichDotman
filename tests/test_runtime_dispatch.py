"""Synthetic checks for explicit host controls; no model or validator execution."""

from copy import deepcopy
from pathlib import Path

import pytest

from engineering_cascade.adapters import ManualAdapter
from engineering_cascade.contracts import load_json, validate
from engineering_cascade.handoff import build_packet
from engineering_cascade.routing import route

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs(tmp_path):
    task = load_json(ROOT / 'examples/task.json')
    policy = load_json(ROOT / 'examples/policy.json')
    project = load_json(ROOT / 'examples/project.json')
    project['repository'] = str(tmp_path)
    runtime = {
        'schema_version': 1, 'policy_id': 'synthetic-runtime-v1',
        'profiles': {
            'routine': {'model': 'example-light', 'reasoning': 'low'},
            'engineering': {'model': 'example-standard', 'reasoning': 'medium'},
            'escalation': {'model': 'example-frontier', 'reasoning': 'high'},
        },
        'max_attempts': 2, 'max_parallel_workers': 1,
    }
    launch = {
        'schema_version': 1, 'project_id': task['project_id'], 'task_id': task['task_id'],
        'revision': project['revision'], 'run_id': 'synthetic-run',
        'completed_attempts': 0, 'active_workers': 0, 'stop_requested': False,
        'escalation_reason': None,
    }
    return dict(task=task, policy=policy, project=project, runtime=runtime, launch=launch)


def prepare(inputs, host_ack=None, workflow=None):
    decision = route(inputs['task'], inputs['policy'], workflow=workflow)
    packet = build_packet(inputs['task'], inputs['project'], decision, [],
                          **load_json(ROOT / 'examples/packet-details.json'))
    return ManualAdapter().prepare(
        packet, decision, workflow=workflow, policy=inputs['policy'],
        task=inputs['task'], runtime_policy=inputs['runtime'], launch=inputs['launch'],
        host_ack=host_ack,
    )


def acknowledge(result):
    return {
        'schema_version': 1, 'accepted': True,
        'capabilities': dict.fromkeys(
            ['model_selection', 'reasoning_selection', 'attempt_limit', 'parallel_limit'], True),
        'request': deepcopy(result['execution_request']),
    }


def observation(result):
    return {
        'schema_version': 1, 'request_id': result['execution_request']['request_id'],
        'effective_model': None, 'effective_reasoning': None, 'runtime_evidence': None,
        'input_tokens': None, 'cached_input_tokens': None, 'output_tokens': None,
        'usage_evidence': None, 'cost': None, 'currency': None, 'billing_evidence': None,
        'latency_ms': None,
    }


def test_manual_policy_request_stops_without_host_acknowledgment(inputs):
    result = prepare(inputs)
    assert result['status'] == 'blocked_host_controls'
    assert result['requested_model'] == 'example-light'
    assert result['requested_reasoning'] == 'low'
    assert result['effective_model'] is None and result['effective_reasoning'] is None
    assert result['usage'] is None and result['effective_tier'] is None
    assert result['capabilities']['execution'] is False
    validate(result, 'runtime_dispatch')


def test_matching_acknowledgment_prepares_but_does_not_claim_execution(inputs):
    result = prepare(inputs)
    accepted = prepare(inputs, acknowledge(result))
    assert accepted['status'] == 'awaiting_host_execution'
    assert accepted['effective_model'] is None and accepted['effective_reasoning'] is None
    assert accepted['capabilities']['model_selection'] is False
    assert accepted['unavailable_controls'] == []
    assert inputs['launch']['completed_attempts'] == 0


@pytest.mark.parametrize('control', [
    'model_selection', 'reasoning_selection', 'attempt_limit', 'parallel_limit',
])
def test_unsupported_control_blocks_dispatch(inputs, control):
    ack = acknowledge(prepare(inputs))
    ack['capabilities'][control] = False
    result = prepare(inputs, ack)
    assert result['status'] == 'blocked_host_controls'
    assert control in result['unavailable_controls']


def test_host_declining_controls_blocks_dispatch(inputs):
    ack = acknowledge(prepare(inputs))
    ack['accepted'] = False
    assert prepare(inputs, ack)['status'] == 'blocked_host_controls'


@pytest.mark.parametrize('change', ['revision', 'run', 'packet', 'runtime'])
def test_acknowledgment_cannot_be_reused_after_bound_inputs_change(inputs, change):
    ack = acknowledge(prepare(inputs))
    if change == 'revision':
        inputs['project']['revision'] = inputs['launch']['revision'] = 'different-revision'
    elif change == 'run':
        inputs['launch']['run_id'] = 'other-run'
    elif change == 'packet':
        inputs['task']['objective'] = 'A different scoped repair'
    else:
        inputs['runtime']['profiles']['routine']['reasoning'] = 'medium'
    with pytest.raises(ValueError, match='acknowledgment'):
        prepare(inputs, ack)


@pytest.mark.parametrize('field,value,message', [
    ('active_workers', 1, 'Parallel'),
    ('completed_attempts', 2, 'attempt'),
    ('stop_requested', True, 'Stop'),
])
def test_limits_and_stop_request_fail_closed(inputs, field, value, message):
    inputs['launch'][field] = value
    with pytest.raises(ValueError, match=message):
        prepare(inputs)


def test_ordinary_engineering_uses_standard_profile(inputs):
    inputs['task'].update(category='feature', mechanical=False, complexity='medium')
    assert prepare(inputs)['requested_model'] == 'example-standard'


@pytest.mark.parametrize('field,value', [
    ('ambiguity', 'medium'), ('risk', 'medium'), ('signals', ['unfamiliar']),
])
def test_routine_profile_cannot_disguise_higher_scope(inputs, field, value):
    inputs['task'][field] = value
    assert prepare(inputs)['requested_model'] == 'example-standard'


def test_frontier_profile_is_reserved_for_explicit_escalation_or_high_risk_review(inputs):
    inputs['task'].update(stage='review', category='review', risk='high')
    assert prepare(inputs)['requested_model'] == 'example-frontier'
    inputs['task'].update(stage='implementation', risk='critical')
    with pytest.raises(ValueError, match='Frontier'):
        prepare(inputs)
    inputs['task']['stage'] = 'escalation'
    inputs['launch']['escalation_reason'] = 'capability_gap'
    assert prepare(inputs)['requested_model'] == 'example-frontier'


def test_escalation_needs_a_defined_reason(inputs):
    inputs['task']['stage'] = 'escalation'
    with pytest.raises(ValueError, match='Escalation'):
        prepare(inputs)


def test_deterministic_dispatch_requests_no_model_controls(inputs):
    inputs['task']['deterministic'] = True
    result = prepare(inputs)
    assert result['requested_model'] is None and result['requested_reasoning'] is None
    ack = acknowledge(result)
    ack['capabilities']['model_selection'] = False
    ack['capabilities']['reasoning_selection'] = False
    assert prepare(inputs, ack)['status'] == 'awaiting_host_execution'


def test_unknown_observation_is_not_promoted_to_verified_settings(inputs):
    result = prepare(inputs)
    result = prepare(inputs, acknowledge(result))
    recorded = ManualAdapter().record_execution(result, observation(result))
    assert recorded['status'] == 'host_execution_unverified'
    assert recorded['effective_model'] is None
    assert recorded['usage']['cost'] is None


def test_observed_mismatch_is_retained_as_control_violation(inputs):
    result = prepare(inputs)
    result = prepare(inputs, acknowledge(result))
    data = observation(result)
    data.update(effective_model='unexpected-model', effective_reasoning='low',
                runtime_evidence='synthetic-host-receipt')
    recorded = ManualAdapter().record_execution(result, data)
    assert recorded['status'] == 'host_control_violation'
    assert recorded['effective_model'] == 'unexpected-model'
    assert result['effective_model'] is None


def test_token_counts_do_not_establish_billed_cost(inputs):
    result = prepare(inputs)
    result = prepare(inputs, acknowledge(result))
    data = observation(result)
    data.update(input_tokens=120, cached_input_tokens=20, output_tokens=30,
                usage_evidence='synthetic-token-receipt')
    recorded = ManualAdapter().record_execution(result, data)
    assert recorded['usage']['cost'] is None
    data.update(cost=1.5, currency='credits')
    with pytest.raises(ValueError, match='billing'):
        ManualAdapter().record_execution(result, data)
    data['billing_evidence'] = 'synthetic-billing-receipt'
    assert ManualAdapter().record_execution(result, data)['usage']['cost'] == 1.5


@pytest.mark.parametrize('change', ['request', 'cached', 'runtime_evidence', 'usage_evidence'])
def test_invalid_observation_is_rejected(inputs, change):
    result = prepare(inputs)
    result = prepare(inputs, acknowledge(result))
    data = observation(result)
    if change == 'request':
        data['request_id'] = '0' * 64
    elif change == 'cached':
        data.update(input_tokens=10, cached_input_tokens=20,
                    usage_evidence='synthetic-token-receipt')
    elif change == 'runtime_evidence':
        data['effective_model'] = 'example-light'
    else:
        data['input_tokens'] = 10
    with pytest.raises(ValueError):
        ManualAdapter().record_execution(result, data)


def test_blocked_request_cannot_record_execution(inputs):
    result = prepare(inputs)
    with pytest.raises(ValueError, match='acknowledged'):
        ManualAdapter().record_execution(result, observation(result))


def test_recorded_matching_settings_are_observations_not_task_acceptance(inputs):
    result = prepare(inputs)
    result = prepare(inputs, acknowledge(result))
    data = observation(result)
    data.update(effective_model='example-light', effective_reasoning='low',
                runtime_evidence='synthetic-host-receipt')
    recorded = ManualAdapter().record_execution(result, data)
    assert recorded['status'] == 'host_controls_observed'
    assert recorded['usage']['cost'] is None
    assert 'task_success' not in recorded


def test_observation_cannot_follow_packet_mutation(inputs):
    result = prepare(inputs)
    result = prepare(inputs, acknowledge(result))
    result['packet']['desired_behavior'] = 'Changed after acknowledgment'
    with pytest.raises(ValueError, match='packet'):
        ManualAdapter().record_execution(result, observation(result))


def test_configurable_worker_limit_allows_one_more_declared_worker(inputs):
    inputs['runtime']['max_parallel_workers'] = 2
    inputs['launch']['active_workers'] = 1
    result = prepare(inputs)
    assert result['execution_request']['max_parallel_workers'] == 2


def test_retry_count_requires_workflow_and_stricter_policy_limit(inputs):
    inputs['launch']['completed_attempts'] = 1
    with pytest.raises(ValueError, match='classified workflow'):
        prepare(inputs)
    workflow = load_json(ROOT / 'evals/workflow_reliability/cases.json')['stream']
    inputs['task'].update(project_id=workflow['project_id'], task_id=workflow['task_id'])
    inputs['project'].update(project_id=workflow['project_id'], revision=workflow['revision'])
    inputs['launch'].update(project_id=workflow['project_id'], task_id=workflow['task_id'],
                            revision=workflow['revision'])
    request = prepare(inputs, workflow=workflow)['execution_request']
    assert request['attempt'] == 2 and request['max_attempts'] == 2
    inputs['policy']['max_attempts'] = 1
    with pytest.raises(ValueError):
        prepare(inputs, workflow=workflow)


def test_runtime_fields_cannot_silently_fall_back_to_uncontrolled_dispatch(inputs):
    decision = route(inputs['task'], inputs['policy'])
    packet = build_packet(inputs['task'], inputs['project'], decision, [],
                          **load_json(ROOT / 'examples/packet-details.json'))
    with pytest.raises(ValueError, match='runtime policy'):
        ManualAdapter().prepare(packet, decision, launch=inputs['launch'])


def test_request_contract_rejects_model_free_inference_profile(inputs):
    request = prepare(inputs)['execution_request']
    request['requested_model'] = None
    with pytest.raises(ValueError):
        validate(request, 'execution_request')


def test_runtime_cli_blocks_without_ack_and_records_observations(inputs, tmp_path, capsys):
    import json

    from engineering_cascade.cli import main

    decision = route(inputs['task'], inputs['policy'])
    packet = build_packet(inputs['task'], inputs['project'], decision, [],
                          **load_json(ROOT / 'examples/packet-details.json'))
    values = dict(task=inputs['task'], policy=inputs['policy'], runtime=inputs['runtime'],
                  launch=inputs['launch'], decision=decision, packet=packet)
    paths = {}
    for name, value in values.items():
        paths[name] = tmp_path / f'{name}.json'
        paths[name].write_text(json.dumps(value))
    arguments = ['dispatch', str(paths['packet']), '--decision', str(paths['decision']),
                 '--policy', str(paths['policy']), '--task', str(paths['task']),
                 '--runtime-policy', str(paths['runtime']), '--launch', str(paths['launch'])]
    assert main(arguments) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked['status'] == 'blocked_host_controls'
    ack = tmp_path / 'ack.json'
    ack.write_text(json.dumps(acknowledge(blocked)))
    assert main([*arguments, '--host-ack', str(ack)]) == 0
    accepted = json.loads(capsys.readouterr().out)
    prepared = tmp_path / 'prepared.json'
    prepared.write_text(json.dumps(accepted))
    data = observation(accepted)
    data.update(effective_model='example-light', effective_reasoning='low',
                runtime_evidence='synthetic-receipt')
    observed = tmp_path / 'observation.json'
    observed.write_text(json.dumps(data))
    assert main(['record-execution', str(prepared), str(observed)]) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'host_controls_observed'


@pytest.mark.parametrize('filename,kind', [
    ('runtime-policy.json', 'runtime_policy'), ('launch.json', 'launch_context'),
])
def test_synthetic_runtime_examples_conform(filename, kind):
    validate(load_json(ROOT / 'examples' / filename), kind)


@pytest.mark.parametrize('change', ['revision', 'hypothesis', 'drop'])
def test_observation_rejects_workflow_mutated_after_acknowledgment(inputs, change):
    workflow = load_json(ROOT / 'evals/workflow_reliability/cases.json')['stream']
    inputs['task'].update(project_id=workflow['project_id'], task_id=workflow['task_id'])
    inputs['project'].update(project_id=workflow['project_id'], revision=workflow['revision'])
    inputs['launch'].update(project_id=workflow['project_id'], task_id=workflow['task_id'],
                            revision=workflow['revision'], completed_attempts=1)
    pending = prepare(inputs, workflow=workflow)
    result = prepare(inputs, acknowledge(pending), workflow=workflow)
    if change == 'drop':
        del result['workflow']
    elif change == 'revision':
        result['workflow']['revision'] = 'other-revision'
    else:
        result['workflow']['retry']['hypothesis'] = 'Changed after acknowledgment'
    with pytest.raises(ValueError, match='workflow'):
        ManualAdapter().record_execution(result, observation(result))
