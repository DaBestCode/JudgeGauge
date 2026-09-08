# Validate the OpenAI-compatible adapter against a live endpoint

## Problem

The adapter is covered by deterministic local tests, but has not yet been exercised against a live
OpenAI-compatible Chat Completions endpoint. We need to verify wire compatibility without making a
personal API key a contributor requirement.

## Proposed work

- Add mocked HTTP fixtures for successful, malformed, unauthorized, rate-limited, and unavailable
  responses.
- Add an opt-in live test marked with `JUDGEGAUGE_LIVE_TEST=1`.
- Read the credential only from `OPENAI_API_KEY`; never print or persist it.
- Support `OPENAI_MODEL` and `OPENAI_BASE_URL` in the live test.
- Run the live test only from a manually triggered GitHub Actions workflow using repository secrets.
- Confirm that request and response hashes contain no authorization material.
- Document the maximum request count and expected API cost before the workflow runs.

## Acceptance criteria

- The default test suite remains completely keyless.
- `python -m unittest discover -s tests -v` never calls the network.
- The opt-in test skips with a clear message unless both the flag and API key are present.
- Authentication, transport, and malformed-response failures exit with code `2`.
- A smoke-gate failure exits with code `1` and does not expose the credential.
- CI logs and uploaded artifacts contain no API key or `Authorization` header.

## Security note

Do not ask contributors to place keys in fixtures, issue comments, pull requests, or fork secrets.
Repository maintainers should use an environment-protected secret with a low-spend project key.

Suggested labels: `good first issue`, `testing`, `provider:openai-compatible`, `security`
