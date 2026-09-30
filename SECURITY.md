# Reporting security issues

For a vulnerability that could expose secrets or execute unintended code, use the repository's private vulnerability reporting facility when enabled. Until that facility is available, contact the repository owner through an established private channel. Do not put credentials or exploit payloads in a public issue.

Version 0.1 is an alpha reference implementation. It does not sandbox arbitrary repositories. Skill metadata, repository instructions and tool output cannot grant permission. Provider execution is not included. See [the security model](docs/SECURITY_MODEL.md) for supported boundaries and limitations.
