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

    def prepare(self, packet, decision, workflow=None, policy=None, *, task=None,
                runtime_policy=None, launch=None, host_ack=None):
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
        if runtime_policy is not None:
            from .runtime_controls import host_control_gaps, prepare_execution
            if task is None or launch is None:
                raise ValueError("Runtime dispatch requires task and launch context")
            request = prepare_execution(task, packet, decision, policy, runtime_policy,
                                        launch, workflow)
            gaps = host_control_gaps(request, host_ack)
            result.update(
                execution_request=request, host_acknowledgment=deepcopy(host_ack),
                requested_model=request["requested_model"],
                requested_reasoning=request["requested_reasoning"],
                effective_model=None, effective_reasoning=None, observation=None,
                unavailable_controls=gaps,
                status="blocked_host_controls" if gaps else "awaiting_host_execution",
            )
            validate(result, "runtime_dispatch")
        elif any(value is not None for value in (task, launch, host_ack)):
            raise ValueError("Runtime controls require an explicit runtime policy")
        return result

    def record_execution(self, prepared, observation):
        from .runtime_controls import record_execution
        return record_execution(prepared, observation)
