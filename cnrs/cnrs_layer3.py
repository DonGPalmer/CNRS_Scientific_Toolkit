"""
cnrs_layer3.py
--------------
Layer-3 analytic object for the CNRS programme.

Layer-3 unifies:
  - Layer-1 CNRS-A values
  - Layer-2 branch index
  - CNRS-H streams (prefixes)
  - Continuation rules
  - Operator calculus

This is the analytic layer required for Problem 2 and Problem 4.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable

from .cnrs_layer2 import Layer2
from .cnrs_layer2_value import L2Val
from .cnrs_hstream import HStream
from .cnrs_continuation import ContinuationEngine, rule_greedy
from .cnrs_operator import Operator


@dataclass
class L3Value:
    """
    Layer-3 analytic object.

    Components:
      - l2 : Layer2 value (z, k)
      - stream : HStream prefix
      - cont : continuation engine
      - op : optional operator acting on the stream

    This object is the "analytic state" of a CNRS value.
    """
    l2: L2Val
    stream: HStream
    cont: ContinuationEngine
    op: Optional[Operator] = None

    # -----------------------------
    # Construction
    # -----------------------------

    @staticmethod
    def from_gaussian(g: complex, k: int = 0,
                      rule: Callable = rule_greedy) -> "L3Value":
        """
        Build a Layer-3 value from a Gaussian integer and branch index.
        """
        l2 = L2Val.from_gaussian(g, k)
        stream = HStream.from_gaussian(g)
        cont = ContinuationEngine(rule)
        return L3Value(l2, stream, cont)

    @staticmethod
    def from_layer2(l2: L2Val,
                    rule: Callable = rule_greedy) -> "L3Value":
        """
        Build a Layer-3 value from a Layer-2 object.
        """
        stream = HStream.from_gaussian(l2.to_gaussian())
        cont = ContinuationEngine(rule)
        return L3Value(l2, stream, cont)

    # -----------------------------
    # Evaluation
    # -----------------------------

    def to_gaussian(self) -> complex:
        """
        Evaluate the Layer-3 value by forgetting stream/operator context.
        """
        return self.l2.to_gaussian()

    # -----------------------------
    # Continuation
    # -----------------------------

    def continue_by(self, n: int) -> "L3Value":
        """
        Extend the HStream prefix by n digits using the continuation rule.
        """
        new_stream = self.cont.extend(self.stream, n)
        return L3Value(self.l2, new_stream, self.cont, self.op)

    # -----------------------------
    # Operator application
    # -----------------------------

    def apply(self, operator: Operator) -> "L3Value":
        """
        Apply an operator to the HStream component.
        """
        new_stream = operator(self.stream)
        return L3Value(self.l2, new_stream, self.cont, operator)

    # -----------------------------
    # Branch manipulation
    # -----------------------------

    def shift_branch(self, dk: int) -> "L3Value":
        """
        Adjust the branch index.
        """
        new_l2 = L2Val.from_gaussian(self.l2.to_gaussian(), self.l2.k + dk)
        return L3Value(new_l2, self.stream, self.cont, self.op)

    # -----------------------------
    # Pretty printing
    # -----------------------------

    def __str__(self) -> str:
        op_str = f", op={self.op}" if self.op else ""
        return f"L3Value(z={self.l2.z}, k={self.l2.k}, stream={self.stream.to_str()}{op_str})"

    def __repr__(self) -> str:
        return str(self)
