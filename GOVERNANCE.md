# Governance

JudgeGauge currently uses a maintainer-led model. Maintainers are responsible for releases, security
responses, measurement semantics, and the fail-closed contract.

## Decision process

Small fixes are decided in pull-request review. Changes to public APIs, default thresholds, metric
definitions, exclusion rules, or report semantics require an issue describing:

1. The downstream claim the change is intended to license.
2. The evidence collected to support that claim.
3. The behavior when evidence is missing or invalid.
4. Migration impact for existing users.

Consensus is preferred. When consensus cannot be reached, the maintainer documents the decision and
its tradeoffs in the issue before merging.

## Becoming a maintainer

Regular contributors may be invited after sustained, technically sound contributions and dependable
review participation. Maintainer access is never required to influence design decisions.

