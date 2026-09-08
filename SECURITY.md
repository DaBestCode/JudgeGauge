# Security policy

## Supported versions

JudgeGauge is pre-1.0. Security fixes are applied to the latest published minor release.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/DaBestCode/JudgeGauge/security/advisories/new).
Do not open a public issue for exposed credentials, unsafe artifact handling, request smuggling, or
report-redaction failures.

Include the affected version, impact, and a minimal reproduction with all credentials removed. A
maintainer will acknowledge a complete report within seven days. No response-time guarantee applies
until the project has more than one active maintainer.

JudgeGauge should never persist `Authorization`, `Proxy-Authorization`, or API-key headers. Treat a
report containing any of these values as a security vulnerability.

