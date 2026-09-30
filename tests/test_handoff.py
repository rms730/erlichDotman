"""A handoff carries every required fact without granting permission."""

from copy import deepcopy

import pytest

from engineering_cascade.handoff import build_packet, render_packet


def inputs(tmp_path):
    task = {
        "schema_version": 1, "project_id": "demo", "task_id": "fix",
        "category": "tiny_bug", "stage": "implementation", "objective": "Fix parsing.",
        "complexity": "low", "ambiguity": "low", "risk": "low", "signals": [],
        "mechanical": True, "deterministic": False, "required_capabilities": [],
        "validation_commands": [["python", "-m", "pytest"]],
    }
    project = {
        "schema_version": 1, "project_id": "demo", "repository": str(tmp_path),
        "branch": "main", "revision": "r1", "stack": ["Python"],
        "architecture": "Library.", "conventions": [], "objectives": [],
        "constraints": ["Keep compatibility."], "decisions": [],
        "validation_commands": [["python", "-m", "pytest"]], "skill_roots": [],
        "instructions": [],
    }
    decision = {
        "schema_version": 1, "project_id": "demo", "task_id": "fix", "policy_id": "p1",
        "tier": 1, "context_budget_tokens": 8, "skill_budget_tokens": 5,
        "reason_codes": ["category:tiny_bug"],
        "validation_commands": [["python", "-m", "pytest"]],
        "escalate_if": ["Validation fails."], "status": "ready",
    }
    context = [{
        "id": "facts", "project_id": "demo", "revision": "r1", "content": "Keep all facts.",
        "estimated_tokens": 4, "required": True, "trust": "repository-local",
    }]
    details = {
        "why": "Users cannot parse empty input.", "files": ["src/parser.py"],
        "symbols": ["parse"], "current_behavior": "Empty input raises.",
        "desired_behavior": "Empty input returns an empty list.",
        "invariants": ["Valid inputs still parse."], "implementation_notes": ["Handle empty input."],
        "tests": ["Cover empty input."], "do_not_change": ["Public signature."],
        "expected_output": "Reviewable diff and passing checks.",
    }
    return task, project, decision, context, details


def test_packet_binds_identity_preserves_facts_and_does_not_mutate_inputs(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    snapshot = deepcopy((task, project, decision, context, details))
    packet = build_packet(task, project, decision, context, **details)
    assert (packet["project_id"], packet["task_id"], packet["revision"], packet["tier"]) == (
        "demo", "fix", "r1", 1)
    assert packet["constraints"] == ["Keep compatibility."]
    assert packet["context"] == context
    assert (task, project, decision, context, details) == snapshot
    packet["context"][0]["content"] = "changed"
    assert context[0]["content"] == "Keep all facts."


@pytest.mark.parametrize("field,value", [
    ("project_id", "foreign"), ("task_id", "other"), ("status", "needs_human")])
def test_handoff_rejects_foreign_or_blocked_decision(tmp_path, field, value):
    task, project, decision, context, details = inputs(tmp_path)
    decision[field] = value
    with pytest.raises(ValueError):
        build_packet(task, project, decision, context, **details)


def test_handoff_rejects_stale_mixed_or_over_budget_context(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    for field, value in (("revision", "r0"), ("project_id", "foreign"), ("estimated_tokens", 9)):
        changed = deepcopy(context)
        changed[0][field] = value
        with pytest.raises(ValueError):
            build_packet(task, project, decision, changed, **details)
    selection = {"items": context, "estimated_tokens": 0, "omitted": []}
    with pytest.raises(ValueError, match="estimate"):
        build_packet(task, project, decision, selection, **details)


@pytest.mark.parametrize("path", ["../secrets", "/tmp/secrets", "a/../../secrets", "C:\\secrets", "..\\secrets", "\\secrets"])
def test_handoff_rejects_absolute_and_traversal_targets(tmp_path, path):
    task, project, decision, context, details = inputs(tmp_path)
    details["files"] = [path]
    with pytest.raises(ValueError, match="path"):
        build_packet(task, project, decision, context, **details)


def test_handoff_checks_target_symlink_and_context_source_escape(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    outside = tmp_path.parent / "outside"
    outside.mkdir(exist_ok=True)
    (tmp_path / "escape").symlink_to(outside, target_is_directory=True)
    details["files"] = ["escape/new.py"]
    with pytest.raises(ValueError, match="outside"):
        build_packet(task, project, decision, context, **details)
    details["files"] = ["src/parser.py"]
    context[0]["path"] = "../foreign/facts.txt"
    with pytest.raises(ValueError, match="path"):
        build_packet(task, project, decision, context, **details)


def test_handoff_identity_cannot_be_overridden_or_unknown_details_hidden(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    for extra in ({"tier": 4}, {"revision": "r0"}, {"project_id": "foreign"}, {"unknown": "value"}):
        with pytest.raises(ValueError):
            build_packet(task, project, decision, context, **details, **extra)


@pytest.mark.parametrize("field,value", [("constraints", "a string"),
                                        ("escalate_if", False),
                                        ("validation_commands", ["shell command"])])
def test_handoff_rejects_wrong_detail_types_with_contract_errors(tmp_path, field, value):
    task, project, decision, context, details = inputs(tmp_path)
    details[field] = value
    with pytest.raises(ValueError):
        build_packet(task, project, decision, context, **details)


def test_missing_handoff_facts_cannot_be_invented(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    del details["invariants"]
    with pytest.raises(ValueError, match="invariants"):
        build_packet(task, project, decision, context, **details)


def test_explicit_constraints_and_validation_supplement_existing_facts(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    task["validation_commands"] = [["python", "-m", "pytest", "tests/test_parser.py"]]
    project["validation_commands"] = [["python", "-m", "ruff", "check", "."]]
    decision["validation_commands"] = [["python", "-m", "pytest"]]
    details["constraints"] = ["Preserve performance."]
    details["validation_commands"] = [["python", "-m", "pytest"]]
    packet = build_packet(task, project, decision, context, **details)
    assert packet["constraints"] == ["Keep compatibility.", "Preserve performance."]
    assert len(packet["validation_commands"]) == 3
    rendered = render_packet(packet)
    assert "tests/test_parser.py" in rendered
    assert "ruff check ." in rendered


def test_schema_integer_tiers_budgets_and_estimates_are_normalized(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    decision["tier"] = 1.0
    decision["context_budget_tokens"] = 8.0
    context[0]["estimated_tokens"] = 4.0
    selection = {"items": context, "estimated_tokens": 4.0, "omitted": []}
    packet = build_packet(task, project, decision, selection, **details)
    assert type(packet["tier"]) is int
    assert type(packet["context"][0]["estimated_tokens"]) is int
    assert "Tier 1" in render_packet(packet)
    packet["context"][0]["estimated_tokens"] = 4.0
    assert "Keep all facts." in render_packet(packet)


def test_markdown_render_includes_every_nonempty_fact_and_quotes_argv(tmp_path):
    task, project, decision, context, details = inputs(tmp_path)
    decision["validation_commands"] = [["python", "script with spaces.py", "$(danger)"]]
    packet = build_packet(task, project, decision, context, **details)
    rendered = render_packet(packet)
    for value in ("demo", "fix", "r1", "Tier 1", "Fix parsing.", "Keep compatibility.",
                  "Public signature.", "Keep all facts.", "Validation fails.", "src/parser.py",
                  "script with spaces.py", "'$(danger)'", "Reviewable diff and passing checks."):
        assert value in rendered
    assert "display only" in rendered
    invalid = deepcopy(packet)
    invalid["revision"] = "r0"
    with pytest.raises(ValueError):
        render_packet(invalid)
