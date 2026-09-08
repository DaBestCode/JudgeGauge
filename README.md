# JudgeGauge

**JudgeGauge is a fail-closed calibration gate for teams using LLMs as judges, preventing expensive evaluations from running when the judge itself is too unstable to support the intended conclusion.**

> [!IMPORTANT]
> Terminal recording coming before the first public release. It will show installation, a failed gate, and the generated HTML report.

## 60-Second Quickstart

JudgeGauge currently supports an OpenAI-compatible Chat Completions endpoint and reads `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_BASE_URL`. The model defaults to `gpt-5-mini` and the base URL defaults to OpenAI's API.

```bash
pip install judgegauge
judgegauge gate --smoke
```

Or use the Python API with any callable that follows the `Judge` protocol:

```python
import judgegauge

judgegauge.calibrate().require()
```

The bounded smoke suite makes nine requests and measures same-window repeat ranking, candidate-order sensitivity, and invalid readouts. It does **not** certify cross-day stability, correctness, or agreement with humans.

## Reports

```bash
judgegauge gate --smoke --format json --output judgegauge.json
judgegauge gate --smoke --format sarif --output judgegauge.sarif
judgegauge gate --smoke --format html --output judgegauge.html
```

Exit `0` means the frozen smoke gates passed, `1` means calibration completed but failed, and `2` means the gate could not be evaluated. Unparseable readouts fail closed.

## Old Way vs. JudgeGauge

| Concern | Old Way / Fragile DIY | Using JudgeGauge |
|---|---|---|
| Repeatability | Assume temperature zero is deterministic | Measure repeated rankings in the current window |
| Position bias | Shuffle candidates informally | Run paired exact-order reversals |
| Invalid output | Retry until parsing succeeds | Retain invalid readouts as gate failures |
| Model identity | Log only the requested model | Record requested and response-side model identifiers |
| CI behavior | Discover instability after the full evaluation | Exit non-zero before downstream work |
| Reporting | Mix API health with scientific validity | State the verdict and its scope limits separately |

## Why This Exists

A preregistered audit of 52,988 request attempts reported same-window repeat rankings at Spearman `0.400` against a required `0.90`, and byte-identical next-day replay agreement of `0.78` against `0.99`, despite clean delivery, schema validity, and request hashes. Its practical conclusion is narrow: a model name on a shared endpoint is not automatically a frozen measurement instrument.

Read [Clean Engineering, Unstable Measurement](https://arxiv.org/abs/2609.04198).

JudgeGauge is an independent implementation inspired by the paper. It is not affiliated with or endorsed by the paper's authors.

## Current Scope

Version `0.1.0` is the first vertical slice:

- Built-in same-window smoke suite
- OpenAI-compatible Chat Completions adapter
- Custom Python judge protocol
- Text, JSON, SARIF, and standalone HTML reports
- Fail-closed CLI exit codes

Cross-day sealed baselines, framework adapters, GitHub Actions packaging, richer provenance logs, and statistically calibrated task-specific batteries remain roadmap work.

## Development

```bash
python -m pip install -e '.[dev]'
python -m unittest discover -s tests
ruff check .
```

## License

Apache-2.0
