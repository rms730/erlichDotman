# Eight-task orchestration pilot protocol

## Question and unit of comparison

Can a matched, controlled evaluation capture useful differences between ordinary orchestration and ErlichDotman without dropping quality, work legs or human effort? This is a feasibility study, with descriptive results. The allocation unit is one distinct task trial. Four pairs contain eight tasks: one baseline and one treatment per pair. A retry belongs to its original trial.

Choose two comparably scoped held-out tasks in each project/risk stratum. Exclude tasks already solved in supplied chats, nonreproducible external incidents and work requiring live trades, production mutations or changing approval scope. Record exclusions before assignment. Match category, ambiguity, subsystem familiarity and frozen acceptance; document residual mismatch rather than claiming tasks are identical.

## Freeze, randomize and isolate

- Fill every `null` registration field needed to execute or grade. Freeze task specs, starting snapshots including dirty edits, accepted invariants, validator versions/argv, retry/time/spending limits, baseline prompt, treatment skill commit and allowed tools/skills. Save checksums before any run; do not edit graders after seeing results.
- Preserve the same authorization and approval behavior in both arms. The baseline is the actual ordinary workflow, not an exaggerated approval sequence or a weak strawman. Identical measurement instructions apply to both arms.
- Use the same observed effective model/reasoning settings and tool bindings. The treatment adds ErlichDotman's orchestration/context guidance. This isolates that comparison; testing different routing/model choices is a later experiment.
- Assign one task in each pair to each arm using a recorded random seed after freezing the cohort. Independently randomize within-pair execution order, with two pairs baseline-first and two treatment-first. Publish the assignment map privately before execution; no rerolling for favorable assignments.
- Start fresh task/worker sessions and isolated checkouts from the frozen inputs. Keep the other skill catalog constant. Disable ErlichDotman body loading only in baseline trial sessions, or trace and report contamination. Do not globally disable it for ordinary work. Reusing a solved packet or persistent project notes between pair members is a protocol deviation.
- If effective controls or arm isolation cannot be verified, mark the comparison exploratory/uncontrolled. An intended setting is not an observed setting.

## Capture every leg without duplicate accounting

Inventory orchestration, context loading/compaction, implementation workers, checks, independent review, logging, failed attempts, retries and follow-up. Record one entry per actual leg/boundary; multiple legs can share a stage and implementation-attempt number. Number implementation attempts from one without resetting after a handoff. Use distinct leg IDs and link parent/worker traces.

Capture revision/dirty-state evidence, acceptance checks, requested versus observed capability, available incremental usage, wall-clock elapsed time and human minutes. Log control-plane failures and abandoned tasks, not just successful workers. Never reconstruct missing billed usage from context estimates, account quotas or a summary's confidence.

Parent-inclusive usage overlaps worker records. Reconcile unique call IDs or choose a verified nonoverlapping accounting boundary before summing. If that cannot be established, totals stay unknown. A host/self-reported complete flag is a declaration; reconcile it with an expected-leg inventory and trace evidence. Missing entire legs defeat a completeness claim even when every supplied record has numeric usage.

Record trial start/terminal timestamps and each leg's timing boundary. Task end-to-end elapsed time includes waits and retries. Summed stage time is a separate measure and may overlap in parallel work. Human active minutes, approval-wait time and logging effort remain separate; do not infer active effort from a boolean intervention flag. Logging minutes are a subset of human active minutes, not an additional amount to add again.

## Grade and follow up

An independent reviewer receives frozen acceptance, sanitized candidate artifacts and validator evidence without arm names, resource totals, transcripts or suggestive commit messages. Apply identical pass/fail criteria; record any unblinding. Validators alone do not establish product acceptance. A worker's success claim remains separate from this acceptance decision; keep `task_success` unknown until the terminal decision is recorded. Preserve failing acceptance and early-stop outcomes.

At seven days after each terminal trial, check attributable defects and rework with the same definitions in both arms. Record follow-up completeness, reviewer/evidence, actual use or test exposure and correction resources. No follow-up means unknown, not zero defects; absence of reported defects without meaningful observation does not establish durability. Report initial accepted outcomes separately from accepted outcomes retained through completed follow-up. Do not call the study final while that window is pending.

## Report and decide

Report all eight assigned tasks, per-pair differences, acceptance counts, first-pass outcomes, retries, omitted-fact defects, deviations and observation coverage. An incomplete task remains in the assigned-task denominator. Report protocol failures separately from product failures.

Within each arm, tokens/cost per independently accepted outcome use **all** task-leg resources, including failed/incomplete trials and retries. Report initial acceptance with resources through terminal stop, and retained acceptance with resources through the completed seven-day window, including measured follow-up. Do not mix those windows. With no accepted outcomes, incompatible units or incomplete capture, the metric is `null`; disclose observed subtotals and coverage without substituting them for full totals. Report elapsed time and human minutes separately. Do not claim comparable token/dollar savings from partial or unmatched metering.

Four pairs provide no reliable general effect estimate or evidence of noninferiority. Do not tune routing policy from this pilot, select only favorable tasks or compute a confident headline from a noisy ratio. The decision is whether capture, grading and task matching are feasible enough for a larger preregistered study. Stop/revise if binding, acceptance, arm separation or accounting cannot be audited; retain all attempted work in the report.

## Method references

[OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices) supports task-specific tests, logging and calibrated human judgment. [Feasibility-pilot methodology](https://pmc.ncbi.nlm.nih.gov/articles/PMC8849521/) distinguishes process/feasibility questions from efficacy inference. The latter concerns clinical studies; applying its small-pilot caution here is a methodological adaptation, not a validated sample-size rule for coding agents.
