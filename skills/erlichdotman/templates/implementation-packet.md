# Implementation packet

PROJECT / TASK / REVISION / CAPABILITY TIER

OBJECTIVE: Observable accepted behavior.
WHY: Consequence motivating the change.
FILES / SYMBOLS: Exact project-relative targets and interfaces.
CURRENT → DESIRED: Concrete before/after behavior.
INVARIANTS: Properties that must survive.
CONSTRAINTS: Scope, compatibility, security and dependency limits.
NOTES: Decisions already made upstream, without the reasoning transcript.
TESTS: Normal behavior, edge cases and regression acceptance.
VALIDATION: Commands as argv arrays; authorization stays with the host.
DO NOT CHANGE: Surfaces explicitly excluded.
ESCALATE IF: Missing facts, contradicting evidence, failed checks or permission needs.
EXPECTED OUTPUT: Patch, checks, unresolved issues and available usage.
CONTEXT: Minimum required excerpts, each with project/revision/provenance/estimate.

Use the version 1 JSON contract when the CLI is available. Do not fill unknown facts with plausible guesses. This initial format needs measured comparison with other formats before claiming optimal compression.
