"""
cnrs.cnrs_h_taylor_model
========================

Lightweight Taylor-model-style remainder metadata for CNRS-H local jets.

A ``CnrsHTaylorModel`` pairs a finite local jet with a conservative numerical
remainder bound.  It is intended to make truncation explicit when using finite
CNRS-H coefficient objects.  The implementation is deliberately modest: bounds
are heuristic/local indicators unless the caller supplies a trusted bound.

This module does not prove global convergence or perform interval arithmetic.
It provides a structured place to carry finite-order error information through
basic CNRS-H jet operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Any

from .cnrs_h_jet import CnrsHJet, jet_from_symbolic, verify_jet_chain_rule
from .cnrs_h_domain import estimate_next_term_error


class TaylorModelError(ValueError):
    """Raised for unsupported Taylor-model-style operations."""


def _as_bound(x: float | int | None) -> float | None:
    if x is None:
        return None
    b = float(x)
    if b < 0:
        raise ValueError("remainder_bound must be non-negative")
    return b


def _sum_bounds(*bounds: float | None) -> float | None:
    clean = [b for b in bounds if b is not None]
    if len(clean) != len(bounds):
        return None
    return float(sum(clean))


def _mul_bound(a_value: complex, a_bound: float | None, b_value: complex, b_bound: float | None) -> float | None:
    """Conservative product remainder bound at a point.

    If A = a + ra and B = b + rb with |ra|<=Ra, |rb|<=Rb, then
    |AB - ab| <= |a|Rb + |b|Ra + Ra Rb.
    """
    if a_bound is None or b_bound is None:
        return None
    return abs(a_value) * b_bound + abs(b_value) * a_bound + a_bound * b_bound


@dataclass(frozen=True)
class CnrsHTaylorModel:
    """Finite CNRS-H local jet plus an explicit remainder/error bound.

    Parameters
    ----------
    jet:
        The finite CNRS-H local jet.
    remainder_bound:
        Optional non-negative numerical remainder bound.  The bound is usually
        local to a chosen evaluation point or neighbourhood, depending on the
        provenance.  ``None`` means unknown.
    bound_kind:
        Short label describing the meaning of the bound, e.g. ``"heuristic"``
        or ``"caller_supplied"``.
    provenance:
        Human-readable explanation of how the model was formed.
    """

    jet: CnrsHJet
    remainder_bound: float | None = None
    bound_kind: str = "unknown"
    provenance: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "remainder_bound", _as_bound(self.remainder_bound))

    @property
    def center(self) -> complex:
        return self.jet.center

    @property
    def order(self) -> int:
        return self.jet.order

    @property
    def var(self) -> str:
        return self.jet.var

    @property
    def domain(self):
        return self.jet.domain

    def evaluate(self, point: complex | float | int) -> complex:
        """Evaluate the polynomial/jet part at ``point``."""
        return self.jet.evaluate(point)

    __call__ = evaluate

    def enclosure(self, point: complex | float | int) -> tuple[complex, float | None]:
        """Return ``(value, radius)`` for a disk enclosure at ``point``.

        The radius is the stored remainder bound when known.  No interval or
        ball arithmetic is implied; this is a lightweight diagnostic object.
        """
        return self.evaluate(point), self.remainder_bound

    def valid_for(self, point: complex | float | int, *, strict: bool = True) -> bool | None:
        return self.jet.valid_for(point, strict=strict)

    def distance_to_boundary(self, point: complex | float | int) -> float | None:
        return self.jet.distance_to_boundary(point)

    def with_remainder(self, bound: float | None, *, kind: str | None = None, provenance: str | None = None) -> "CnrsHTaylorModel":
        return CnrsHTaylorModel(self.jet, bound, kind or self.bound_kind, provenance or self.provenance)

    def diff(self, *, order: int | None = None) -> "CnrsHTaylorModel":
        """Differentiate the jet part and carry the bound as unknown.

        A rigorous derivative remainder bound requires domain-specific estimates;
        v0.5.4 therefore preserves the structural derivative but marks the new
        bound as unknown rather than pretending to certify it.
        """
        return CnrsHTaylorModel(self.jet.diff(order=order), None, "unknown_after_diff", f"D({self.provenance or self.jet.description})")

    differentiate = diff
    D = diff

    def integrate(self, constant: complex = 0, *, order: int | None = None) -> "CnrsHTaylorModel":
        """Integrate the jet part and carry the bound as unknown."""
        return CnrsHTaylorModel(self.jet.integrate(constant, order=order), None, "unknown_after_integrate", f"Int({self.provenance or self.jet.description})")

    def __add__(self, other: "CnrsHTaylorModel") -> "CnrsHTaylorModel":
        if not isinstance(other, CnrsHTaylorModel):
            return NotImplemented
        return CnrsHTaylorModel(
            self.jet + other.jet,
            _sum_bounds(self.remainder_bound, other.remainder_bound),
            "propagated" if self.remainder_bound is not None and other.remainder_bound is not None else "unknown",
            "sum",
        )

    def __sub__(self, other: "CnrsHTaylorModel") -> "CnrsHTaylorModel":
        if not isinstance(other, CnrsHTaylorModel):
            return NotImplemented
        return CnrsHTaylorModel(
            self.jet - other.jet,
            _sum_bounds(self.remainder_bound, other.remainder_bound),
            "propagated" if self.remainder_bound is not None and other.remainder_bound is not None else "unknown",
            "difference",
        )

    def __mul__(self, other: object) -> "CnrsHTaylorModel":
        if isinstance(other, CnrsHTaylorModel):
            # Bound propagation for products depends on where the model is used.
            # Use the shared expansion center as a conservative local diagnostic.
            self.jet._require_same_center(other.jet)  # noqa: SLF001 - internal consistency reuse
            a0 = self.evaluate(self.center)
            b0 = other.evaluate(other.center)
            return CnrsHTaylorModel(
                self.jet * other.jet,
                _mul_bound(a0, self.remainder_bound, b0, other.remainder_bound),
                "local_center_propagated" if self.remainder_bound is not None and other.remainder_bound is not None else "unknown",
                "product",
            )
        try:
            scalar = complex(other)  # type: ignore[arg-type]
        except TypeError:
            return NotImplemented
        bound = None if self.remainder_bound is None else abs(scalar) * self.remainder_bound
        return CnrsHTaylorModel(self.jet * scalar, bound, self.bound_kind, self.provenance)

    def __rmul__(self, other: object) -> "CnrsHTaylorModel":
        return self.__mul__(other)

    def compose(self, inner: "CnrsHTaylorModel", *, order: int | None = None) -> "CnrsHTaylorModel":
        """Compose Taylor-model jet parts and mark the bound as unknown.

        Rigorous composition bounds require a validated neighbourhood for the
        image of the inner model.  The finite jet composition is still useful,
        but v0.5.4 does not claim a certified composition remainder.
        """
        if not isinstance(inner, CnrsHTaylorModel):
            raise TaylorModelError("compose expects a CnrsHTaylorModel inner argument")
        return CnrsHTaylorModel(
            self.jet.compose(inner.jet, order=order),
            None,
            "unknown_after_compose",
            f"{self.provenance or 'outer'}∘{inner.provenance or 'inner'}",
        )

    def shift_center(self, new_center: complex | float | int, *, order: int | None = None) -> "CnrsHTaylorModel":
        return CnrsHTaylorModel(self.jet.shift_center(new_center, order=order), None, "unknown_after_shift", f"shift_center({self.provenance})")


def taylor_model_from_jet(
    jet: CnrsHJet,
    *,
    sample_point: complex | float | int | None = None,
    remainder_bound: float | None = None,
    bound_kind: str | None = None,
    provenance: str | None = None,
) -> CnrsHTaylorModel:
    """Build a Taylor-model wrapper around an existing jet.

    If ``remainder_bound`` is omitted and ``sample_point`` is supplied, the
    model uses the existing v0.5.3 last-retained-term indicator at that sample
    point.  This is a heuristic diagnostic, not a proof-grade bound.
    """
    if remainder_bound is None and sample_point is not None:
        remainder_bound = estimate_next_term_error(jet, sample_point)
        bound_kind = bound_kind or "last_retained_term_indicator"
    return CnrsHTaylorModel(jet, remainder_bound, bound_kind or "caller_supplied" if remainder_bound is not None else "unknown", provenance or jet.description)


def taylor_model_from_symbolic(
    expr: Any,
    var: str | Any = "s",
    *,
    center: complex | float | int = 0,
    order: int = 12,
    sample_point: complex | float | int | None = None,
    env: dict[str, Any] | None = None,
    remainder_bound: float | None = None,
) -> CnrsHTaylorModel:
    """Build a finite CNRS-H Taylor model from a symbolic expression."""
    jet = jet_from_symbolic(expr, var, center=center, order=order, env=env)
    return taylor_model_from_jet(jet, sample_point=sample_point, remainder_bound=remainder_bound, provenance=str(expr))


@dataclass(frozen=True)
class TaylorModelChainRuleComparison:
    """Chain-rule comparison for Taylor-model jet parts."""

    lhs: CnrsHTaylorModel
    rhs: CnrsHTaylorModel
    max_error: float
    passed: bool
    note: str = "remainder bounds are diagnostic, not proof-grade"


def verify_taylor_model_chain_rule(
    outer: CnrsHTaylorModel,
    inner: CnrsHTaylorModel,
    *,
    order: int = 12,
    atol: float = 1e-10,
) -> TaylorModelChainRuleComparison:
    """Verify the CNRS-H chain rule on the finite jet parts of two models."""
    comparison = verify_jet_chain_rule(outer.jet, inner.jet, order=order, atol=atol)
    return TaylorModelChainRuleComparison(
        CnrsHTaylorModel(comparison.lhs, None, "comparison_lhs", "D(f∘g)"),
        CnrsHTaylorModel(comparison.rhs, None, "comparison_rhs", "(Df∘g)Dg"),
        comparison.max_error,
        comparison.passed,
    )


__all__ = [
    "TaylorModelError",
    "CnrsHTaylorModel",
    "TaylorModelChainRuleComparison",
    "taylor_model_from_jet",
    "taylor_model_from_symbolic",
    "verify_taylor_model_chain_rule",
]
