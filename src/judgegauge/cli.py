from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .calibration import calibrate
from .errors import JudgeGaugeError
from .providers import DEFAULT_MODEL
from .reporting import render_html, render_json, render_sarif, render_text

RENDERERS = {
    "text": render_text,
    "json": render_json,
    "sarif": render_sarif,
    "html": render_html,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="judgegauge")
    parser.add_argument("--version", action="version", version="JudgeGauge 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)
    gate = subparsers.add_parser("gate", help="calibrate a judge and fail closed")
    gate.add_argument("--smoke", action="store_true", help="run the built-in smoke suite")
    gate.add_argument("--model", help=f"model id (default: OPENAI_MODEL or {DEFAULT_MODEL})")
    gate.add_argument("--base-url", help="OpenAI-compatible API base URL")
    gate.add_argument("--format", choices=tuple(RENDERERS), default="text")
    gate.add_argument("--output", type=Path, help="write the report to a file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "gate":
        return 2
    if not args.smoke:
        print("error: v0.1.0 requires --smoke", file=sys.stderr)
        return 2
    try:
        result = calibrate(model=args.model, base_url=args.base_url)
    except (JudgeGaugeError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = RENDERERS[args.format](result)
    if args.output:
        try:
            args.output.write_text(
                rendered + ("\n" if args.format != "html" else ""), encoding="utf-8"
            )
        except OSError as exc:
            print(f"error: could not write report: {exc}", file=sys.stderr)
            return 2
        if args.format == "text":
            print(f"Report: {args.output}")
    else:
        print(rendered)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
