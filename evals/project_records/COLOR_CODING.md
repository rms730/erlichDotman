# Project color-coding application checks

[Requests](color-coding-requests.json) and [state](color-coding-state.json) are synthetic. They cover a stable configured marker across a failure and later success, a new project's private mapping, and a plain-text host. Real project assignments remain private.

Give a fresh evaluator only the chosen portable skill, its conditionally needed references and these two files. Request exact outgoing messages, intended private configuration actions and minimal reads. Withhold this rubric, other skill variants and upstream conversation. Check:

- Each message begins with the configured marker and readable project label, covering one project. A status change leaves its mapping unchanged.
- With authorized persistence and a supplied palette, an unconfigured project receives an available distinct marker. The intended private write preserves other entries, and the same assignment is reused on resume.
- A plain-text host receives the readable label and keeps its private mapping for capable hosts. Responses claim no message-bubble styling control.
- Current supplied record/owner outcomes determine status. Reported checks remain attributed, and outstanding acceptance gates remain visible.
- Reads stay scoped. Proposed private writes are distinguished from actual persistence.

## Observations

Five fresh single-shot evaluators per variant each simulated all three requests in one session. The baseline portable skill was frozen at `4d8a4aa`; the refined variant added the explicit color-coding contract. Evaluators received neither the other variant, this rubric nor upstream conversation. Each response was inspected individually.

| Behavior | Baseline | Refined |
| --- | --- | --- |
| Configured marker and readable label stable across outcomes | 5/5 | 5/5 |
| New private assignment proposed and reused, preserving other entries | 4/5 | 5/5 |
| Plain-label fallback retains the mapping and claims no bubble control | 5/5 | 5/5 |

One baseline evaluator used `Spruce:` for both new-project updates and proposed no mapping. That followed the old contract's plain-name fallback; initial assignment was not yet required. All refined evaluators proposed the supplied unused purple/`🟣` entry, conditioned its use on confirming persistence, and described the plain-label fallback if saving failed. Existing marker stability and unsupported-host handling were already adequate in the baseline.

These are small instruction application simulations. No live message delivery, actual preference persistence, UI controls, project work, provider API trials or remote CI were exercised by these cases. Effective model/effort, input/cached/output tokens and cost remain unknown; host-agent usage was not metered. The results establish neither causal engineering improvement nor resource savings.

The supplied records and owner outcomes agree at their stated boundaries. Conflicting identities/preferences, palette exhaustion, failed persistence and live handoffs remain unexecuted coverage; the guidance describes their safe fallback. The skill is a host instruction contract, not a runtime UI or configuration loader.

The entrypoint's character-based estimate is 1,238 versus 1,185 at `4d8a4aa`, using `ceil(characters / 4)`. This is neither tokenizer output nor billed usage. Detailed communication guidance remains conditional.
