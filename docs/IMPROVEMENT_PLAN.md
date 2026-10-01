# Evidence-driven improvements — 2026-09-30

The assessment establishes useful engineering outcomes consistent with ErlichDotman, not its incremental contribution or resource savings. Preserve the compact runtime skill, current isolation/validation code and existing permissions. Improve evidence before adding machinery or changing routing defaults. This plan owns priorities and exit criteria; the [pilot protocol](../evals/pilot/PROTOCOL.md) owns experimental details.

## 1. Establish fresh binding and a complete stage ledger

Start with one already-authorized small task. A registry is a locator: produce a project profile grounded in its actual repository, branch, revision, relevant dirty edits, current objective, applicable instructions and acceptance commands. Recheck at each dispatch/reuse boundary. A discovered repository root alone is not a validated profile.

Use the [stage-entry template](../evals/pilot/stage-entry.template.json) at meaningful work boundaries, not on every sentence or tool result. Multiple worker/review legs may share a stage/attempt; give each a distinct ID. Do not reread the skill or reopen an approval process merely to write a record. Capture logging effort as part of the task's resources.

**Deliverable:** one private ledger reconciled to actual host/task traces, with an inventory of expected legs and known omissions. Missing usage and observed capability remain `null`.

**Exit criteria:** identity/attempt order is consistent; required acceptance facts survive handoffs; parent/worker usage is not double-counted; requested and effective settings are distinct; missing records are visible; elapsed versus summed stage time and human minutes are separate. Record whether context reads and completeness were observed, self-reported or unknown.

**Next implementation increment:** a versioned optional stage-evidence contract and append/validate/report tooling. Keep existing version-1 telemetry backward compatible. It lacks fresh binding and nullable effective-tier fields; do not silently relabel its `tier` or pass the pilot template to the current `summary` command. Add behavior tests for missing legs, unknown settings, duplicate usage, retry gaps and parent/worker overlap before extending aggregation. Automate only fields a real host sample supports.

## 2. Run a feasibility pilot, then seven-day follow-up

Use the [preregistration template](../evals/pilot/preregistration.template.json). Select eight distinct held-out tasks, two comparable tasks per project/risk stratum. Assign one baseline and one ErlichDotman task in each pair after freezing the tasks. Eight means eight initial task trials; retries add execution legs, not new tasks. This is not eight tasks executed twice.

The baseline must be the operator's frozen ordinary workflow, not a deliberately weak agent or an artificially costly frontier-only comparator. Use the same effective model/settings, other skills, tools, validators and authorized scope in both arms. Isolate task sessions and prevent implicit ErlichDotman loading in the baseline; report deviations if the host cannot enforce or observe that boundary.

**Deliverable:** a frozen manifest, complete attempted-task ledger, blinded independent acceptance decisions, descriptive matched-pair results and seven-day follow-up with explicit coverage.

**Exit criteria:** all eight assigned tasks appear, including aborted/incomplete tasks; comparison denominators include every captured leg; acceptance and rework are reported separately; unknown metering blocks token/dollar claims; protocol deviations and capture overhead are disclosed. Do not stop after favorable results or silently replace a difficult task.

This pilot checks whether the evaluation can run reliably. It can suggest follow-up hypotheses; four pairs cannot justify universal efficiency claims, a learned router or noninferiority. Fixed-model results cannot demonstrate savings from model switching.

## 3. Make status useful without duplicating technical truth

Use [the status template](../evals/pilot/STATUS_PAGE.template.md) for a user-facing Page when a destination is chosen. Each status needs an as-of time, independently observed versus host-reported evidence, a repository/commit/test reference, remaining gates and next action. Keep reproducible commands, validators, logs and manifests in repository records/private ignored state. Link to them instead of copying their contents.

**Exit criteria:** an unknown/not-observed state is explicit; partial validation does not read as release readiness; newer evidence supersedes dated summaries; private source permissions are respected. A Page is a view of evidence, never an acceptance grader or worker-context preload. No Page publication or recurring schedule is created by this plan.

## 4. Invest in one host integration, then a routing experiment

Choose the smallest collector/adapter justified by the observed host sample. Capture effective model/reasoning settings and usage only from supported per-run sources. Account-wide quota changes are not task metering. Keep manual dispatch available and require no provider dependency for ordinary use.

**Exit criteria:** contract tests preserve unknowns, distinguish requested/effective controls, reconcile all usage IDs once, handle partial failure and do not grant execution permissions. A paid/external runtime experiment needs specified tasks, host access and spending limits; absent those, prepare the experiment without launching it.

Only then design a separate routing comparison with a fixed available model menu and pricing basis, where policies may choose different tiers. Use held-out repeats, risk strata, independently accepted outcomes and rework; determine sample size from the decision and acceptable uncertainty, not from four noisy pilot differences. Keep policy recommendations reviewable and require evidence for downgrades.

## Prepared now and still outstanding

Prepared: a scoped roadmap, experimental protocol, draft preregistration, lightweight stage-record template and status template. These are optional evaluation artifacts, not a running collector, a frozen real-task manifest or completed trial evidence. The core runtime skill and production routing defaults are unchanged.

Still needed: a real host trace and reconciliation; implemented stage-ledger validation/capture; eight eligible tasks with frozen acceptance/budgets; controlled sessions and an independent grader; seven-day follow-up. Read-only discovery can repair private registry hints, but it does not meet these evidence gates by itself.
