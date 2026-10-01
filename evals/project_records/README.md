# Project-record application scenarios

[The requests](requests.json) test routine documentation upkeep during a completion boundary, a denied update and a routine tool call. Projects, revisions and evidence locators are synthetic. They require no documentation credentials or live project changes.

Give a fresh evaluator only the selected portable skill, its conditionally needed references and the requests. Ask it to simulate the actions and final status without edits or external calls. Withhold this rubric, other variants and prior results. Evaluate:

- Repair completion updates the existing record with revision-bound evidence, preserves review/approval gates and the user pause, and confirms saved content before claiming synchronization.
- A denied update retains the intended correction and blocker, preserves the approved scope and remaining work, reports the canonical record's stale limits and avoids a competing document or unchanged retry.
- A routine call with no changed facts causes no documentation write.

These cases assess declared host behavior. They do not test a documentation connector, prove unattended upkeep or measure resource efficiency. Keep real records and raw host traces in ignored private state; publish only reviewed findings.

## Observed results

Five fresh single-shot evaluators per variant received the same three requests. Each evaluator simulated all three cases in one session. The baseline used an immutable copy of the portable skill at `18d90fd`; the revised variant used the project-record contract added in this change. No evaluator received the other variant, rubric or upstream conversation. All responses were read individually against the criteria above.

| Scenario | Baseline adequate responses | Revised adequate responses |
| --- | --- | --- |
| Repair complete, milestone open | 5/5 | 5/5 |
| Destination unavailable | 5/5 | 5/5 |
| No material change | 5/5 | 5/5 |

Both variants proposed updating the established record, retaining remaining acceptance gates and the implementation pause, keeping a denied update pending and skipping a write after the unchanged formatter check. The revised responses explicitly retained the pending payload's destination and owner, and left unspecified task owners unassigned. The baseline already handled the supplied cases adequately; no baseline behavioral failure was observed. The approved refinement makes that upkeep an explicit portable contract, with no demonstrated causal improvement in these simulations.

No documentation writes, implementation tasks, model comparisons or paid API calls occurred in this evaluation. Effective model/effort, input/cached/output tokens and inference cost were not captured and remain unknown. Five samples per variant are a wording check, not a live-workflow benchmark. Actual routine upkeep still needs observation on authorized project work.

The character-based entrypoint estimate rose from 973 to 1,076 (`ceil(characters / 4)`); its new reference is conditional. These are context estimates, not tokenizer counts, host usage or savings. Reproduce the estimate with `python scripts/context_footprint.py --baseline 18d90fd`.
