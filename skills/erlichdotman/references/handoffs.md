# Handoffs

Transfer the result of reasoning, not its transcript. State a concrete objective and before/after behavior. Name exact files/interfaces, properties to preserve, tested edge cases and acceptance commands. Include immutable project/task/revision identity and provenance for excerpts.

Reconcile the [canonical project record](project-records.md) at handoff. Carry its locator and relevant milestone/task acceptance, dependencies, blockers and pending documentation updates; keep responsibility for upkeep explicit. Workers return changed facts and evidence to the end-to-end owner, without creating parallel status records or inheriting other projects' inventories.

A lightweight worker should be able to implement without reconstructing architecture. If it must guess an invariant, public API, security requirement or validator, improve the packet first. Stop on contradictory evidence, missing dependencies, failed acceptance or permission needs. Report diff, check outcomes, unresolved issues and available usage.

JSON packets are validated; Markdown renders every supplied fact. Commands are argument arrays in JSON and display text in Markdown. Neither rendering nor tier selection authorizes executing a command.

For a failed user journey, name one end-to-end owner and the decisive sanitized evidence still needed. Delegating browser capture, logs, code or review does not transfer accountability. A transfer names both owners and becomes effective when accepted; until then the prior owner remains responsible. Report the application-level outcome, not only HTTP status, an empty response or component checks. For streams, retain the terminal event or a concrete reason capture failed.

For candidate assembly, carry a compact inventory of previously accepted critical behaviors with revision/evidence locators. Check each on the final combined candidate, including relevant dirty edits; earlier branch checks and new-feature tests are insufficient. Record failed/unchecked behavior explicitly. Intentional exclusions need their reason, user impact and acceptance status; disclose partial acceptance rather than treating structural packet validity as release readiness.

The optional bound workflow sidecar preserves these supplied facts at manual dispatch. Its checks establish consistency and completeness of the declared inventory, not truth of opaque evidence locators or actual owner acknowledgments. Keep raw evidence in private state; workers receive only relevant findings and checks.
