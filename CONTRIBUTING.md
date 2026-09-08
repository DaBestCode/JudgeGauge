# Contributing to JudgeGauge

JudgeGauge treats measurement semantics as part of its public API. Before proposing a change,
describe which claim the new metric or gate is intended to license and which evidence it records.

## Local checks

```bash
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Tests must not require paid API calls. Provider behavior should be covered with recorded, redacted
fixtures or local fakes. Never commit credentials or raw headers that may contain credentials.

Keep execution-integrity failures separate from reliability verdicts. Invalid readouts must fail
closed; a new parser, adapter, or report must not silently turn missing evidence into a pass.
