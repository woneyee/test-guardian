"""Failure routing interfaces and implementations."""

from test_guardian.agents.router.base import FailureRouter
from test_guardian.agents.router.simple import SimpleFailureRouter

__all__ = [
    "FailureRouter",
    "SimpleFailureRouter",
]
