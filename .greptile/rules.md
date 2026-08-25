# assinstants — code review rules

Greptile: apply these product-specific rules in addition to general correctness and
security review. This file is owned by this repo. Cost and behaviour settings live in
`greptile.json`, which is generated from algominds-ai/algominds-standards.

Style, formatting and copy rules are enforced by Biome and check-copy-rules.sh in CI.
Do not comment on them here.

## What this service is

TODO: one paragraph. What it does, who uses it, what breaking it costs.

## Rules that outrank convenience

TODO: the things that must never regress. Sending suppression, auth, billing, tenancy.
