"""Routing agents."""

from test_guardian.agents.router.base import FailureRouter
from test_guardian.agents.router.simple import SimpleFailureRouter

__all__ = [
    "FailureRouter",
    "SimpleFailureRouter",
]
