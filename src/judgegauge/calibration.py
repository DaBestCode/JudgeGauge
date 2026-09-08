from __future__ import annotations

import math
from collections.abc import Sequence

from .errors import InvalidReadout
from .models import CalibrationCase, CalibrationResult, JudgeResponse, Metric, Verdict
from .providers import Judge, OpenAICompatibleJudge
from .suites import SMOKE_SUITE


def _pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_scale = math.sqrt(sum((a - left_mean) ** 2 for a in left))
    right_scale = math.sqrt(sum((b - right_mean) ** 2 for b in right))
    if left_scale == 0 or right_scale == 0:
        return 1.0 if list(left) == list(right) else 0.0
    return numerator / (left_scale * right_scale)


def _rank_vector(
    responses: Sequence[JudgeResponse], cases: Sequence[CalibrationCase]
) -> list[float]:
    vector: list[float] = []
    for response, case in zip(responses, cases):
        positions = {candidate_id: index for index, candidate_id in enumerate(response.ranking)}
        vector.extend(float(positions[candidate.id]) for candidate in case.candidates)
    return vector


def _validate_response(response: JudgeResponse, case: CalibrationCase) -> None:
    candidate_ids = {candidate.id for candidate in case.candidates}
    if len(response.ranking) != len(candidate_ids) or set(response.ranking) != candidate_ids:
        raise InvalidReadout("ranking must contain every candidate id exactly once")
    if set(response.scores) != candidate_ids:
        raise InvalidReadout("scores must contain every candidate id exactly once")
    if any(
        isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score)
        for score in response.scores.values()
    ):
        raise InvalidReadout("every candidate score must be a finite number")


def calibrate(
    judge: Judge | None = None,
    *,
    suite: str = "smoke",
    max_requests: int = 12,
    model: str | None = None,
    base_url: str | None = None,
    repeat_threshold: float = 0.90,
    permutation_flip_threshold: float = 0.10,
) -> CalibrationResult:
    """Measure a judge in the current execution window and return a frozen verdict."""
    if suite != "smoke":
        raise ValueError("only the builtin smoke suite is available in v0.1.0")
    cases = SMOKE_SUITE
    required_requests = len(cases) * 3
    if max_requests < required_requests:
        raise ValueError(f"smoke suite requires {required_requests} requests")

    resolved_judge = judge or OpenAICompatibleJudge.from_env(model=model, base_url=base_url)
    forward_first: list[JudgeResponse] = []
    forward_second: list[JudgeResponse] = []
    reversed_order: list[JudgeResponse] = []
    response_models: list[str] = []
    invalid_readouts = 0
    request_count = 0

    def measured_call(case: CalibrationCase, *, reverse: bool = False) -> JudgeResponse | None:
        nonlocal invalid_readouts, request_count
        candidates = tuple(reversed(case.candidates)) if reverse else case.candidates
        request_count += 1
        try:
            response = resolved_judge(case, candidates)
            _validate_response(response, case)
        except InvalidReadout:
            invalid_readouts += 1
            return None
        response_models.append(response.model)
        return response

    for case in cases:
        first = measured_call(case)
        second = measured_call(case)
        reversed_response = measured_call(case, reverse=True)
        if first is not None:
            forward_first.append(first)
        if second is not None:
            forward_second.append(second)
        if reversed_response is not None:
            reversed_order.append(reversed_response)

    complete = (
        len(forward_first) == len(cases)
        and len(forward_second) == len(cases)
        and len(reversed_order) == len(cases)
    )
    repeat_spearman = (
        _pearson(_rank_vector(forward_first, cases), _rank_vector(forward_second, cases))
        if complete
        else 0.0
    )
    permutation_flip_rate = (
        sum(a.ranking != b.ranking for a, b in zip(forward_first, reversed_order)) / len(cases)
        if complete
        else 1.0
    )
    invalid_rate = invalid_readouts / request_count if request_count else 1.0

    metrics = (
        Metric(
            "repeat_spearman",
            repeat_spearman,
            repeat_threshold,
            ">=",
            repeat_spearman >= repeat_threshold,
            "Rank-position correlation between two same-order passes.",
        ),
        Metric(
            "permutation_flip_rate",
            permutation_flip_rate,
            permutation_flip_threshold,
            "<=",
            permutation_flip_rate <= permutation_flip_threshold,
            "Fraction of cases whose ranking changed after candidate-order reversal.",
        ),
        Metric(
            "invalid_readout_rate",
            invalid_rate,
            0.0,
            "<=",
            invalid_rate == 0.0,
            "Unparseable readouts are retained as failures rather than retried away.",
        ),
    )
    verdict = Verdict.PASS if all(metric.passed for metric in metrics) else Verdict.FAIL
    return CalibrationResult(
        verdict=verdict,
        metrics=metrics,
        request_count=request_count,
        valid_readouts=request_count - invalid_readouts,
        invalid_readouts=invalid_readouts,
        requested_model=getattr(resolved_judge, "model", model or "custom"),
        response_models=tuple(sorted(set(response_models))),
    )
