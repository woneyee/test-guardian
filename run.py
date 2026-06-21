"""Compatibility wrapper for the Test Guardian run CLI."""

from test_guardian.cli.run import *  # noqa: F403


if __name__ == "__main__":
    raise SystemExit(main())
