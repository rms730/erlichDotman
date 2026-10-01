# Project communication

## Project color coding

Keep a private mapping from stable project identity to `label`, `color` and `emoji`. The readable label is required, including when a color or emoji is shown. Reuse the entry across progress, failures, successes, pauses, resumes and handoffs; status changes belong in words and do not change the project's marker. User preferences and host palettes configure the mapping; public examples define no mandatory palette.

At project binding, load its existing entry. When no entry exists and the host supports colored emoji, choose a distinct available marker from the configured host palette and persist the new entry in authorized private preferences or ignored host-local state. Preserve other entries. If no palette preference is specified, choose a host-supported marker once for this private mapping. If the configured palette has no distinct available marker, use the plain label and keep assignment pending until the user supplies or approves one. Resolve ambiguous project identity or conflicting explicit preferences before assigning. Confirm persistence before claiming the assignment will carry forward; if persistence is unavailable or fails, use the plain project label and retain the intended assignment as pending.

Carry only the relevant project's mapping in a handoff that needs user-facing updates. An intentional remapping follows the user's decision; avoid silent reassignment or changing every project when one is added.

The skill controls the message prefix through the host's text delivery. Bubble styling and emoji rendering belong to the host; the core/manual adapter exposes no bubble-color control. On a plain-text or emoji/color-unsupported host, begin with the readable label, retaining the private mapping for capable hosts. Color alone never identifies the project or conveys acceptance.

For example, a fictional mapping may assign Maple blue/`🔵` and Cedar orange/`🟠`. Updates begin `🔵 Maple:` or `🟠 Cedar:`. The plain-text fallback is `Maple:` or `Cedar:`. Actual user/project mappings remain private; this host-managed configuration is not a new field in the CLI's project schema.

## Status messages

Use this shape for a project update or status answer:

1. Begin with the stable configured colored marker and readable project label, followed by the current outcome or uncertainty. Use the plain label when no persisted mapping is available or the host cannot display the marker.
2. State the next milestone gate, remaining task or blocker and the responsible owner when known. Keep each message about one project. For a multiple-project request, send separate project messages through the host's supported conversation delivery, preserving the requested coverage and existing channel permissions.
3. Give the relevant evidence/freshness limit and next targeted check when it changes the reader's decision. A label does not establish current state.

Before answering status, read the latest authoritative project record and available current owner outcome. Match their project, revision and relevant dirty state when supplied. Cached conversation summaries identify what to check; they do not establish that an old blocker still exists. Attribute a reported outcome when its underlying evidence has not been checked independently.

If a newer owner outcome resolves an old blocker, report that current outcome and its remaining acceptance gates. Reconcile a lagging canonical record under the [project-record contract](project-records.md); keep an unsaved update pending. If current sources conflict or are unavailable, state the last verified date/revision or supplied freshness, what remains uncertain, and the smallest record section, owner outcome or decisive evidence needed to resolve it. A status question triggers that focused refresh, not a broad repository re-audit or speculative replay of a resolved defect.

For a fictional update: `🔵 Maple: Owner reports preview validation passed at maple-r9; independent review remains pending with review-owner.` If current evidence is unavailable: `🟠 Cedar: Current status is unverified. The last confirmed record was from the previous day; the next check is today's review-owner outcome.` Keep these examples' names as text on unsupported hosts.
