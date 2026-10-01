"""Check declared workflow facts; do not infer evidence, schedule work or run code."""

from .contracts import validate


def _indexed(items, keys):
    indexed = {tuple(item[key] for key in keys): item for item in items}
    if len(indexed) != len(items):
        raise ValueError("Duplicate workflow identity")
    return indexed


def _journey(journey):
    if journey["owner"] is None:
        raise ValueError("Journey needs one accountable owner")
    transfer = journey["transfer"]
    if transfer:
        expected = transfer["to_owner"] if transfer["accepted"] else transfer["from_owner"]
        if journey["owner"] != expected or transfer["from_owner"] == transfer["to_owner"]:
            raise ValueError("Journey ownership transfer is inconsistent")
    captured = _indexed(journey["captured_evidence"], ("requirement",))
    if journey["outcome"] != "unknown" and journey["outcome_ref"] is None:
        raise ValueError("Application outcome needs evidence")
    if journey["state"] == "accepted":
        if journey["outcome"] != "passed" or journey["outcome_kind"] != "application":
            raise ValueError("Component success is not journey acceptance")
        if any((name,) not in captured for name in journey["required_evidence"]):
            raise ValueError("Journey acceptance omits required evidence")


def _priority(priority, identity):
    before = _indexed(priority["before"], ("project_id", "task_id"))
    after = _indexed(priority["after"], ("project_id", "task_id"))
    if not before.keys() <= after.keys():
        raise ValueError("Priority change drops an existing task")
    if identity not in after:
        raise ValueError("Priority change omits the incoming task")
    if sum(item["state"] == "active" for item in after.values()) > priority["wip_limit"]:
        raise ValueError("Priority change exceeds the declared WIP limit")
    for item in after.values():
        if item["state"] in {"paused", "displaced"}:
            if item["checkpoint_ref"] is None or item["next_step"] is None:
                raise ValueError("Interrupted task needs a checkpoint and next step")
        if item["state"] == "completed" and item["checkpoint_ref"] is None:
            raise ValueError("Completed task needs an outcome checkpoint")


def _integration(integration, revision):
    accepted = _indexed(integration["critical_behaviors"], ("id",))
    checks = _indexed(integration["candidate_checks"], ("id",))
    if accepted.keys() != checks.keys():
        raise ValueError("Candidate checks must cover every declared critical behavior")
    for check in checks.values():
        state = check["status"]
        if state != "not_checked" and check["revision"] != revision:
            raise ValueError("Candidate evidence belongs to another revision")
        if state in {"passed", "failed"} and check["evidence_ref"] is None:
            raise ValueError("Candidate check needs evidence")
        exclusion = check["exclusion"]
        if (state == "excluded") != (exclusion is not None):
            raise ValueError("Candidate exclusion needs explicit reason, impact and acceptance")
    acceptance = integration["acceptance"]
    if acceptance in {"accepted", "accepted_with_exclusions"}:
        excluded = [check for check in checks.values() if check["status"] == "excluded"]
        if any(check["status"] not in {"passed", "excluded"} for check in checks.values()):
            raise ValueError("Candidate acceptance has failed or unchecked critical behavior")
        if acceptance == "accepted" and excluded:
            raise ValueError("Candidate acceptance must disclose exclusions")
        if acceptance == "accepted_with_exclusions" and not excluded:
            raise ValueError("Candidate declares exclusions without any")
        if any(check["exclusion"]["acceptance"] != "accepted" for check in excluded):
            raise ValueError("Candidate exclusion acceptance remains unresolved")


def check_workflow(workflow, *, project_id=None, task_id=None, revision=None, worker=False):
    """Validate the optional v1 sidecar and its supplied facts, without side effects.

    Evidence references and owner acknowledgments are declarations, not verified
    artifacts. Priority inventories are host-local; never include them in workers.
    """
    validate(workflow, "workflow")
    for key, expected in (("project_id", project_id), ("task_id", task_id), ("revision", revision)):
        if expected is not None and workflow[key] != expected:
            raise ValueError("Workflow binding differs")
    if worker and "priority" in workflow:
        raise ValueError("Multi-project priority state stays with the orchestrator")
    if "journey" in workflow:
        _journey(workflow["journey"])
    if "priority" in workflow:
        _priority(workflow["priority"], (workflow["project_id"], workflow["task_id"]))
    if "retry" in workflow:
        retry = workflow["retry"]
        if retry["failure_evidence_ref"] is None and retry["capture_blocked_reason"] is None:
            raise ValueError("Retry needs failure evidence or a capture blocker")
    if "integration" in workflow:
        _integration(workflow["integration"], workflow["revision"])
