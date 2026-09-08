from __future__ import annotations

import hashlib
import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

from judgegauge.errors import ConfigurationError, InvalidReadout, ProviderError
from judgegauge.providers import OpenAICompatibleJudge
from judgegauge.suites import SMOKE_SUITE


class FakeHTTPResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


def completion_body(content) -> bytes:
    return json.dumps(
        {
            "model": "returned-snapshot",
            "choices": [{"message": {"content": content}}],
        }
    ).encode()


class OpenAICompatibleJudgeTests(unittest.TestCase):
    def setUp(self):
        self.case = SMOKE_SUITE[0]
        self.judge = OpenAICompatibleJudge(
            api_key="test-secret", model="test-model", base_url="https://example.test/v1"
        )

    def test_from_env_requires_a_key(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ConfigurationError):
            OpenAICompatibleJudge.from_env()

    def test_valid_response_is_parsed_and_hashed_without_hashing_credentials(self):
        readout = json.dumps(
            {
                "ranking": ["candidate_a", "candidate_b"],
                "scores": {"candidate_a": 1.0, "candidate_b": 0.0},
            }
        )
        body = completion_body(readout)
        with patch(
            "judgegauge.providers.urllib.request.urlopen",
            return_value=FakeHTTPResponse(body),
        ) as urlopen:
            response = self.judge(self.case, self.case.candidates)

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")
        self.assertNotIn(b"test-secret", request.data)
        self.assertEqual(response.model, "returned-snapshot")
        self.assertEqual(response.request_sha256, hashlib.sha256(request.data).hexdigest())
        self.assertEqual(response.response_sha256, hashlib.sha256(body).hexdigest())

    def test_markdown_wrapped_json_is_rejected(self):
        body = completion_body(
            '```json\n{"ranking":["candidate_a","candidate_b"],'
            '"scores":{"candidate_a":1,"candidate_b":0}}\n```'
        )
        with (
            patch(
                "judgegauge.providers.urllib.request.urlopen",
                return_value=FakeHTTPResponse(body),
            ),
            self.assertRaises(InvalidReadout),
        ):
            self.judge(self.case, self.case.candidates)

    def test_out_of_range_scores_are_rejected(self):
        body = completion_body(
            json.dumps(
                {
                    "ranking": ["candidate_a", "candidate_b"],
                    "scores": {"candidate_a": 10, "candidate_b": 0},
                }
            )
        )
        with (
            patch(
                "judgegauge.providers.urllib.request.urlopen",
                return_value=FakeHTTPResponse(body),
            ),
            self.assertRaises(InvalidReadout),
        ):
            self.judge(self.case, self.case.candidates)

    def test_http_errors_are_execution_errors_not_readout_failures(self):
        error = urllib.error.HTTPError(
            url="https://example.test/v1/chat/completions",
            code=429,
            msg="rate limited",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"rate limited"}'),
        )
        with (
            patch("judgegauge.providers.urllib.request.urlopen", side_effect=error),
            self.assertRaisesRegex(ProviderError, "HTTP 429"),
        ):
            self.judge(self.case, self.case.candidates)


if __name__ == "__main__":
    unittest.main()
