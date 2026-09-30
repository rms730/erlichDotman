# Context management

[Context ownership](CONTEXT_ARCHITECTURE.md) defines which entrypoint each agent loads. This document explains the implementation and freshness limits; it is optional, not an additional default prompt.

Context is an explicit manifest of excerpts, not an invitation to read the repository. Each item carries project identity, repository revision, provenance, an estimate and a required/optional flag. Each project profile carries its repository, branch, revision, stack, compact architecture, constraints, decisions, validation commands and skill locations.

Selection rejects mixed project IDs, stale revisions and duplicate item IDs. Required excerpts must fit before optional context is selected. If a required item exceeds the budget, stop and ask the host to narrow scope or expand the budget from evidence. Never truncate invariants or quietly omit the relevant interface to save tokens.

Budgets are token estimates, not billed counts or context-window guarantees. The caller supplies estimates for excerpts; the skill uses a rough estimate only when no tokenizer is available. A host must reserve room for skill instructions, packet prose, responses and tool output separately. Check the actual provider context limit in a future provider adapter.

Reusable profiles are revision-bound snapshots. `load_project` checks the supplied repository/revision against the profile; the caller must obtain the current revision from repository truth. A Git commit ID does not capture dirty working-tree edits: include a content hash or mark the snapshot stale whenever relevant files change. Do not reuse architecture summaries after a changed interface merely because HEAD is unchanged.

Keep local profiles and traces under ignored `.cascade/`. Public examples are synthetic. Relative paths must stay within the project after symlink resolution when reading repository content. Path confinement prevents accidental cross-project reads; it does not sandbox processes or neutralize prompt injection inside allowed files.

Expand context when a missing symbol, failed validation, contradictory evidence or dependency edge demonstrates need. Record which excerpts were included so another attempt can avoid rereading them blindly. Separate projects even when two repositories use the same symbols or task IDs.

User-requested reuse of a generic pattern is possible: verify and restate the pattern against the target repository before handoff, retaining target identity and constraints. Do not send the source project's history as target context. Dispatch budget failures do not prevent independent preparation.
