# Roadmap

The roadmap is ordered by evidence value, not feature count. Items move only when their public claim
and keyless verification strategy are defined.

## 0.1 — Same-window preflight

- [x] Built-in repeatability and candidate-order smoke suite
- [x] Fail-closed Python API and CLI
- [x] Text, JSON, SARIF, and HTML reports
- [x] OpenAI-compatible Chat Completions adapter
- [x] Reusable GitHub Action
- [ ] Mocked HTTP compatibility matrix and opt-in live validation
- [ ] Versioned JSON result schema

## 0.2 — Auditable baselines

- [ ] Append-only event ledger with credential-safe request and response hashes
- [ ] Sealed baseline creation and strict-prefix resume
- [ ] Cross-window and cross-day byte-identical replay
- [ ] Snapshot-identity reporting at L0, L1, and L2
- [ ] Cost and excluded-run ledgers

## 0.3 — Task-specific calibration

- [ ] User-supplied calibration batteries
- [ ] Noise-floor and candidate-gap distributions
- [ ] Informative-pair conditioning with frozen exclusion rules
- [ ] Continuous equivalence bands
- [ ] Gate operating-characteristic simulation before threshold freeze

## Integrations

Ragas, DeepEval, and LangSmith adapters follow the core measurement work. An adapter must preserve
candidate order, invalid readouts, raw evidence hashes, and downstream blocking semantics.

## Non-goals before 1.0

- Provider leaderboards from single runs
- Claims that reliability establishes correctness or human validity
- Silent retries or post-hoc threshold movement
- A hosted service that stores customer prompts or judge responses

