import pytest

from engineering_cascade.adapters import ManualAdapter


def test_manual_adapter_reports_unavailable_runtime_controls():
    adapter = ManualAdapter()
    assert adapter.capabilities['model_selection'] is False
    assert adapter.capabilities['exact_usage'] is False
    assert adapter.capabilities['execution'] is False


def test_manual_dispatch_requires_validated_packet():
    with pytest.raises(ValueError):
        ManualAdapter().prepare({}, {})


@pytest.fixture
def packet_and_decision(tmp_path):
    from pathlib import Path

    from engineering_cascade.contracts import load_json
    from engineering_cascade.handoff import build_packet
    from engineering_cascade.routing import route
    root = Path(__file__).resolve().parents[1]
    task = load_json(root / 'examples/task.json')
    project = load_json(root / 'examples/project.json')
    project['repository'] = str(tmp_path)
    decision = route(task, load_json(root / 'examples/policy.json'))
    packet = build_packet(task, project, decision, [],
                          **load_json(root / 'examples/packet-details.json'))
    return packet, decision


def test_valid_manual_request_preserves_unknown_effective_tier(packet_and_decision):
    packet, decision = packet_and_decision
    prepared = ManualAdapter().prepare(packet, decision)
    assert prepared['effective_tier'] is None
    assert prepared['usage'] is None
    assert prepared['status'] == 'awaiting_host_execution'


def test_raw_packet_cannot_bypass_relative_file_boundary(packet_and_decision):
    packet, decision = packet_and_decision
    packet['files'] = ['../../other-project/secret.txt']
    with pytest.raises(ValueError):
        ManualAdapter().prepare(packet, decision)


def test_dispatch_cannot_drop_decision_validation(packet_and_decision):
    packet, decision = packet_and_decision
    packet['validation_commands'] = [['python', '-c', 'pass']]
    with pytest.raises(ValueError):
        ManualAdapter().prepare(packet, decision)


def test_dispatch_cannot_drop_decision_escalation(packet_and_decision):
    packet, decision = packet_and_decision
    packet['escalate_if'] = ['different-condition']
    with pytest.raises(ValueError):
        ManualAdapter().prepare(packet, decision)
