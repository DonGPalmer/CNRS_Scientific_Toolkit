"""
cnrs_layer4.py
--------------
Layer-4: Global analytic object for the CNRS programme.

Layer-4 unifies:
  - multiple Layer-3 analytic states
  - continuation paths
  - branch transitions
  - operator histories
  - global analytic evaluation

This is the top-level analytic layer required for Problem 2 and Problem 4.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable

from .cnrs_layer3 import L3Value
from .cnrs_layer3_continuation import L3ContinuationEngine, l3_rule_greedy
from .cnrs_layer3_ops import L3Operator


@dataclass
class L4State:
    """
    A single analytic branch/state inside a Layer-4 object.

    Stores:
      - l3 : the Layer-3 analytic value
      - path : list of continuation steps (digits)
      - ops : list of operators applied in sequence
    """
    l3: L3Value
    path: List[int] = field(default_factory=list)
    ops: List[L3Operator] = field(default_factory=list)

    def record_step(self, digit: int):
        self.path.append(digit)

    def record_operator(self, op: L3Operator):
        self.ops.append(op)


@dataclass
class L4Value:
    """
    Layer-4 global analytic object.

    Contains:
      - states: a list of L4State objects (multiple analytic branches)
      - cont: a continuation engine for evolving states
      - name: optional label for debugging / display
    """
    states: List[L4State]
    cont: L3ContinuationEngine
    name: Optional[str] = None

    # -----------------------------
    # Construction
    # -----------------------------

    @staticmethod
    def from_l3(l3: L3Value,
                rule: Callable = l3_rule_greedy,
                name: Optional[str] = None) -> "L4Value":
        """
        Build a Layer-4 object from a single Layer-3 value.
        """
        state = L4State(l3)
        eng = L3ContinuationEngine(rule)
        return L4Value([state], eng, name)

    # -----------------------------
    # Global continuation
    # -----------------------------

    def continue_all(self, n: int) -> "L4Value":
        """
        Continue all analytic branches by n steps.
        """
        new_states = []
        for st in self.states:
            l3_new = self.cont.extend(st.l3, n)
            digits = l3_new.stream.digits[len(st.l3.stream.digits):]
            st_new = L4State(l3_new,
                             path=st.path + digits,
                             ops=st.ops[:])
            new_states.append(st_new)
        return L4Value(new_states, self.cont, self.name)

    # -----------------------------
    # Branch creation
    # -----------------------------

    def branch(self, selector: Callable[[L4State], bool]) -> "L4Value":
        """
        Create a new Layer-4 object containing only the states
        for which selector(state) is True.
        """
        filtered = [s for s in self.states if selector(s)]
        return L4Value(filtered, self.cont, self.name)

    def split(self, count: int) -> "L4Value":
        """
        Duplicate each state 'count' times.
        Useful for multi-sheet analytic continuation.
        """
        new_states = []
        for st in self.states:
            for _ in range(count):
                new_states.append(L4State(st.l3, st.path[:], st.ops[:]))
        return L4Value(new_states, self.cont, self.name)

    # -----------------------------
    # Operator application
    # -----------------------------

    def apply(self, op: L3Operator) -> "L4Value":
        """
        Apply an operator to all analytic branches.
        """
        new_states = []
        for st in self.states:
            new_l3 = op(st.l3)
            st_new = L4State(new_l3,
                             path=st.path[:],
                             ops=st.ops + [op])
            new_states.append(st_new)
        return L4Value(new_states, self.cont, self.name)

    # -----------------------------
    # Evaluation
    # -----------------------------

    def evaluate(self) -> List[complex]:
        """
        Evaluate all analytic branches to Gaussian values.
        """
        return [st.l3.to_gaussian() for st in self.states]

    # -----------------------------
    # Pretty printing
    # -----------------------------

    def __str__(self) -> str:
        return f"L4Value(name={self.name}, branches={len(self.states)})"

    def __repr__(self) -> str:
        return str(self)
