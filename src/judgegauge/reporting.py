from __future__ import annotations

import html
import json

from .models import CalibrationResult


def _escape_md(text: str) -> str:
    """Escape characters that carry meaning in Markdown.

    Table delimiters (``|``) and inline HTML supplied through model
    identifiers or metric details must not break the table layout.
    """
    text = html.escape(text)
    return text.replace("|", "\\|")


def render_text(result: CalibrationResult) -> str:
    rows = [
        "JudgeGauge 0.1.0",
        f"Model: {result.requested_model}",
        f"Battery: {result.suite}",
        f"Requests: {result.request_count}",
        "",
    ]
    for metric in result.metrics:
        state = "PASS" if metric.passed else "FAIL"
        rows.append(f"{metric.name:<24} {metric.value:>7.3f}  {state}")
    rows.extend(
        [
            "",
            f"Snapshot identity: {result.snapshot_level}",
            f"VERDICT: {result.verdict.value.upper()}",
        ]
    )
    return "\n".join(rows)


def render_json(result: CalibrationResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True)


def render_sarif(result: CalibrationResult) -> str:
    failures = [metric for metric in result.metrics if not metric.passed]
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "JudgeGauge", "version": "0.1.0"}},
                "results": [
                    {
                        "ruleId": metric.name,
                        "level": "error",
                        "message": {
                            "text": f"{metric.name}={metric.value:.3f} failed {metric.comparator} {metric.threshold:.3f}"
                        },
                    }
                    for metric in failures
                ],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_html(result: CalibrationResult) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(metric.name)}</td>"
        f"<td>{metric.value:.3f}</td>"
        f"<td>{html.escape(metric.comparator)} {metric.threshold:.3f}</td>"
        f"<td>{'PASS' if metric.passed else 'FAIL'}</td>"
        "</tr>"
        for metric in result.metrics
    )
    limitations = "".join(f"<li>{html.escape(item)}</li>" for item in result.limitations)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>JudgeGauge report</title>
<style>body{{font:16px system-ui;max-width:900px;margin:3rem auto;padding:0 1rem}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccc;padding:.6rem;text-align:left}}.verdict{{font-size:2rem;font-weight:700}}</style>
</head><body><h1>JudgeGauge calibration report</h1>
<p class="verdict">{result.verdict.value.upper()}</p>
<p>Suite: {html.escape(result.suite)} · Model: {html.escape(result.requested_model)} · Requests: {result.request_count}</p>
<table><thead><tr><th>Metric</th><th>Value</th><th>Gate</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Scope limitations</h2><ul>{limitations}</ul></body></html>"""


def render_markdown(result: CalibrationResult) -> str:
    """Render a Markdown summary suitable for pull-request summaries or issue comments.

    Passed and failed metrics are visually distinct (``PASS`` / ``FAIL`` plus a
    bold/italic marker) without relying only on color. The report is
    deterministic for the same ``CalibrationResult`` and makes no cross-day or
    validity claim.
    """
    header = _escape_md(result.requested_model)
    suite = _escape_md(result.suite)
    lines = [
        f"## JudgeGauge calibration — {header}",
        "",
        f"- **Suite:** {suite}",
        f"- **Requests:** {result.request_count}",
        f"- **Snapshot identity:** {result.snapshot_level}",
        f"- **Valid readouts:** {result.valid_readouts}/{result.request_count}",
        "",
        "### Metrics",
        "",
        "| Metric | Value | Gate | Status |",
        "| --- | ---: | --- | ---: |",
    ]
    for metric in result.metrics:
        name = _escape_md(metric.name)
        comparator = _escape_md(metric.comparator)
        status = "**PASS** ✓" if metric.passed else "**FAIL** ✗"
        lines.append(
            f"| {name} | {metric.value:.3f} | {comparator} {metric.threshold:.3f} | {status} |"
        )
    verdict_text = "PASS" if result.passed else "FAIL"
    lines.extend(
        [
            "",
            f"**Verdict: {verdict_text}**",
            "",
            "### Scope limitations",
            "",
        ]
    )
    for item in result.limitations:
        lines.append(f"- {_escape_md(item)}")
    lines.append("")
    return "\n".join(lines)
