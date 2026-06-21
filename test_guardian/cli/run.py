"""Command-line runner for the Test Guardian pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from test_guardian.agents.failure_analyzer.openai import OpenAIFailureAnalyzer
from test_guardian.agents.requirement_extractor.simple import SimpleRequirementExtractor
from test_guardian.agents.test_auditor.openai import OpenAITestAuditor
from test_guardian.models.requirements import RequirementInput
from test_guardian.workflows.guardian_pipeline import GuardianPipeline
from test_guardian.agents.router.simple import SimpleFailureRouter


class CliArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that raises ValueError for testable error handling."""

    def error(self, message: str) -> None:
        if "required" in message:
            raise ValueError("Missing required argument")
        raise ValueError(message)


def main(
    argv: Sequence[str] | None = None,
    *,
    pipeline: GuardianPipeline | None = None,
) -> int:
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
        readme = _read_file(args.readme)
        issue = _read_file(args.issue)
        source_code = _read_file(args.source)
        test_code = _read_file(args.test)
        ci_log = _read_file(args.log)

        active_pipeline = pipeline or _build_pipeline()
        result = active_pipeline.run(
            requirement_input=RequirementInput(readme=readme, issue=issue),
            source_code=source_code,
            test_code=test_code,
            ci_log=ci_log,
        )
    except (FileNotFoundError, ValueError) as error:
        print(_format_error(error), file=sys.stderr)
        return 1

    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = CliArgumentParser(description="Run Test Guardian on a CI failure.")
    parser.add_argument("--readme", required=True, help="README file path")
    parser.add_argument("--issue", required=True, help="Issue file path")
    parser.add_argument("--source", required=True, help="Source code file path")
    parser.add_argument("--test", required=True, help="Test code file path")
    parser.add_argument("--log", required=True, help="CI failure log file path")
    return parser


def _read_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)
    return file_path.read_text(encoding="utf-8")


def _build_pipeline() -> GuardianPipeline:
    return GuardianPipeline(
        requirement_extractor=SimpleRequirementExtractor(),
        failure_analyzer=OpenAIFailureAnalyzer(),
        router=SimpleFailureRouter(),
        test_auditor=OpenAITestAuditor(),
    )


def _format_error(error: BaseException) -> str:
    if isinstance(error, FileNotFoundError):
        return f"File not found: {error.filename or error}"
    return str(error)


if __name__ == "__main__":
    raise SystemExit(main())
