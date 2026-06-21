"""Compatibility wrapper for the adversarial evaluation CLI."""

from test_guardian.cli.adversarial_evaluate import *  # noqa: F403


def _limited_requirements(limit):
    requirements = load_requirements()  # noqa: F405
    if limit is None:
        return requirements
    return requirements[:limit]


if __name__ == "__main__":
    raise SystemExit(main())
