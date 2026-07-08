"""
cnrs_layer3_continuation.py
---------------------------
Continuation rules for Layer-3 analytic objects.

Layer-3 continuation may depend on:
  - the HStream prefix
  - the Layer-2 branch index
  - the active operator context
  - the underlying Gaussian value

This module provides:
  - L3ContinuationRule: callable rule for L3Value -> next digit
  - simple rules (greedy, branch-sensitive, operator-sensitive)
  - L3ContinuationEngine: applies rules to extend L3Value objects
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from .cnrs_layer3 import L3Value
from .cnrs_repr import cnrs_remainder
from .cnrs_hstream import HStream


# ---------------------------------------------------------------------------
# Rule type
# ---------------------------------------------------------------------------

L3ContinuationRule = Callable[[L3Value], int]


# ---------------------------------------------------------------------------
# Basic continuation rules
# ---------------------------------------------------------------------------

def l3_rule_greedy(v: L3Value) -> int:
    """
    Greedy continuation based on the current HStream prefix.

    This is the Layer-3 lift of the CNRS-A greedy remainder rule.
    """
    g = v.stream.to_gaussian()
    return cnrs_remainder(g)


def l3_rule_branch_sensitive(v: L3Value) -> int:
    """
    Branch-sensitive continuation:

        next_digit = remainder( g + k )

    where k is the Layer-2 branch index.

    This is a simple model of branch-dependent analytic continuation.
    """
    g = v.stream.to_gaussian()
    k = v.l2.k
    return cnrs_remainder(g + k)


def l3_rule_operator_sensitive(v: L3Value) -> int:
    """
    Operator-sensitive continuation:

    If an operator is active, apply it to the stream before computing
    the next digit. Otherwise fall back to greedy.
    """
    if v.op is None:
        return l3_rule_greedy(v)

    # Apply operator to the stream only (not to the whole L3Value)
    transformed_stream = v.op.f_stream(v.stream)
    g = transformed_stream.to_gaussian()
    return cnrs_remainder(g)


# ---------------------------------------------------------------------------
# Continuation engine
# ---------------------------------------------------------------------------

@dataclass
class L3ContinuationEngine:
    """
    Applies a Layer-3 continuation rule to extend L3Value objects.

    Example:
        eng = L3ContinuationEngine(l3_rule_greedy)
        v2 = eng.extend(v, 10)
    """
    rule: L3ContinuationRule

    def step(self, v: L3Value) -> L3Value:
        """
        Extend the L3Value by one digit according to the rule.
        """
        d = self.rule(v)
        new_stream = v.stream.extend(d)

        return L3Value(
            l2=v.l2,
            stream=new_stream,
            cont=v.cont,
            op=v.op
        )

    def extend(self, v: L3Value, n: int) -> L3Value:
        """
        Extend the L3Value by n digits.
        """
        out = v
        for _ in range(n):
            out = self.step(out)
        return out
