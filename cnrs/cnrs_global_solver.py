"""
cnrs_global_solver.py
---------------------
Global solver for CNRS Layer-4 analytic objects.

This module provides:
  - evolution under continuation
  - operator-driven evolution
  - constraint enforcement
  - fixed-point iteration
  - multi-branch solving

This is the computational engine for Problem 2 and Problem 4.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, List

from .cnrs_layer4 import L4Value, L4State
from .cnrs_layer3_ops import L3Operator
from .cnrs_layer3_continuation import L3ContinuationEngine


# ---------------------------------------------------------------------------
# Constraint type
# ---------------------------------------------------------------------------

Constraint = Callable[[L4State], bool]


# ---------------------------------------------------------------------------
# Global Solver
# ---------------------------------------------------------------------------

@dataclass
class GlobalSolver:
    """
    Global CNRS analytic solver.

    Controls:
      - continuation
      - operator application
      - constraint filtering
      - fixed-point iteration
      - multi-branch evolution
    """
    cont: L3ContinuationEngine

    # -----------------------------
    # Continuation evolution
    # -----------------------------

    def evolve(self, v: L4Value, steps: int) -> L4Value:
        """
        Continue all branches for a fixed number of steps.
        """
        return v.continue_all(steps)

    # -----------------------------
    # Operator-driven evolution
    # -----------------------------

    def apply_operator(self, v: L4Value, op: L3Operator) -> L4Value:
        """
        Apply an operator to all branches.
        """
        return v.apply(op)

    # -----------------------------
    # Constraint enforcement
    # -----------------------------

    def enforce(self, v: L4Value, constraint: Constraint) -> L4Value:
        """
        Keep only branches satisfying the constraint.
        """
        return v.branch(constraint)

    # -----------------------------
    # Fixed-point iteration
    # -----------------------------

    def fixed_point(self,
                    v: L4Value,
                    op: L3Operator,
                    max_iter: int = 50,
                    tol: float = 1e-9) -> L4Value:
        """
        Solve for a fixed point of an operator:

            op(v) = v

        using iterative refinement on each branch.
        """
        current = v
        for _ in range(max_iter):
            next_v = current.apply(op)

            # Check convergence branch-by-branch
            converged = True
            for s_old, s_new in zip(current.states, next_v.states):
                if abs(s_old.l3.to_gaussian() - s_new.l3.to_gaussian()) > tol:
                    converged = False
                    break

            if converged:
                return next_v

            current = next_v

        return current  # return last iterate if no convergence

    # -----------------------------
    # Multi-branch evolution
    # -----------------------------

    def evolve_branches(self,
                        v: L4Value,
                        steps: int,
                        branch_factor: int,
                        constraint: Optional[Constraint] = None) -> L4Value:
        """
        Evolve with branching:

            1. Continue all branches
            2. Split each branch
            3. Optionally enforce a constraint
        """
        evolved = v.continue_all(steps)
        branched = evolved.split(branch_factor)

        if constraint is not None:
            return branched.branch(constraint)

        return branched
