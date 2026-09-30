# Handoff protocol

A packet transfers conclusions and constraints so an implementation agent does not repeat architecture work. It binds task/project IDs and repository revision, tier, objective, rationale, target files/symbols, current/desired behavior, invariants, constraints, notes, tests, argv validators, forbidden changes, escalation triggers, expected output and selected excerpts.

The constructor checks task/project/decision identity, revision-scoped context and context estimates. A `needs_human` decision cannot become a dispatchable packet. Paths are project-relative. Required facts such as tests and invariants must be provided, rather than invented from a short objective.

Use [the template](../skills/erlichdotman/templates/implementation-packet.md) and [the worked example](../examples/README.md). A useful packet answers:

- What observable behavior changes, and why?
- Which files/interfaces carry that behavior?
- Which properties and surfaces must remain unchanged?
- Which deterministic checks accept the patch?
- What evidence should stop the worker and escalate?

Markdown rendering is for a host agent; commands are quoted for display, never executed by the renderer. JSON is canonical and validated. Trust labels remain visible on context so repository instructions are not mistaken for higher-authority instructions.

Evaluate packet formats by running equivalent held-out tasks with full context, compact structured JSON and rendered Markdown. Compare validation success, retries, usage, human review and omitted-fact defects. The first milestone checks required-field preservation and realistic skill behavior; it does not assert that this initial format is optimal.
