import json
import unittest

import judgegauge
from judgegauge.models import JudgeResponse
from judgegauge.reporting import (
    render_html,
    render_json,
    render_markdown,
    render_sarif,
    render_text,
)


class StableJudge:
    model = "test-model"

    def __call__(self, case, candidates):
        return JudgeResponse(
            ranking=tuple(candidate.id for candidate in case.candidates),
            scores={candidate.id: float(index) for index, candidate in enumerate(case.candidates)},
            model=self.model,
        )


class ReportingTests(unittest.TestCase):
    def test_all_report_formats_are_renderable(self):
        result = judgegauge.calibrate(StableJudge())

        self.assertIn("VERDICT: PASS", render_text(result))
        self.assertEqual(json.loads(render_json(result))["verdict"], "pass")
        self.assertEqual(json.loads(render_sarif(result))["version"], "2.1.0")
        self.assertIn("<title>JudgeGauge report</title>", render_html(result))

    def test_markdown_contains_verdict(self):
        result = judgegauge.calibrate(StableJudge())
        md = render_markdown(result)
        self.assertIn("**Verdict: PASS**", md)

    def test_markdown_contains_metric_table(self):
        result = judgegauge.calibrate(StableJudge())
        md = render_markdown(result)
        self.assertIn("| Metric | Value | Gate | Status |", md)
        self.assertIn("| --- | ---: | --- | ---: |", md)
        for metric in result.metrics:
            self.assertIn(metric.name, md)

    def test_markdown_contains_limitations(self):
        result = judgegauge.calibrate(StableJudge())
        md = render_markdown(result)
        self.assertIn("### Scope limitations", md)
        for item in result.limitations:
            self.assertIn(item, md)

    def test_markdown_is_deterministic(self):
        result = judgegauge.calibrate(StableJudge())
        self.assertEqual(render_markdown(result), render_markdown(result))

    def test_markdown_escapes_table_delimiters(self):
        result = judgegauge.calibrate(StableJudge())
        result = result.__class__(
            verdict=result.verdict,
            metrics=result.metrics,
            request_count=result.request_count,
            valid_readouts=result.valid_readouts,
            invalid_readouts=result.invalid_readouts,
            requested_model="provider|model",
            response_models=result.response_models,
            snapshot_level=result.snapshot_level,
            suite=result.suite,
            limitations=result.limitations,
        )
        md = render_markdown(result)
        self.assertIn("provider\\|model", md)

    def test_markdown_distinguishes_pass_fail(self):
        result = judgegauge.calibrate(StableJudge())
        md = render_markdown(result)
        self.assertTrue(
            "**PASS** ✓" in md or "**FAIL** ✗" in md,
            "Markdown should contain visual pass/fail markers",
        )


if __name__ == "__main__":
    unittest.main()
