"""Honest runtime boundary: v0.1 prepares work, it does not launch models."""

from copy import deepcopy

from .contracts import validate
from .handoff import _check_packet_binding


class ManualAdapter:
    """Produce a reviewable dispatch request for a human or host coding agent."""

    capabilities = {
        "model_selection": False,
        "reasoning_selection": False,
        "exact_usage": False,
        "execution": False,
    }

    def prepare(self, packet, decision, workflow=None, policy=None):
        _check_packet_binding(packet)
        validate(decision, "decision")
        for key in ("project_id", "task_id", "tier"):
            if packet[key] != decision[key]:
                raise ValueError("Packet and decision differ")
        if decision["status"] != "ready":
            raise ValueError("Decision requires human intervention")
        if policy is not None:
            validate(policy, "policy")
            if policy["policy_id"] != decision["policy_id"]:
                raise ValueError("Dispatch policy differs from the decision")
        for field in ("validation_commands", "escalate_if"):
            if any(value not in packet[field] for value in decision[field]):
                raise ValueError(f"Packet omits decision {field}")
        if sum(item["estimated_tokens"] for item in packet["context"]) > decision[
            "context_budget_tokens"
        ]:
            raise ValueError("Packet context exceeds decision budget")
        for item in packet["context"]:
            if item["project_id"] != packet["project_id"] or item["revision"] != packet[
                "revision"
            ]:
                raise ValueError("Packet context identity differs")
        result = {
            "adapter": "manual",
            "capabilities": deepcopy(self.capabilities),
            "requested_tier": decision["tier"],
            "effective_tier": None,
            "packet": deepcopy(packet),
            "usage": None,
            "status": "awaiting_host_execution",
        }
        if workflow is not None:
            from .workflow import check_workflow
            check_workflow(workflow, project_id=packet["project_id"], task_id=packet["task_id"],
                           revision=packet["revision"], worker=True)
            if "retry" in workflow:
                if policy is None:
                    raise ValueError("Retry dispatch requires the active policy")
                limit = int(policy["max_attempts"])
                if workflow["retry"]["completed_attempts"] >= limit:
                    raise ValueError("Retry attempt limit exhausted")
                result["retry_attempt_limit"] = limit
            result["workflow"] = deepcopy(workflow)
        return result
