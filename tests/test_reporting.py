import json
import unittest

import judgegauge
from judgegauge.models import JudgeResponse
from judgegauge.reporting import render_html, render_json, render_sarif, render_text, render_markdown


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
        self.assertIn("**VERDICT:** PASS", render_markdown(result))


if __name__ == "__main__":
    unittest.main()
