"""
cnrs_continuation.py
--------------------
Analytic continuation framework for CNRS-H streams.

This module provides:

  - ContinuationRule: a callable rule for extending an HStream
  - simple continuation rules (identity, zero-fill, greedy remainder)
  - ContinuationEngine: applies rules to extend streams
  - multi-branch continuation (Layer-2 compatible)

This is the foundation for Problem-2's analytic continuation layer.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable, List

from .cnrs_hstream import HStream
from .cnrs_repr import cnrs_remainder, Z0
from .cnrs_layer2 import Layer2


# ---------------------------------------------------------------------------
# Continuation rules
# ---------------------------------------------------------------------------

ContinuationRule = Callable[[HStream], int]


def rule_identity(stream: HStream) -> int:
    """
    Identity continuation: repeat the last digit.
    Useful as a placeholder or for testing.
    """
    return stream.digits[-1] if stream.digits else 0


def rule_zero(stream: HStream) -> int:
    """
    Zero-fill continuation: always append 0.
    """
    return 0


def rule_greedy(stream: HStream) -> int:
    """
    Greedy analytic continuation rule:

        Given prefix d0, d1, ..., dn, compute the Gaussian value
        and choose the next digit via the CNRS remainder logic.

    This is the natural extension of the CNRS-A greedy expansion.
    """
    g = stream.to_gaussian()
    d = cnrs_remainder(g)
    return d


# ---------------------------------------------------------------------------
# Continuation engine
# ---------------------------------------------------------------------------

@dataclass
class ContinuationEngine:
    """
    Applies a continuation rule to extend an HStream.

    Example:
        eng = ContinuationEngine(rule_greedy)
        s2 = eng.extend(stream, 10)   # extend by 10 digits
    """
    rule: ContinuationRule

    def step(self, stream: HStream) -> HStream:
        """Extend by one digit."""
        d = self.rule(stream)
        return stream.extend(d)

    def extend(self, stream: HStream, n: int) -> HStream:
        """Extend by n digits."""
        out = stream
        for _ in range(n):
            out = self.step(out)
        return out


# ---------------------------------------------------------------------------
# Multi-branch continuation (Layer-2 compatible)
# ---------------------------------------------------------------------------

@dataclass
class BranchContinuation:
    """
    Continuation with branch index propagation.

    Each continuation step updates:
        - the HStream prefix
        - the Layer-2 branch index k
    """
    rule: ContinuationRule

    def step(self, stream: HStream, k: int) -> tuple[HStream, int]:
        """
        Extend the stream and update the branch index.

        Current convention:
            k_next = k   (branch index unchanged)
        """
        d = self.rule(stream)
        return stream.extend(d), k

    def extend(self, stream: HStream, k: int, n: int) -> tuple[HStream, int]:
        out = stream
        kk = k
        for _ in range(n):
            out, kk = self.step(out, kk)
        return out, kk
