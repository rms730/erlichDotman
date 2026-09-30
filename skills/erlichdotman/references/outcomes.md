# Outcome boundary

Record observed acceptance, failed checks and available runtime usage in an external trace. Include planning, worker, retry and review legs when the host can measure them. Unavailable values stay unknown; context estimates cannot become billed usage.

Send workers only the findings needed for their next attempt, not raw logs or comparison history. Keep private traces in host-local ignored state.

Detailed telemetry contracts, aggregation, benchmark design and routing calibration are separate evaluation work. Consult the current host tooling/contracts for that work; do not load datasets or research during an ordinary implementation handoff.
