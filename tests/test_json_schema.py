import json
from pathlib import Path

from jsonschema import validate

from judgegauge.models import CalibrationResult, Metric, Verdict
from judgegauge.reporting import render_json


SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "judgegauge-result-v1.schema.json"


def _result(verdict: Verdict) -> CalibrationResult:
    return CalibrationResult(
        verdict=verdict,
        metrics=(Metric("repeat_ranking", 0.95, 0.90, ">=", verdict is Verdict.PASS),),
        request_count=9,
        valid_readouts=9,
        invalid_readouts=0,
        requested_model="synthetic-model",
        response_models=("synthetic-model",),
        suite="builtin/smoke-v1",
    )


def test_pass_report_matches_v1_schema():
    schema = json.loads(SCHEMA_PATH.read_text())
    payload = json.loads(render_json(_result(Verdict.PASS)))
    validate(payload, schema)
    assert payload["schema_version"] == 1


def test_fail_report_matches_v1_schema_and_allows_additive_fields():
    schema = json.loads(SCHEMA_PATH.read_text())
    payload = json.loads(render_json(_result(Verdict.FAIL)))
    payload["future_additive_field"] = {"safe": True}
    validate(payload, schema)
    assert payload["verdict"] == "fail"
