"""
cnrs.cnrs_h_continuation
========================

Branch-aware local continuation scaffolding for CNRS-H jets.

v0.6.2 recorded path-induced branch-state changes on finite CNRS-H jets.
v0.6.3 takes the next conservative step: when the original symbolic expression
is available, it can build a *continued symbolic expression* whose local branch
labels are shifted by the winding events along a supplied path, and then rebuild
the CNRS-H jet from that continued expression.

This is still not a full Riemann-surface or global analytic-continuation engine.
It is a local, finite-order coefficient recalculation using explicit branch
metadata.  The intent is to make branch changes affect the local coefficients
when they can be represented by supported symbolic log/sqrt/power nodes, rather
than merely storing path history as metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from . import symbolic as sy
from .symbolic import BranchState, DEFAULT_BRANCH_STATE
from .cnrs_h_path import (
    BranchPoint,
    ContinuationPath,
    WindingEvent,
    winding_events,
    update_branch_state_along_path,
    path_history_note,
)
from .cnrs_h_jet import CnrsHJet, jet_from_symbolic


class CnrsHContinuationError(ValueError):
    """Raised for unsupported CNRS-H continuation operations."""


@dataclass(frozen=True)
class BranchDelta:
    """Integer branch changes induced by a continuation path."""

    log_delta: int = 0
    sqrt_delta: int = 0
    pow_delta: int = 0
    winding_delta: int = 0

    @property
    def is_zero(self) -> bool:
        return not (self.log_delta or self.sqrt_delta or self.pow_delta or self.winding_delta)

    def apply_to_state(self, state: BranchState | None = None) -> BranchState:
        """Return ``state`` shifted by this branch delta."""
        s = state or DEFAULT_BRANCH_STATE
        return BranchState(
            s.log_branch + self.log_delta,
            (s.sqrt_branch + self.sqrt_delta) % 2,
            s.pow_branch + self.pow_delta,
            s.winding + self.winding_delta,
        )

    def summary(self) -> str:
        parts = []
        if self.log_delta:
            parts.append(f"log {self.log_delta:+d}")
        if self.sqrt_delta:
            parts.append(f"sqrt parity {self.sqrt_delta:+d}")
        if self.pow_delta:
            parts.append(f"pow {self.pow_delta:+d}")
        if self.winding_delta:
            parts.append(f"winding {self.winding_delta:+d}")
        return ", ".join(parts) if parts else "no branch delta"


@dataclass(frozen=True)
class ContinuationRebuildResult:
    """Result of rebuilding a CNRS-H jet after symbolic branch continuation."""

    original_expr: sy.Expr
    continued_expr: sy.Expr
    original_jet: CnrsHJet
    continued_jet: CnrsHJet
    branch_delta: BranchDelta
    events: tuple[WindingEvent, ...]
    note: str

    @property
    def coeff_changed(self) -> bool:
        return self.original_jet.max_coeff_error(self.continued_jet) > 0

    @property
    def max_coeff_delta(self) -> float:
        return self.original_jet.max_coeff_error(self.continued_jet)

    def summary(self) -> str:
        return (
            f"{self.note}; delta=({self.branch_delta.summary()}); "
            f"max_coeff_delta={self.max_coeff_delta:g}"
        )


def branch_delta_from_events(events: Sequence[WindingEvent]) -> BranchDelta:
    """Convert winding events into a conservative branch delta.

    Rules match :func:`update_branch_state_along_path`:
    log branch increments by winding; sqrt branch toggles by winding parity;
    power branch increments by winding; kind ``all`` applies all three.
    """
    log_delta = 0
    sqrt_delta = 0
    pow_delta = 0
    winding_delta = 0
    for event in events:
        kind = event.kind.lower()
        w = event.winding
        winding_delta += w
        if kind in {"log", "logarithm"}:
            log_delta += w
        elif kind in {"sqrt", "square-root", "square_root"}:
            sqrt_delta += w
        elif kind in {"pow", "power"}:
            pow_delta += w
        elif kind == "all":
            log_delta += w
            sqrt_delta += w
            pow_delta += w
    return BranchDelta(log_delta, sqrt_delta, pow_delta, winding_delta)


def _shift_expr(node: sy.Expr, delta: BranchDelta) -> sy.Expr:
    """Recursively shift explicit symbolic branch labels."""
    # Leaves.
    if isinstance(node, (sy.Const, sy.Var)):
        return node

    # Unary functions with explicit branch data.
    if isinstance(node, sy.Log):
        return sy.Log(_shift_expr(node.arg, delta), branch=node.branch + delta.log_delta)
    if isinstance(node, sy.Sqrt):
        return sy.Sqrt(_shift_expr(node.arg, delta), branch=(node.branch + delta.sqrt_delta) % 2)
    if isinstance(node, sy.Pow):
        return sy.Pow(_shift_expr(node.left, delta), _shift_expr(node.right, delta), branch=node.branch + delta.pow_delta)

    # Other common unary functions.
    if isinstance(node, sy.Exp):
        return sy.Exp(_shift_expr(node.arg, delta))
    if isinstance(node, sy.Sin):
        return sy.Sin(_shift_expr(node.arg, delta))
    if isinstance(node, sy.Cos):
        return sy.Cos(_shift_expr(node.arg, delta))
    if isinstance(node, sy.Tan):
        return sy.Tan(_shift_expr(node.arg, delta))
    if isinstance(node, sy.Neg):
        return sy.Neg(_shift_expr(node.arg, delta))

    # Binary algebra.
    if isinstance(node, sy.Add):
        return sy.Add(_shift_expr(node.left, delta), _shift_expr(node.right, delta))
    if isinstance(node, sy.Sub):
        return sy.Sub(_shift_expr(node.left, delta), _shift_expr(node.right, delta))
    if isinstance(node, sy.Mul):
        return sy.Mul(_shift_expr(node.left, delta), _shift_expr(node.right, delta))
    if isinstance(node, sy.Div):
        return sy.Div(_shift_expr(node.left, delta), _shift_expr(node.right, delta))

    # Formal integral: preserve bound variable, shift branches in integrand.
    if isinstance(node, sy.Integral):
        return sy.Integral(_shift_expr(node.integrand, delta), node.var)

    raise CnrsHContinuationError(f"unsupported symbolic node for branch shifting: {type(node).__name__}")


def shift_symbolic_branches(expr: Any, delta: BranchDelta) -> sy.Expr:
    """Return a copy of ``expr`` with explicit log/sqrt/power branches shifted."""
    return _shift_expr(sy.sympify(expr), delta).simplify()


def continued_jet_from_symbolic(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    center: complex | float | int = 0,
    order: int = 12,
    path: ContinuationPath,
    branch_points: Sequence[BranchPoint] | None = None,
    env: Mapping[str, Any] | None = None,
    L: int = 18,
    description: str = "",
) -> ContinuationRebuildResult:
    """Rebuild a CNRS-H jet after conservative symbolic branch continuation.

    This helper first builds the original local jet.  It then computes winding
    events for ``path`` around ``branch_points``, shifts explicit symbolic
    branches, rebuilds the local jet from the continued symbolic expression, and
    records the same path event metadata on the result.
    """
    e = sy.sympify(expr)
    bps = tuple(branch_points or (BranchPoint(0j, kind="log", label="0"),))
    events = winding_events(path, bps)
    delta = branch_delta_from_events(events)
    continued_expr = shift_symbolic_branches(e, delta)
    note = path_history_note(path, events)

    original = jet_from_symbolic(e, var, center=center, order=order, env=env, L=L, description=description or str(e))
    continued = jet_from_symbolic(
        continued_expr,
        var,
        center=center,
        order=order,
        env=env,
        L=L,
        branch_state=update_branch_state_along_path(original.branch_state, path, bps),
        description=description or str(continued_expr),
    )
    continued = CnrsHJet(
        continued.series,
        center=continued.center,
        var=continued.var,
        radius_hint=continued.radius_hint,
        domain=continued.domain,
        truncation_error=continued.truncation_error,
        branch_state=continued.branch_state,
        branch_note=note,
        path_history=original.path_history + (note,),
        description=continued.description,
    )
    return ContinuationRebuildResult(e, continued_expr, original, continued, delta, tuple(events), note)


__all__ = [
    "CnrsHContinuationError",
    "BranchDelta",
    "ContinuationRebuildResult",
    "branch_delta_from_events",
    "shift_symbolic_branches",
    "continued_jet_from_symbolic",
]
