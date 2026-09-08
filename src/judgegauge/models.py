from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .errors import JudgeUnreliable


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class Candidate:
    id: str
    text: str


@dataclass(frozen=True)
class CalibrationCase:
    id: str
    prompt: str
    candidates: tuple[Candidate, ...]


@dataclass(frozen=True)
class JudgeResponse:
    ranking: tuple[str, ...]
    scores: dict[str, float]
    model: str = "unknown"
    request_sha256: str | None = None
    response_sha256: str | None = None


@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    threshold: float
    comparator: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class CalibrationResult:
    verdict: Verdict
    metrics: tuple[Metric, ...]
    request_count: int
    valid_readouts: int
    invalid_readouts: int
    requested_model: str
    response_models: tuple[str, ...]
    snapshot_level: str = "L0"
    suite: str = "builtin/smoke-v1"
    limitations: tuple[str, ...] = field(
        default=(
            "This run measures the current execution window only.",
            "Reliability does not establish correctness or agreement with humans.",
            "Results do not generalize to another endpoint, model, rubric, or task family.",
        )
    )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def require(self) -> CalibrationResult:
        if not self.passed:
            failed = ", ".join(metric.name for metric in self.metrics if not metric.passed)
            raise JudgeUnreliable(f"judge failed calibration: {failed}")
        return self

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["verdict"] = self.verdict.value
        return value
