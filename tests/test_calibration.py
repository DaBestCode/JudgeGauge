from __future__ import annotations

import unittest

import judgegauge
from judgegauge.errors import InvalidReadout
from judgegauge.models import JudgeResponse


class StableJudge:
    model = "test-stable"

    def __call__(self, case, candidates):
        ranking = tuple(candidate.id for candidate in case.candidates)
        return JudgeResponse(
            ranking=ranking,
            scores={candidate.id: 1.0 - index for index, candidate in enumerate(case.candidates)},
            model=self.model,
        )


class PositionBiasedJudge:
    model = "test-position-biased"

    def __call__(self, case, candidates):
        ranking = tuple(candidate.id for candidate in candidates)
        return JudgeResponse(
            ranking=ranking,
            scores={candidate.id: 1.0 - index for index, candidate in enumerate(candidates)},
            model=self.model,
        )


class InvalidJudge:
    model = "test-invalid"

    def __call__(self, case, candidates):
        raise InvalidReadout("bad schema")


class MalformedCustomJudge:
    model = "test-malformed"

    def __call__(self, case, candidates):
        return JudgeResponse(ranking=("unknown",), scores={"unknown": 1.0}, model=self.model)


class CalibrationTests(unittest.TestCase):
    def test_stable_judge_passes(self):
        result = judgegauge.calibrate(StableJudge())

        self.assertTrue(result.passed)
        self.assertEqual(result.request_count, 9)
        self.assertEqual(result.invalid_readouts, 0)
        self.assertIs(result.require(), result)

    def test_position_bias_fails_permutation_gate(self):
        result = judgegauge.calibrate(PositionBiasedJudge())

        self.assertFalse(result.passed)
        metric = next(item for item in result.metrics if item.name == "permutation_flip_rate")
        self.assertEqual(metric.value, 1)
        with self.assertRaises(judgegauge.JudgeUnreliable):
            result.require()

    def test_invalid_readouts_fail_closed(self):
        result = judgegauge.calibrate(InvalidJudge())

        self.assertFalse(result.passed)
        self.assertEqual(result.invalid_readouts, 9)
        metric = next(item for item in result.metrics if item.name == "invalid_readout_rate")
        self.assertEqual(metric.value, 1)

    def test_custom_judge_output_is_validated(self):
        result = judgegauge.calibrate(MalformedCustomJudge())

        self.assertFalse(result.passed)
        self.assertEqual(result.invalid_readouts, 9)

    def test_request_budget_is_enforced_before_calls(self):
        with self.assertRaisesRegex(ValueError, "requires 9 requests"):
            judgegauge.calibrate(StableJudge(), max_requests=8)


if __name__ == "__main__":
    unittest.main()
