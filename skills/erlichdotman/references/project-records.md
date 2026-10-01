# Routine project upkeep

The end-to-end owner maintains one canonical project record as part of authorized work, without waiting for reminders. Locate the existing record and documentation destination from user preferences or host project configuration at binding/resumption. Reuse it; create one only when none exists and the destination is authorized. Resolve a materially ambiguous destination with the user while continuing independent work. Keep the locator in private orchestrator state.

## Record contract

| Field | Required content |
| --- | --- |
| Binding and freshness | Project/repository, current revision and relevant dirty changes; the evidence checked and last confirmed record update. Unverified facts stay explicit. |
| Next meaningful milestone | The next observable outcome useful to the user, with acceptance criteria, current acceptance state and remaining gates. A green component check completes only its own criterion. |
| Ordered remaining tasks | Stable task identities in execution order, each with objective, owner, status, dependencies and acceptance check. Use `unassigned` for an unknown owner. Retain completed/cancelled outcomes compactly with evidence or the scope decision. |
| Blockers and continuation | What is blocked, who can resolve it, the needed evidence/decision and the next concrete step. Preserve paused/displaced work and user priority/scope decisions. |
| Acceptance evidence | Relevant check result and locator bound to the checked revision/dirty state; failed, unchecked and intentionally excluded criteria remain visible. |

Tasks may live in linked tickets; the canonical record keeps their order, status and acceptance coherent. A dated view or chat update links back to that record. Do not create competing status documents for each phase or worker.

Use [project communication](communication.md) for user-facing status: identify the project first and check current record/owner evidence before reusing a cached status.

## Update boundary

Reconcile the record when scope, priority, milestone, task/owner/status/dependency, blocker, acceptance evidence or a user decision materially changes. Also reconcile before handoff, pause/resume and completion. Preserve still-valid criteria and decisions; update the changed facts rather than rewriting the history. Routine tool calls with no changed facts need no write. Batch related changes at the next meaningful boundary.

For example, a parser repair can finish with revision-bound regression evidence while the milestone remains open for independent review and approval. Mark the repair complete, expose review as the next task, retain the approval dependency and the user's implementation pause, then confirm the saved record.

Use the configured documentation tool and its selected skill for mechanics; a Pages destination uses the existing Pages skill. This contract requires no vendor, scheduler or polling. It grants no installation, access, publication or messaging authority. The CLI/manual adapter does not update documentation.

Confirm persisted content by readback or an authoritative saved-content response before claiming the record is current. If access or a write fails, keep the intended update, destination, blocker and next recovery step in private continuation state; report synchronization pending and the last confirmed record's limits. Retry only with a credible remedy within existing authority. A local pending payload is not a second canonical record. At handoff, name the owner responsible for applying it and carry only the relevant milestone/task facts to the worker.
