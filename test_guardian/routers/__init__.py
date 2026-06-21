"""Failure routing interfaces and implementations."""

from test_guardian.routers.base import FailureRouter
from test_guardian.routers.failure_router import SimpleFailureRouter

__all__ = [
    "FailureRouter",
    "SimpleFailureRouter",
]
