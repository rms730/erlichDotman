# Handoffs

Transfer the result of reasoning, not its transcript. State a concrete objective and before/after behavior. Name exact files/interfaces, properties to preserve, tested edge cases and acceptance commands. Include immutable project/task/revision identity and provenance for excerpts.

Reconcile the [canonical project record](project-records.md) at handoff. Carry its locator and relevant milestone/task acceptance, dependencies, blockers and pending documentation updates; keep responsibility for upkeep explicit. Workers return changed facts and evidence to the end-to-end owner, without creating parallel status records or inheriting other projects' inventories.

A lightweight worker should be able to implement without reconstructing architecture. If it must guess an invariant, public API, security requirement or validator, improve the packet first. Stop on contradictory evidence, missing dependencies, failed acceptance or permission needs. Report diff, check outcomes, unresolved issues and available usage.

JSON packets are validated; Markdown renders every supplied fact. Commands are argument arrays in JSON and display text in Markdown. Neither rendering nor tier selection authorizes executing a command.

For a failed user journey, name one end-to-end owner and the decisive sanitized evidence still needed. Delegating browser capture, logs, code or review does not transfer accountability. A transfer names both owners and becomes effective when accepted; until then the prior owner remains responsible. Report the application-level outcome, not only HTTP status, an empty response or component checks. For streams, retain the terminal event or a concrete reason capture failed.

For candidate assembly, carry a compact inventory of previously accepted critical behaviors with revision/evidence locators. Check each on the final combined candidate, including relevant dirty edits; earlier branch checks and new-feature tests are insufficient. Record failed/unchecked behavior explicitly. Intentional exclusions need their reason, user impact and acceptance status; disclose partial acceptance rather than treating structural packet validity as release readiness.

The optional bound workflow sidecar preserves these supplied facts at manual dispatch. Its checks establish consistency and completeness of the declared inventory, not truth of opaque evidence locators or actual owner acknowledgments. Keep raw evidence in private state; workers receive only relevant findings and checks.

## Milestone threads

Keep one accountable owner through a coherent milestone's implementation, review and acceptance. Start a fresh thread at a completed milestone or major scope change when it improves organization. Do not rotate by message count or abandon an unfinished acceptance gate.

The compact handoff carries the exact revision and relevant dirty state, preserved decisions, test results/evidence, open defects, next acceptance criteria, canonical-record locator and responsible owner. Read that record and current source on resumption; transfer the required conclusions rather than a full transcript. The prior owner remains responsible until a transfer is accepted.

Prefer the relevant project folder through supported host project/thread placement APIs, then verify actual project membership from host metadata. A working directory or title alone does not assign a thread. If placement or verification is unavailable, disclose it and retain one owner, preparing a handoff at a safe checkpoint. Never launch duplicate concurrent implementation to obtain a new thread, and do not force migration of running tasks.

Shorter threads do not guarantee token savings. Count compaction, cache reuse, reconstruction, parent/review work and human effort when comparing accepted outcomes.
