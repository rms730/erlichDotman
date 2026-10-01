"""Explicit, reviewable routing; decisions never authorize execution."""

from copy import deepcopy

from .contracts import validate


def _evidence(value):
    value = {} if value is None else value
    allowed = {"attempts", "validation_failed", "previous_tier", "root_cause_unclear",
               "context_insufficient"}
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError("Invalid evidence fields")
    attempts = value.get("attempts", 0)
    previous = value.get("previous_tier")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
        raise ValueError("Invalid attempt count")
    if previous is not None and (
        isinstance(previous, bool) or not isinstance(previous, int) or not 0 <= previous <= 4
    ):
        raise ValueError("Invalid previous tier")
    for key in allowed - {"attempts", "previous_tier"}:
        if key in value and not isinstance(value[key], bool):
            raise ValueError("Invalid evidence flag")
    return value


def route(task, policy, evidence=None, workflow=None):
    """Recommend a tier and context budget using classified task and observed evidence.

    attempts counts completed implementation attempts, not planning calls. Context
    expansion is independent of capability escalation. This policy is a heuristic,
    not an empirically calibrated expected-cost estimator.
    """
    validate(task, "task")
    validate(policy, "policy")
    # JSON Schema integers include 1.0. Normalize validated count fields without
    # mutating the caller, before using them as tier keys or loop bounds.
    policy = deepcopy(policy)
    for field in ("category_tiers", "risk_floors", "signal_floors", "context_budgets"):
        policy[field] = {key: int(value) for key, value in policy[field].items()}
    for field in ("max_attempts", "max_context_tokens", "skill_budget_tokens", "minimum_samples"):
        policy[field] = int(policy[field])
    evidence = deepcopy(_evidence(evidence))
    retry = None
    if workflow is not None:
        from .workflow import check_workflow
        check_workflow(workflow, project_id=task["project_id"], task_id=task["task_id"])
        retry = workflow.get("retry")
        if retry:
            attempts = int(retry["completed_attempts"])
            if "attempts" in evidence and evidence["attempts"] != attempts:
                raise ValueError("Retry attempt count differs")
            previous = retry["effective_tier"]
            if "previous_tier" in evidence and evidence["previous_tier"] != previous:
                raise ValueError("Retry effective tier differs")
            evidence["attempts"] = attempts
            evidence["previous_tier"] = None if previous is None else int(previous)
            kind = retry["stall_kind"]
            evidence["validation_failed"] = (
                kind in {"implementation", "reasoning"} and retry["purpose"] != "capture_evidence"
            )
            evidence["root_cause_unclear"] = kind == "reasoning"
            if kind == "context":
                evidence["context_insufficient"] = True
    reasons = ["category_default"]
    if retry:
        reasons.append(f"stall:{retry['stall_kind']}")
        if retry["purpose"] == "capture_evidence":
            reasons.append("capture_failure_evidence")
    baseline = policy["category_tiers"][task["category"]]
    floor = policy["risk_floors"][task["risk"]]
    level_floor = {"low": 0, "medium": 2, "high": 3}
    floor = max(floor, level_floor[task["complexity"]], level_floor[task["ambiguity"]])
    if task["risk"] != "low":
        reasons.append("risk_floor")
    if task["complexity"] != "low":
        reasons.append("complexity_floor")
    if task["ambiguity"] != "low":
        reasons.append("ambiguity_floor")
    for signal in task["signals"]:
        floor = max(floor, policy["signal_floors"][signal])
        reasons.append(f"signal:{signal}")

    # A security/migration task's category is itself evidence of consequential scope.
    if task["category"] in {"security", "migration"}:
        floor = max(floor, baseline)
    can_simplify = floor == 0 and not task["signals"]
    if task["deterministic"] and can_simplify:
        baseline = 0
        reasons.append("deterministic_resolution")
    elif (task["mechanical"] and can_simplify
          and task["stage"] in {"implementation", "documentation"}):
        baseline = 1
        reasons.append("specified_mechanical_work")
    elif task["stage"] in {"architecture", "planning"}:
        baseline = max(baseline, 3)
        reasons.append("design_stage")

    tier = max(baseline, floor)
    if evidence.get("root_cause_unclear"):
        tier = max(tier, 3)
        reasons.append("unclear_root_cause")
    if evidence.get("validation_failed"):
        previous = evidence.get("previous_tier")
        tier = max(tier, min(4, (tier if previous is None else previous) + 1))
        reasons.append("validation_failure")
    budget = policy["context_budgets"][str(tier)]
    if evidence.get("context_insufficient"):
        budget = max(2000, budget * 2)
        reasons.append("expand_context")
    status = "ready"
    if evidence.get("attempts", 0) >= policy["max_attempts"]:
        status = "needs_human"
        reasons.append("attempt_limit")
    decision = {
        "schema_version": 1,
        "project_id": task["project_id"],
        "task_id": task["task_id"],
        "policy_id": policy["policy_id"],
        "tier": tier,
        "context_budget_tokens": min(budget, policy["max_context_tokens"]),
        "skill_budget_tokens": policy["skill_budget_tokens"],
        "reason_codes": reasons,
        "validation_commands": deepcopy(task["validation_commands"]),
        "escalate_if": ["deterministic_validation_failed", "required_context_missing",
                        "invariants_unclear", "permission_required"],
        "status": status,
    }
    validate(decision, "decision")
    return decision
