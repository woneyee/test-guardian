"""Compatibility wrapper for the Test Guardian evaluation CLI."""

from test_guardian.cli.evaluate import *  # noqa: F403


if __name__ == "__main__":
    raise SystemExit(main())
