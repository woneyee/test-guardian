"""Deterministic requirement extractor for the MVP."""

from __future__ import annotations

import re

from test_guardian.models.requirements import ExtractedRequirement, RequirementInput

_REQUIREMENT_HEADINGS = {
    "acceptance criteria",
    "expected behavior",
    "feature",
    "requirement",
    "requirements",
}


class SimpleRequirementExtractor:
    """Extract a compact requirement from README and issue text."""

    def extract(self, input_data: RequirementInput) -> ExtractedRequirement:
        sources: list[str] = []
        sections: list[str] = []

        if input_data.readme:
            sources.append("README.md")
            sections.append(input_data.readme)

        if input_data.issue:
            sources.append("Issue.md")
            sections.append(input_data.issue)

        combined = _clean_text("\n\n".join(sections))
        feature = _extract_feature(combined)
        requirement = _extract_requirement(combined)

        return ExtractedRequirement(
            feature=feature,
            requirement=requirement,
            sources=sources,
        )


def _clean_text(value: str) -> str:
    lines = [line.strip() for line in value.splitlines()]
    collapsed = "\n".join(line for line in lines if line)
    return re.sub(r"\n{3,}", "\n\n", collapsed).strip()


def _extract_feature(text: str) -> str:
    for line in text.splitlines():
        heading = line.lstrip("#").strip()
        if heading:
            return _trim_sentence(heading)
    return "Unspecified feature"


def _extract_requirement(text: str) -> str:
    heading_lines = text.splitlines()

    for index, line in enumerate(heading_lines):
        heading = line.lstrip("#").strip().rstrip(":").lower()
        if heading in _REQUIREMENT_HEADINGS:
            body = _collect_section_body(heading_lines[index + 1 :])
            if body:
                return body

    return _trim_requirement(text)


def _collect_section_body(lines: list[str]) -> str:
    body: list[str] = []

    for line in lines:
        if line.startswith("#") and body:
            break
        if line:
            body.append(line.lstrip("-* ").strip())

    return _trim_requirement("\n".join(body))


def _trim_requirement(text: str, max_chars: int = 600) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def _trim_sentence(text: str, max_chars: int = 120) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."
