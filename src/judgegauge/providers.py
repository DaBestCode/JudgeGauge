from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from .errors import ConfigurationError, InvalidReadout, ProviderError
from .models import CalibrationCase, Candidate, JudgeResponse

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-5-mini"


class Judge(Protocol):
    model: str

    def __call__(self, case: CalibrationCase, candidates: Sequence[Candidate]) -> JudgeResponse: ...


@dataclass
class OpenAICompatibleJudge:
    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0

    @classmethod
    def from_env(
        cls, *, model: str | None = None, base_url: str | None = None
    ) -> OpenAICompatibleJudge:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not set; export it or pass a custom judge to calibrate()"
            )
        return cls(
            api_key=api_key,
            model=model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
            base_url=(base_url or os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)).rstrip("/"),
        )

    def __call__(self, case: CalibrationCase, candidates: Sequence[Candidate]) -> JudgeResponse:
        candidate_ids = [candidate.id for candidate in candidates]
        rendered = "\n\n".join(f"[{candidate.id}]\n{candidate.text}" for candidate in candidates)
        prompt = (
            f"{case.prompt}\n\n{rendered}\n\n"
            "Return only a JSON object with two keys: "
            '"ranking", an array of every candidate id from best to worst, and '
            '"scores", an object mapping every candidate id to a numeric quality score from 0 to 1.'
        )
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "developer",
                    "content": "You are a precise evaluator. Follow the requested JSON schema exactly.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        request_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=request_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_bytes = response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:500]
            raise ProviderError(f"endpoint returned HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(f"endpoint request failed: {exc.reason}") from exc

        try:
            envelope = json.loads(response_bytes)
            content = envelope["choices"][0]["message"]["content"]
            readout = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise InvalidReadout("response was not a valid Chat Completions JSON readout") from exc

        ranking = readout.get("ranking")
        scores = readout.get("scores")
        if not isinstance(ranking, list) or ranking != list(dict.fromkeys(ranking)):
            raise InvalidReadout("ranking must be an array with no duplicate ids")
        if set(ranking) != set(candidate_ids) or len(ranking) != len(candidate_ids):
            raise InvalidReadout("ranking must contain every candidate id exactly once")
        if not isinstance(scores, dict) or set(scores) != set(candidate_ids):
            raise InvalidReadout("scores must contain every candidate id exactly once")
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= float(value) <= 1
            for value in scores.values()
        ):
            raise InvalidReadout("every candidate score must be numeric and between 0 and 1")

        return JudgeResponse(
            ranking=tuple(ranking),
            scores={key: float(value) for key, value in scores.items()},
            model=str(envelope.get("model", self.model)),
            request_sha256=hashlib.sha256(request_bytes).hexdigest(),
            response_sha256=hashlib.sha256(response_bytes).hexdigest(),
        )
