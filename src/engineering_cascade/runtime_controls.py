"""Check declared launch controls. No launcher, scheduler or billing estimator."""

import hashlib
import json
from copy import deepcopy

from .contracts import validate
from .routing import route


def _digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def prepare_execution(task, packet, decision, policy, runtime_policy, launch, workflow=None):
    """Bind private model settings and bounded supplied state to a dispatch request."""
    for value, kind in [(task, "task"), (runtime_policy, "runtime_policy"),
                        (launch, "launch_context")]:
        validate(value, kind)
    if policy is None:
        raise ValueError("Runtime dispatch requires the active routing policy")
    for key in ("project_id", "task_id"):
        if task[key] != packet[key] or launch[key] != packet[key]:
            raise ValueError("Runtime dispatch identity differs")
    if launch["revision"] != packet["revision"]:
        raise ValueError("Runtime dispatch revision differs")
    if task["objective"] != packet["objective"]:
        raise ValueError("Runtime task differs from packet")
    if route(task, policy, workflow=workflow) != decision:
        raise ValueError("Runtime dispatch requires a current routing decision")
    limit = min(runtime_policy["max_attempts"], policy["max_attempts"])
    if launch["completed_attempts"] >= limit:
        raise ValueError("Runtime attempt limit exhausted")
    if launch["active_workers"] >= runtime_policy["max_parallel_workers"]:
        raise ValueError("Parallel worker limit exhausted")
    if launch["stop_requested"]:
        raise ValueError("Stop requested before runtime dispatch")
    retry = (workflow or {}).get("retry")
    if launch["completed_attempts"] != (retry["completed_attempts"] if retry else 0):
        raise ValueError("Runtime retry counts require matching classified workflow evidence")

    tier = decision["tier"]
    high_risk_review = task["stage"] == "review" and (
        task["risk"] in {"high", "critical"} or
        bool(set(task["signals"]) & {"security", "irreversible", "production_critical"})
    )
    if task["stage"] == "escalation" and launch["escalation_reason"] is None:
        raise ValueError("Escalation requires a defined reason")
    if task["stage"] != "escalation" and launch["escalation_reason"] is not None:
        raise ValueError("Escalation reason requires an explicit escalation stage")
    if tier == 0:
        profile = "deterministic"
        controls = {"model": None, "reasoning": None}
    elif task["stage"] == "escalation" or high_risk_review:
        profile = "escalation"
        controls = runtime_policy["profiles"][profile]
    elif tier == 4:
        raise ValueError("Frontier route requires explicit escalation or high-risk review")
    elif (tier <= 1 and task["mechanical"] and task["risk"] == "low" and
          task["ambiguity"] == task["complexity"] == "low" and not task["signals"] and
          task["stage"] in {"implementation", "documentation", "validation"}):
        profile = "routine"
        controls = runtime_policy["profiles"][profile]
    else:
        profile = "engineering"
        controls = runtime_policy["profiles"][profile]
    request = {
        "schema_version": 1,
        **{key: packet[key] for key in ("project_id", "task_id", "revision")},
        "run_id": launch["run_id"], "runtime_policy_id": runtime_policy["policy_id"],
        "routing_policy_id": policy["policy_id"], "profile": profile,
        "requested_tier": tier, "requested_model": controls["model"],
        "requested_reasoning": controls["reasoning"],
        "attempt": launch["completed_attempts"] + 1, "max_attempts": limit,
        "active_workers": launch["active_workers"],
        "max_parallel_workers": runtime_policy["max_parallel_workers"],
        "packet_digest": _digest(packet),
        "workflow_digest": _digest(workflow) if workflow is not None else None,
    }
    request["request_id"] = _digest({"request": request, "task": task,
                                      "decision": decision, "runtime_policy": runtime_policy,
                                      "launch": launch, "workflow": workflow})
    validate(request, "execution_request")
    return request


def host_control_gaps(request, acknowledgment):
    """An acknowledgment is a host declaration, not proof of effective execution."""
    if acknowledgment is None:
        return ["host_acknowledgment"]
    validate(acknowledgment, "host_acknowledgment")
    if acknowledgment["request"] != request:
        raise ValueError("Host acknowledgment differs from current execution request")
    required = ["attempt_limit", "parallel_limit"]
    if request["requested_model"] is not None:
        required.extend(["model_selection", "reasoning_selection"])
    gaps = [name for name in required if not acknowledgment["capabilities"][name]]
    if not acknowledgment["accepted"]:
        gaps.append("host_declined")
    return gaps


def record_execution(prepared, observation):
    """Retain supplied observations, including violations and unknown measurements."""
    validate(prepared, "runtime_dispatch")
    request = prepared["execution_request"]
    if prepared["status"] != "awaiting_host_execution" or host_control_gaps(
        request, prepared["host_acknowledgment"]
    ):
        raise ValueError("Execution observation requires an acknowledged dispatch")
    if request["packet_digest"] != _digest(prepared["packet"]):
        raise ValueError("Observed dispatch packet differs from acknowledged packet")
    workflow = prepared.get("workflow")
    if request["workflow_digest"] != (_digest(workflow) if workflow is not None else None):
        raise ValueError("Observed dispatch workflow differs from acknowledged workflow")
    for key in ("requested_tier", "requested_model", "requested_reasoning"):
        if prepared[key] != request[key]:
            raise ValueError("Observed dispatch controls differ from acknowledged request")
    validate(observation, "execution_observation")
    if observation["request_id"] != request["request_id"]:
        raise ValueError("Execution observation binding differs")
    if any(observation[key] is not None for key in ("effective_model", "effective_reasoning")):
        if observation["runtime_evidence"] is None:
            raise ValueError("Effective settings require runtime evidence")
    usage_fields = ("input_tokens", "cached_input_tokens", "output_tokens", "latency_ms")
    if any(observation[key] is not None for key in usage_fields):
        if observation["usage_evidence"] is None:
            raise ValueError("Usage measurements require usage evidence")
    if (observation["cached_input_tokens"] is not None and
        observation["input_tokens"] is not None and
        observation["cached_input_tokens"] > observation["input_tokens"]):
        raise ValueError("Cached input exceeds total input tokens")
    if observation["cost"] is not None and (
        observation["billing_evidence"] is None or observation["currency"] is None
    ):
        raise ValueError("Cost requires billing evidence and a unit/currency")
    result = deepcopy(prepared)
    result["observation"] = deepcopy(observation)
    result["usage"] = {key: observation[key] for key in (
        *usage_fields, "usage_evidence", "cost", "currency", "billing_evidence")}
    for key in ("effective_model", "effective_reasoning"):
        result[key] = observation[key]
    pairs = [(observation["effective_model"], request["requested_model"]),
             (observation["effective_reasoning"], request["requested_reasoning"])]
    if any(actual is not None and actual != wanted for actual, wanted in pairs):
        result["status"] = "host_control_violation"
    elif observation["runtime_evidence"] is not None and all(
        actual == wanted for actual, wanted in pairs
    ):
        result["status"] = "host_controls_observed"
    else:
        result["status"] = "host_execution_unverified"
    validate(result, "runtime_dispatch")
    return result
