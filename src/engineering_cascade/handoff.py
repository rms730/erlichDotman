"""Build complete, project-bound packets; routing never grants permission."""

import shlex
from copy import deepcopy
from pathlib import PurePosixPath, PureWindowsPath

from .context import _check_budget, _repository_file, select_context
from .contracts import validate

_DETAIL_FIELDS = {
    "why", "files", "symbols", "current_behavior", "desired_behavior", "invariants",
    "constraints", "implementation_notes", "tests", "validation_commands", "do_not_change",
    "escalate_if", "expected_output",
}
_MANDATORY_DETAILS = {"why", "current_behavior", "desired_behavior", "invariants", "tests", "expected_output"}


def _unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _safe_relative_path(path, repository=None):
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ValueError("path must be a nonempty relative path")
    posix = PurePosixPath(path)
    windows = PureWindowsPath(path)
    if (posix.is_absolute() or windows.is_absolute() or windows.drive or windows.root or
            ".." in posix.parts or ".." in windows.parts or path in (".", "./")):
        raise ValueError("path must be relative without traversal")
    if repository is not None:
        _repository_file(repository, path)


def _check_packet_binding(packet):
    validate(packet, "packet")
    selected = select_context(packet["context"], packet["project_id"], packet["revision"],
                              sum(int(item["estimated_tokens"]) for item in packet["context"]))
    for path in packet["files"]:
        _safe_relative_path(path)
    for item in selected["items"]:
        if "path" in item:
            _safe_relative_path(item["path"])


def build_packet(task, project, decision, context, **details):
    """Bind a routed task to complete handoff facts and checked context.

    ``context`` is a selected-context dictionary or a list of context items.
    Required prose, invariants, and tests must be supplied explicitly in details.
    Project constraints and every supplied validator/escalation condition survive.
    """
    for document, kind in ((task, "task"), (project, "project"), (decision, "decision")):
        validate(document, kind)
    if task["project_id"] != project["project_id"] or decision["project_id"] != project["project_id"]:
        raise ValueError("task, project, and decision project identities must match")
    if task["task_id"] != decision["task_id"]:
        raise ValueError("decision task identity does not match the task")
    if decision["status"] != "ready":
        raise ValueError("needs_human decision cannot produce an execution handoff")
    unknown = set(details) - _DETAIL_FIELDS
    if unknown:
        raise ValueError(f"unsupported or immutable packet details: {', '.join(sorted(unknown))}")
    missing = _MANDATORY_DETAILS - set(details)
    if missing:
        raise ValueError(f"missing required handoff facts: {', '.join(sorted(missing))}")
    for field in ("constraints", "escalate_if", "validation_commands"):
        if field in details and not isinstance(details[field], list):
            raise ValueError(f"{field} must be a list")
    if isinstance(context, dict):
        if set(context) != {"items", "estimated_tokens", "omitted"}:
            raise ValueError("invalid context selection fields")
        supplied_estimate = context["estimated_tokens"]
        if isinstance(supplied_estimate, float) and supplied_estimate.is_integer():
            supplied_estimate = int(supplied_estimate)
        _check_budget(supplied_estimate)
        if not isinstance(context["omitted"], list):
            raise ValueError("omitted context ids must be a list")
        items = context["items"]
    else:
        items = context
    # Validate identity and duplicate boundaries before accessing item estimates.
    checked = select_context(items, project["project_id"], project["revision"],
                             int(decision["context_budget_tokens"]))
    estimated = sum(int(item["estimated_tokens"]) for item in items)
    if estimated > decision["context_budget_tokens"]:
        raise ValueError("selected context exceeds the heuristic token budget")
    if isinstance(context, dict) and estimated != context["estimated_tokens"]:
        raise ValueError("context estimate does not match selected items")
    packet = {
        "schema_version": 1, "project_id": task["project_id"], "task_id": task["task_id"],
        "revision": project["revision"], "tier": int(decision["tier"]), "objective": task["objective"],
        "files": [], "symbols": [], "implementation_notes": [], "do_not_change": [],
        **deepcopy(details),
        "constraints": _unique(project["constraints"] + details.get("constraints", [])),
        "validation_commands": _unique(task["validation_commands"] + project["validation_commands"] +
                                       decision["validation_commands"] + details.get("validation_commands", [])),
        "escalate_if": _unique(decision["escalate_if"] + details.get("escalate_if", [])),
        "context": checked["items"],
    }
    _check_packet_binding(packet)
    for path in packet["files"]:
        _safe_relative_path(path, project["repository"])
    for item in packet["context"]:
        if "path" in item:
            _safe_relative_path(item["path"], project["repository"])
    return deepcopy(packet)


def render_packet(packet):
    """Render every nonempty contract field without executing display commands."""
    _check_packet_binding(packet)
    lines = [f"# {packet['objective']}", "",
             f"Project: {packet['project_id']} · Task: {packet['task_id']} · "
             f"Revision: {packet['revision']} · Tier {int(packet['tier'])} · Schema {int(packet['schema_version'])}", ""]
    labels = {
        "why": "Why", "files": "Files", "symbols": "Symbols", "current_behavior": "Current behavior",
        "desired_behavior": "Desired behavior", "invariants": "Invariants", "constraints": "Constraints",
        "implementation_notes": "Implementation notes", "tests": "Tests", "do_not_change": "Do not change",
        "escalate_if": "Escalate if", "expected_output": "Expected output",
    }
    for field, label in labels.items():
        value = packet[field]
        if not value:
            continue
        lines.extend((f"## {label}", ""))
        lines.extend((f"- {entry}" for entry in value) if isinstance(value, list) else [value])
        lines.append("")
    lines.extend(("## Validation commands (display only)", ""))
    for command in packet["validation_commands"]:
        lines.append(f"- {shlex.join(command)}")
    if packet["context"]:
        lines.extend(("", "## Context", ""))
        for item in packet["context"]:
            facts = [f"Project {item['project_id']}", f"Revision {item['revision']}",
                     f"Trust {item['trust']}", f"Required: {str(item['required']).lower()}",
                     f"Heuristic estimated tokens: {int(item['estimated_tokens'])}"]
            if item.get("path"):
                facts.append(f"Path: {item['path']}")
            if item.get("symbol"):
                facts.append(f"Symbol: {item['symbol']}")
            lines.extend((f"### {item['id']}", "", " · ".join(facts), "", item["content"], ""))
    return "\n".join(lines).rstrip() + "\n"
