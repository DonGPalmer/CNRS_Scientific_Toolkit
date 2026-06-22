"""
cnrs.cnrs_h_branch
==================

Branch-state helpers for CNRS-H local analytic objects.

v0.6.1 moves branch metadata from the symbolic layer into the CNRS-H jet layer.
The goal is deliberately modest: branch choices used by symbolic log/sqrt/power
expressions are carried by the local coefficient representation, and simple
composition/multiplication operations preserve a conservative merged branch
state.  This is not yet path-dependent analytic continuation; it is local branch
bookkeeping for finite CNRS-H jets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .symbolic import BranchState, DEFAULT_BRANCH_STATE, Expr, Log, Sqrt, Pow


@dataclass(frozen=True)
class BranchConflict:
    """Description of a conservative branch-state merge conflict."""

    field: str
    left: int
    right: int

    def __str__(self) -> str:  # pragma: no cover - trivial display helper
        return f"{self.field}: {self.left} vs {self.right}"


@dataclass(frozen=True)
class BranchMergeResult:
    """Result returned by :func:`merge_branch_states`."""

    state: BranchState
    conflicts: tuple[BranchConflict, ...] = ()

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        if not self.conflicts:
            return str(self.state)
        conflicts = ", ".join(str(c) for c in self.conflicts)
        return f"{self.state} [conflicts: {conflicts}]"


def _choose_nonzero_or_left(field: str, left: int, right: int) -> tuple[int, BranchConflict | None]:
    """Merge one integer branch field conservatively.

    Zero is treated as the default branch.  If one side is default and the other
    is non-default, keep the non-default.  If both sides are non-default and
    different, keep the left value but report a conflict so callers can expose
    the ambiguity to users/tests.
    """
    if left == right:
        return left, None
    if left == 0:
        return right, None
    if right == 0:
        return left, None
    return left, BranchConflict(field, left, right)


def merge_branch_states(left: BranchState | None, right: BranchState | None) -> BranchMergeResult:
    """Conservatively merge two local branch-state records.

    This function does not attempt path lifting or monodromy.  It just preserves
    explicit local branch choices when finite CNRS-H jets are combined.
    """
    a = left or DEFAULT_BRANCH_STATE
    b = right or DEFAULT_BRANCH_STATE
    log_branch, c1 = _choose_nonzero_or_left("log_branch", a.log_branch, b.log_branch)
    sqrt_branch, c2 = _choose_nonzero_or_left("sqrt_branch", a.sqrt_branch, b.sqrt_branch)
    pow_branch, c3 = _choose_nonzero_or_left("pow_branch", a.pow_branch, b.pow_branch)
    winding, c4 = _choose_nonzero_or_left("winding", a.winding, b.winding)
    conflicts = tuple(c for c in (c1, c2, c3, c4) if c is not None)
    return BranchMergeResult(BranchState(log_branch, sqrt_branch, pow_branch, winding), conflicts)


def branch_state_from_symbolic(expr: Any) -> BranchState:
    """Extract local branch-state metadata from a symbolic expression tree.

    The returned state records explicit branch choices appearing in ``Log``,
    ``Sqrt``, and branch-aware ``Pow`` nodes.  Mixed non-default branches of the
    same kind are merged conservatively by keeping the first encountered value;
    callers that need conflict reporting should use :func:`branch_merge_report`.
    """
    return branch_merge_report(expr).state


def branch_merge_report(expr: Any) -> BranchMergeResult:
    """Return extracted branch state plus any local merge conflicts."""
    from . import symbolic as sy

    try:
        e = sy.sympify(expr)
    except Exception:
        return BranchMergeResult(DEFAULT_BRANCH_STATE)

    def walk(node: Expr) -> BranchMergeResult:
        state = DEFAULT_BRANCH_STATE
        conflicts: list[BranchConflict] = []

        if isinstance(node, Log):
            state = state.for_log(node.branch)
        elif isinstance(node, Sqrt):
            state = state.for_sqrt(node.branch)
        elif isinstance(node, Pow):
            state = state.for_pow(node.branch)

        children = []
        if hasattr(node, "arg"):
            children.append(getattr(node, "arg"))
        if hasattr(node, "left") and hasattr(node, "right"):
            children.extend([getattr(node, "left"), getattr(node, "right")])
        if hasattr(node, "integrand"):
            children.append(getattr(node, "integrand"))

        result = BranchMergeResult(state)
        conflicts.extend(result.conflicts)
        current = result.state
        for child in children:
            child_result = walk(child)
            merged = merge_branch_states(current, child_result.state)
            current = merged.state
            conflicts.extend(child_result.conflicts)
            conflicts.extend(merged.conflicts)
        return BranchMergeResult(current, tuple(conflicts))

    return walk(e)


def branch_note_for_composition(outer: BranchState, inner: BranchState) -> str:
    """Human-readable local warning for branch-state composition."""
    merged = merge_branch_states(outer, inner)
    if merged.has_conflicts:
        return "local branch states merged with conflicts; no path continuation performed"
    if merged.state != DEFAULT_BRANCH_STATE:
        return "local branch state preserved; no path continuation performed"
    return "principal/default local branch state; no path continuation performed"


__all__ = [
    "BranchConflict",
    "BranchMergeResult",
    "merge_branch_states",
    "branch_state_from_symbolic",
    "branch_merge_report",
    "branch_note_for_composition",
]
