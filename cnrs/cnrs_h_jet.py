"""
cnrs.cnrs_h_jet
================

CNRS-H local jets and expansion-point support.

A ``CnrsHJet`` is a finite local analytic representation around a specified
expansion point.  If ``center = s0`` and the stored CNRS-H coefficients are
``[d0, d1, ..., dN]``, the represented local expansion is

    f(s) ~= sum_n d_n * (s - s0)**n / n!.

This makes the expansion point explicit.  It is a finite computational object:
it supports structural differentiation, integration, multiplication,
composition, and chain-rule verification to the chosen truncation order.  It is
not a full global analytic-continuation engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .cnrs_h import CnrsH
from . import symbolic as sy
from .cnrs_h_bridge import UnsupportedBridgeExpression, _eval_symbolic_scalar
from .cnrs_h_chain import compose_series, max_coeff_error, multiply_truncated, truncate_pad
from .cnrs_h_domain import CnrsHDomain, combine_domains, domain_from_radius, estimate_next_term_error, infer_symbolic_domain
from .symbolic import BranchState, DEFAULT_BRANCH_STATE
from .cnrs_h_branch import branch_merge_report, merge_branch_states, branch_note_for_composition


class CnrsHJetError(ValueError):
    """Raised for unsupported CNRS-H jet operations."""


def _check_order(order: int) -> None:
    if order <= 0:
        raise ValueError("order must be positive")


def _as_center(z: complex | float | int) -> complex:
    c = complex(z)
    if abs(c.imag) < 1e-15:
        return complex(c.real, 0.0)
    return c


def _centers_close(a: complex, b: complex, tol: float = 1e-12) -> bool:
    return abs(complex(a) - complex(b)) <= tol


def _eval_expr_scalar(expr: sy.Expr, env: Mapping[str, Any] | None = None, *, L: int = 18) -> complex:
    """Evaluate a symbolic expression as a Python complex number.

    This uses the bridge's scalar evaluator so jet coefficients are not polluted
    by CNRS complex digit-encoding roundoff when exact ordinary complex
    evaluation is sufficient.
    """
    return _eval_symbolic_scalar(sy.sympify(expr), env or {})


@dataclass(frozen=True)
class CnrsHJet:
    """Finite CNRS-H local jet around an explicit expansion point.

    Parameters
    ----------
    series:
        CNRS-H EGF coefficients representing derivatives at ``center``.
    center:
        Expansion point.  The local variable is ``u = s - center``.
    var:
        Name of the expansion variable.
    radius_hint:
        Optional domain/convergence hint.
    domain:
        Optional structured domain metadata.  v0.5.3 uses this for lightweight
        convergence/radius diagnostics.
    truncation_error:
        Optional numerical truncation/error indicator supplied by callers.
    description:
        Optional human-readable provenance string.
    """

    series: CnrsH
    center: complex = 0j
    var: str = "s"
    radius_hint: float | None = None
    domain: CnrsHDomain | None = None
    truncation_error: float | None = None
    branch_state: BranchState = DEFAULT_BRANCH_STATE
    branch_note: str = ""
    path_history: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "center", _as_center(self.center))
        if not isinstance(self.series, CnrsH):
            object.__setattr__(self, "series", CnrsH.from_list(self.series))
        if self.domain is None and self.radius_hint is not None:
            object.__setattr__(
                self,
                "domain",
                domain_from_radius(self.radius_hint, note="legacy radius_hint", confidence="hint"),
            )
        elif self.domain is not None and self.radius_hint is None:
            object.__setattr__(self, "radius_hint", self.domain.radius)
        if self.branch_state is None:
            object.__setattr__(self, "branch_state", DEFAULT_BRANCH_STATE)
        object.__setattr__(self, "path_history", tuple(self.path_history or ()))

    @property
    def order(self) -> int:
        return self.series.length

    @property
    def coeffs(self) -> tuple:
        return self.series.coeffs

    def coeff(self, n: int) -> Any:
        return self.series.coeff(n)

    def truncate(self, order: int) -> "CnrsHJet":
        _check_order(order)
        return CnrsHJet(
            truncate_pad(self.series, order),
            center=self.center,
            var=self.var,
            radius_hint=self.radius_hint,
            domain=self.domain,
            truncation_error=self.truncation_error,
            branch_state=self.branch_state,
            branch_note=self.branch_note,
            path_history=self.path_history,
            description=self.description,
        )

    def pad(self, order: int) -> "CnrsHJet":
        return self.truncate(order)

    def evaluate(self, s: complex | float | int) -> complex:
        """Evaluate the local truncated expansion at the physical coordinate ``s``."""
        return self.series.evaluate(complex(s) - self.center)

    __call__ = evaluate

    def valid_for(self, s: complex | float | int, *, strict: bool = True) -> bool | None:
        """Return whether ``s`` lies inside the known/hinted local domain.

        Returns ``None`` when no radius information is available.
        """
        if self.domain is None:
            return None
        return self.domain.valid_for(self.center, s, strict=strict)

    def distance_to_boundary(self, s: complex | float | int) -> float | None:
        """Signed distance from ``s`` to the known/hinted convergence boundary."""
        if self.domain is None:
            return None
        return self.domain.distance_to_boundary(self.center, s)

    def estimate_truncation_error(self, s: complex | float | int) -> float | None:
        """Return a simple last-retained-term truncation indicator at ``s``."""
        return estimate_next_term_error(self, s)

    def with_domain(self, domain: CnrsHDomain | None) -> "CnrsHJet":
        """Return a copy carrying structured domain metadata."""
        return CnrsHJet(
            self.series,
            center=self.center,
            var=self.var,
            radius_hint=None if domain is None else domain.radius,
            domain=domain,
            truncation_error=self.truncation_error,
            branch_state=self.branch_state,
            branch_note=self.branch_note,
            path_history=self.path_history,
            description=self.description,
        )

    def with_branch_state(self, branch_state: BranchState, *, note: str | None = None) -> "CnrsHJet":
        """Return a copy carrying explicit local CNRS branch-state metadata and path-history metadata."""
        return CnrsHJet(
            self.series,
            center=self.center,
            var=self.var,
            radius_hint=self.radius_hint,
            domain=self.domain,
            truncation_error=self.truncation_error,
            branch_state=branch_state,
            branch_note=self.branch_note if note is None else note,
            description=self.description,
        )

    def branch_summary(self) -> str:
        """Return a compact description of this jet's local branch state."""
        if self.branch_note:
            return f"{self.branch_state} — {self.branch_note}"
        return str(self.branch_state)

    def continue_along(self, path, *, branch_points=None) -> "CnrsHJet":
        """Return a copy with branch state updated by a continuation path.

        This is local path/winding bookkeeping for finite CNRS-H jets.  It does
        not recompute coefficients by analytic continuation; it records how the
        branch state changes along a supplied piecewise-linear path.
        """
        from .cnrs_h_path import (
            BranchPoint,
            winding_events,
            update_branch_state_along_path,
            path_history_note,
        )

        bps = branch_points or (BranchPoint(0j, kind="log", label="0"),)
        events = winding_events(path, bps)
        new_state = update_branch_state_along_path(self.branch_state, path, bps)
        note = path_history_note(path, events)
        return CnrsHJet(
            self.series,
            center=self.center,
            var=self.var,
            radius_hint=self.radius_hint,
            domain=self.domain,
            truncation_error=self.truncation_error,
            branch_state=new_state,
            branch_note=note,
            path_history=self.path_history + (note,),
            description=self.description,
        )

    continue_path = continue_along

    def _require_same_center(self, other: "CnrsHJet") -> None:
        if self.var != other.var:
            raise CnrsHJetError(f"jet variables differ: {self.var!r} vs {other.var!r}")
        if not _centers_close(self.center, other.center):
            raise CnrsHJetError(
                f"jet centers differ: {self.center!r} vs {other.center!r}; "
                "shift or rebuild one jet at the other's center first"
            )

    def __add__(self, other: "CnrsHJet") -> "CnrsHJet":
        if not isinstance(other, CnrsHJet):
            return NotImplemented
        self._require_same_center(other)
        order = max(self.order, other.order)
        return CnrsHJet(
            truncate_pad(self.series, order) + truncate_pad(other.series, order),
            center=self.center,
            var=self.var,
            radius_hint=_combine_radius(self.radius_hint, other.radius_hint),
            domain=combine_domains(self.domain or domain_from_radius(self.radius_hint), other.domain or domain_from_radius(other.radius_hint)),
            branch_state=merge_branch_states(self.branch_state, other.branch_state).state,
            branch_note=merge_branch_states(self.branch_state, other.branch_state).summary(),
            path_history=self.path_history + other.path_history,
            description="sum",
        ).truncate(order)

    def __sub__(self, other: "CnrsHJet") -> "CnrsHJet":
        if not isinstance(other, CnrsHJet):
            return NotImplemented
        self._require_same_center(other)
        order = max(self.order, other.order)
        return CnrsHJet(
            truncate_pad(self.series, order) - truncate_pad(other.series, order),
            center=self.center,
            var=self.var,
            radius_hint=_combine_radius(self.radius_hint, other.radius_hint),
            domain=combine_domains(self.domain or domain_from_radius(self.radius_hint), other.domain or domain_from_radius(other.radius_hint)),
            branch_state=merge_branch_states(self.branch_state, other.branch_state).state,
            branch_note=merge_branch_states(self.branch_state, other.branch_state).summary(),
            path_history=self.path_history + other.path_history,
            description="difference",
        ).truncate(order)

    def __neg__(self) -> "CnrsHJet":
        return CnrsHJet(-self.series, center=self.center, var=self.var, radius_hint=self.radius_hint, domain=self.domain, truncation_error=self.truncation_error, branch_state=self.branch_state, branch_note=self.branch_note, path_history=self.path_history, description="negated")

    def __mul__(self, other: object) -> "CnrsHJet":
        if isinstance(other, CnrsHJet):
            self._require_same_center(other)
            order = max(self.order, other.order)
            return CnrsHJet(
                multiply_truncated(self.series, other.series, order=order),
                center=self.center,
                var=self.var,
                radius_hint=_combine_radius(self.radius_hint, other.radius_hint),
                domain=combine_domains(self.domain or domain_from_radius(self.radius_hint), other.domain or domain_from_radius(other.radius_hint)),
                branch_state=merge_branch_states(self.branch_state, other.branch_state).state,
                branch_note=merge_branch_states(self.branch_state, other.branch_state).summary(),
                description="product",
            )
        try:
            scalar = complex(other)  # type: ignore[arg-type]
        except TypeError:
            return NotImplemented
        return CnrsHJet(self.series * scalar, center=self.center, var=self.var, radius_hint=self.radius_hint, domain=self.domain, truncation_error=self.truncation_error, branch_state=self.branch_state, branch_note=self.branch_note, path_history=self.path_history, description=self.description)

    def __rmul__(self, other: object) -> "CnrsHJet":
        return self.__mul__(other)

    def diff(self, *, order: int | None = None) -> "CnrsHJet":
        """Differentiate by native CNRS-H coefficient shift, preserving center."""
        out = self.series.differentiate()
        if order is not None:
            out = truncate_pad(out, order)
        return CnrsHJet(out, center=self.center, var=self.var, radius_hint=self.radius_hint, domain=self.domain, truncation_error=self.truncation_error, branch_state=self.branch_state, branch_note=self.branch_note, path_history=self.path_history, description=f"D({self.description})".strip())

    differentiate = diff
    D = diff

    def integrate(self, constant: complex = 0, *, order: int | None = None) -> "CnrsHJet":
        """Integrate by native CNRS-H reverse shift, preserving center."""
        out = self.series.integrate(constant)
        if order is not None:
            out = truncate_pad(out, order)
        return CnrsHJet(out, center=self.center, var=self.var, radius_hint=self.radius_hint, domain=self.domain, truncation_error=self.truncation_error, branch_state=self.branch_state, branch_note=self.branch_note, path_history=self.path_history, description=f"Int({self.description})".strip())

    def compose(self, inner: "CnrsHJet", *, order: int | None = None) -> "CnrsHJet":
        """Return the local jet for ``self(inner(s))``.

        ``self`` is an outer function expanded around ``x = self.center``.
        ``inner`` is a function of ``s`` expanded around ``s = inner.center``.
        Composition is computed by expanding the outer series in
        ``inner(s) - self.center`` and truncating to ``order``.
        """
        if self.var == inner.var:
            # Same names are fine: outer variable is local/dummy for composition.
            pass
        n = order or min(self.order, inner.order)
        _check_order(n)
        outer = truncate_pad(self.series, n)
        inner_shift = list(truncate_pad(inner.series, n).coeffs)
        inner_shift[0] = inner_shift[0] - self.center
        shifted = CnrsH.from_list(inner_shift)
        composed = compose_series(outer, shifted, order=n)
        return CnrsHJet(
            composed,
            center=inner.center,
            var=inner.var,
            radius_hint=inner.radius_hint,
            domain=inner.domain,
            branch_state=merge_branch_states(self.branch_state, inner.branch_state).state,
            branch_note=branch_note_for_composition(self.branch_state, inner.branch_state),
            path_history=self.path_history + inner.path_history,
            description=f"{self.description or 'outer'}∘{inner.description or 'inner'}",
        )

    def chain_lhs(self, inner: "CnrsHJet", *, order: int) -> "CnrsHJet":
        """Compute ``D(self o inner)`` as a local jet."""
        return self.compose(inner, order=order + 1).diff(order=order)

    def chain_rhs(self, inner: "CnrsHJet", *, order: int) -> "CnrsHJet":
        """Compute ``(D self o inner) * D inner`` as a local jet."""
        pulled = self.diff(order=order).compose(inner, order=order)
        din = inner.diff(order=order)
        return (pulled * din).truncate(order)

    def shift_center(self, new_center: complex | float | int, *, order: int | None = None) -> "CnrsHJet":
        """Re-expand this finite jet around a nearby new center.

        This translates the finite polynomial represented by the current jet.
        Because only finite coefficients are known, omitted higher-order terms
        are not recovered.  It is therefore exact for polynomial jets and a
        finite-order re-expansion for truncated analytic jets.
        """
        n = order or self.order
        _check_order(n)
        delta = complex(new_center) - self.center
        identity_shift = CnrsH.from_list([delta, 1] + [0] * max(0, n - 2))
        new_series = compose_series(truncate_pad(self.series, n), identity_shift, order=n)
        return CnrsHJet(
            new_series,
            center=new_center,
            var=self.var,
            radius_hint=self.radius_hint,
            domain=self.domain,
            truncation_error=self.truncation_error,
            branch_state=self.branch_state,
            branch_note=self.branch_note,
            path_history=self.path_history,
            description=f"shift_center({self.description})".strip(),
        )

    def max_coeff_error(self, other: "CnrsHJet") -> float:
        self._require_same_center(other)
        return max_coeff_error(self.series, other.series)

    def pretty(self) -> str:
        u = f"({self.var} - {self.center:g})" if abs(self.center) > 1e-15 else self.var
        return self.series.pretty(var=u)


def _combine_radius(a: float | None, b: float | None) -> float | None:
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


def jet_from_cnrsh(series: CnrsH, *, center: complex | float | int = 0, var: str = "s", radius_hint: float | None = None, domain: CnrsHDomain | None = None, truncation_error: float | None = None, branch_state: BranchState = DEFAULT_BRANCH_STATE, branch_note: str = "", path_history: tuple[str, ...] = (), description: str = "") -> CnrsHJet:
    """Wrap an existing CNRS-H coefficient object as a local jet."""
    return CnrsHJet(series, center=center, var=var, radius_hint=radius_hint, domain=domain, truncation_error=truncation_error, branch_state=branch_state, branch_note=branch_note, path_history=path_history, description=description)


def jet_constant(value: complex | float | int, *, center: complex | float | int = 0, var: str = "s", order: int = 12) -> CnrsHJet:
    _check_order(order)
    return CnrsHJet(CnrsH.from_list([complex(value)] + [0] * (order - 1)), center=center, var=var, domain=domain_from_radius(float("inf"), note="constant is entire", confidence="known"), description="constant")


def jet_identity(*, center: complex | float | int = 0, var: str = "s", order: int = 12) -> CnrsHJet:
    """Local identity ``s`` around center: center + (s-center)."""
    _check_order(order)
    return CnrsHJet(CnrsH.from_list([complex(center), 1] + [0] * max(0, order - 2)), center=center, var=var, domain=domain_from_radius(float("inf"), note="identity is entire", confidence="known"), description=var)


def jet_from_symbolic(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    center: complex | float | int = 0,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    L: int = 18,
    radius_hint: float | None = None,
    domain: CnrsHDomain | None = None,
    truncation_error: float | None = None,
    branch_state: BranchState | None = None,
    description: str = "",
) -> CnrsHJet:
    """Build a CNRS-H jet by evaluating symbolic derivatives at ``center``.

    Coefficient ``n`` is ``d_n = f^(n)(center)``.  This conservative route is
    slower than closed-form bridge conversion but supports nonzero expansion
    points and provides an explicit local analytic object.
    """
    _check_order(order)
    vname = var.name if isinstance(var, sy.Var) else str(var)
    env0 = dict(env or {})
    env0[vname] = complex(center)
    e = sy.sympify(expr)
    coeffs = []
    current = e
    for n in range(order):
        try:
            coeffs.append(_eval_expr_scalar(current, env0, L=L))
        except Exception as exc:  # pragma: no cover - error path sanity
            raise UnsupportedBridgeExpression(
                f"cannot evaluate derivative order {n} at center {center!r}: {current!r}"
            ) from exc
        current = sy.diff(current, vname).simplify()
    if domain is None:
        inferred = infer_symbolic_domain(e, vname, center=center, env=env)
        if radius_hint is not None:
            domain = domain_from_radius(radius_hint, note="caller radius_hint", confidence="hint")
        else:
            domain = inferred
    branch_report = branch_merge_report(e)
    effective_branch_state = branch_state or branch_report.state
    branch_note = branch_report.summary() if effective_branch_state != DEFAULT_BRANCH_STATE or branch_report.has_conflicts else ""
    return CnrsHJet(
        CnrsH.from_list(coeffs),
        center=center,
        var=vname,
        radius_hint=radius_hint,
        domain=domain,
        truncation_error=truncation_error,
        branch_state=effective_branch_state,
        branch_note=branch_note,
        path_history=(),
        description=description or str(e),
    )


@dataclass(frozen=True)
class JetChainRuleComparison:
    """Result of a CNRS-H jet chain-rule comparison."""

    lhs: CnrsHJet
    rhs: CnrsHJet
    max_error: float
    passed: bool


def verify_jet_chain_rule(
    outer: CnrsHJet,
    inner: CnrsHJet,
    *,
    order: int = 12,
    atol: float = 1e-10,
) -> JetChainRuleComparison:
    """Verify the CNRS-H local-jet chain rule to finite order."""
    lhs = outer.chain_lhs(inner, order=order)
    rhs = outer.chain_rhs(inner, order=order)
    err = lhs.max_coeff_error(rhs)
    return JetChainRuleComparison(lhs, rhs, err, err <= atol)


__all__ = [
    "CnrsHJet",
    "CnrsHJetError",
    "CnrsHDomain",
    "JetChainRuleComparison",
    "jet_from_cnrsh",
    "jet_from_symbolic",
    "jet_constant",
    "jet_identity",
    "verify_jet_chain_rule",
    "BranchState",
]
