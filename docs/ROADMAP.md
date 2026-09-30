# Roadmap

1. **Measure one real runtime.** Implement an opt-in adapter exposing actual model selection, reasoning controls, complete usage and latency. Run repeated held-out engineering tasks against a frozen frontier baseline. Evaluate both quality and total cost; include planning/review/retry legs and intervention time.
2. **Test compressed handoffs.** Compare full context, structured packet and rendered packet on unfamiliar and multi-file tasks. Measure omitted-fact defects, first pass, retries and usage. Add dirty-tree fingerprinting for reusable profiles.
3. **Calibrate reviewable policy.** Use sufficient measured samples to propose category/project routing changes. Require evidence that weaker routes preserve acceptance and rework quality. Keep deployment of recommendations explicit.

Later, only if evidence justifies it: SWE-bench runner integration, trusted skill-source recommendations, host-specific discovery adapters, durable scheduling across projects, availability fallback, price catalogs and learned expected-total-cost models. No opaque self-modification, silent installations or unmeasured savings claims.
