# Project communication application checks

[Requests](communication-requests.json) and [state](communication-state.json) are synthetic. They test two-project status delivery, a cached blocker resolved by current evidence, and unavailable current state. The supplied dates/freshness, project names, markers and evidence locators are fictional; real preferences and records remain private.

Give a fresh evaluator only the chosen portable skill, its conditionally needed references and these two files. Ask for proposed host reads and outbound messages with explicit boundaries. Withhold this rubric and other variants. Check:

- Every project message starts with its configured marker/name; an unconfigured project uses its name. Multiple projects receive separate messages without losing requested coverage.
- Status reads use the current canonical record and available owner outcome. A resolved cached blocker is not repeated as current; outstanding milestone gates remain visible.
- Unavailable current state is identified as uncertain, with the last confirmed freshness/revision and a targeted next check. Reported validation is not presented as independently checked evidence.
- Reads remain scoped to the relevant record/owner outcome rather than a broad repository audit. Delivery grants no extra channel or recipient authority.

## Observations

Five fresh single-shot evaluators per variant each simulated all three requests in one session. Baseline artifacts were frozen at `f4e3fb3`; the refined variant included the communication reference. Evaluators received neither the other variant, this rubric nor upstream conversation. Each proposed response was read individually.

| Behavior | Baseline | Refined |
| --- | --- | --- |
| Separate project messages with requested coverage | 5/5 | 5/5 |
| Current evidence supersedes resolved cached blocker | 5/5 | 5/5 |
| Unknown current state remains dated/unverified with targeted refresh | 5/5 | 5/5 |
| Project name first in the unavailable-state reply | 3/5 | 5/5 |

Two baseline replies began with `I can't confirm Cedar's current status` rather than the project name. All refined replies began with `Cedar:` and retained the uncertainty. Freshness and separate-message handling were already adequate in the baseline. The refined responses attributed reported validation to the owner when the underlying artifact had not been independently checked.

These are small instruction application simulations, not measured live delivery, model comparisons or causal engineering-quality evidence. No live project reads, documentation writes, provider API trials or remote CI were run for these cases. Effective model/effort, input/cached/output tokens and cost remain unknown; host-agent usage was not metered. No resource savings are asserted.

The multiple-project case assumes the host supports separate conversation messages. Current record/outcome revisions match in the resolved-blocker fixture; lagging canonical records and conflicting revisions remain follow-up coverage. Independent review accepted the contract without reproducing the evaluator responses.

The entrypoint's character-based estimate is 1,185 versus 1,076 at `f4e3fb3`, using `ceil(characters / 4)`; this is neither tokenizer output nor billed usage. The communication reference remains conditional.
