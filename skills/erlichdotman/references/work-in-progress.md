# Competing work

Use the host/user's chosen work-in-progress limit; do not invent a universal limit. When new work competes, state the priority decision and the resulting active, paused or displaced tasks. Do not multiply workers automatically. If priority is already explicit, proceed within it; ask only when an unresolved tradeoff materially changes requested priority or scope.

Before pausing/displacing a task, retain its project/revision and dirty state, acceptance, evidence, unresolved blocker and next concrete step. Keep a locator to this continuation in private orchestrator state. Refresh it before resuming. Confirm running work has actually stopped or reached a safe checkpoint before counting the capacity as free; a written pause is not a stopped worker.

Keep the multi-project inventory with the orchestrator. A worker receives only its own task's priority, rules and relevant facts. The optional workflow checker can validate a supplied before/after inventory and chosen limit; it cannot discover omitted workers, pause them or decide user priority.
