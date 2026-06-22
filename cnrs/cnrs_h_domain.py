"""
cnrs.cnrs_h_domain
===================

Lightweight convergence-domain metadata for CNRS-H local jets.

The toolkit's CNRS-H jets are finite local coefficient representations.  This
module adds conservative metadata about where such a local representation should
be treated as valid.  It is deliberately modest: it records known singularities,
radius hints, and truncation-error estimates for simple supported expressions.
It is not a global analytic-continuation or proof engine.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence

from . import symbolic as sy
from .cnrs_h_bridge import _eval_symbolic_scalar


INF = float("inf")


@dataclass(frozen=True)
class CnrsHDomain:
    """Conservative local-domain metadata for a CNRS-H jet.

    Parameters
    ----------
    radius:
        Distance from the expansion center to the nearest known singularity.
        ``math.inf`` means known-entire for the supported expression class;
        ``None`` means unknown.
    singularities:
        Known singular points in the expansion variable's coordinate plane.
    note:
        Human-readable explanation of the inference.
    confidence:
        ``"known"`` for simple exact inferences, ``"hint"`` for metadata
        supplied by the caller or propagated through operations, and
        ``"unknown"`` when the domain has not been inferred.
    """

    radius: float | None = None
    singularities: tuple[complex, ...] = ()
    note: str = "unknown domain"
    confidence: str = "unknown"

    @property
    def is_known(self) -> bool:
        return self.confidence in {"known", "hint"} and self.radius is not None

    @property
    def is_entire(self) -> bool:
        return self.radius == INF

    def valid_for(self, center: complex | float | int, point: complex | float | int, *, strict: bool = True) -> bool | None:
        """Return whether ``point`` is inside the hinted local disk.

        Returns ``None`` when the radius is unknown.  Infinite radius always
        returns ``True``.
        """
        if self.radius is None:
            return None
        if self.radius == INF:
            return True
        distance = abs(complex(point) - complex(center))
        return distance < self.radius if strict else distance <= self.radius

    def distance_to_boundary(self, center: complex | float | int, point: complex | float | int) -> float | None:
        """Return signed distance from ``point`` to the hinted radius boundary.

        Positive means inside the hinted disk; negative means outside.  Returns
        ``None`` if radius is unknown and ``math.inf`` if the expression is
        known entire.
        """
        if self.radius is None:
            return None
        if self.radius == INF:
            return INF
        return self.radius - abs(complex(point) - complex(center))

    def with_radius(self, radius: float | None, *, note: str | None = None, confidence: str | None = None) -> "CnrsHDomain":
        return CnrsHDomain(radius, self.singularities, note or self.note, confidence or self.confidence)


def _merge_notes(*domains: CnrsHDomain) -> str:
    notes = [d.note for d in domains if d.note]
    return "; ".join(dict.fromkeys(notes)) or "combined domain"


def combine_domains(*domains: CnrsHDomain) -> CnrsHDomain:
    """Combine local-domain metadata conservatively by taking the nearest boundary."""
    clean = [d for d in domains if d is not None]
    if not clean:
        return CnrsHDomain()
    radii = [d.radius for d in clean if d.radius is not None]
    radius = min(radii) if radii else None
    singularities: list[complex] = []
    for d in clean:
        for z in d.singularities:
            if not any(abs(z - old) <= 1e-12 for old in singularities):
                singularities.append(z)
    if all(d.confidence == "known" for d in clean) and radius is not None:
        confidence = "known"
    elif any(d.confidence in {"known", "hint"} for d in clean):
        confidence = "hint"
    else:
        confidence = "unknown"
    return CnrsHDomain(radius, tuple(singularities), _merge_notes(*clean), confidence)


def domain_from_radius(radius: float | None, *, singularities: Sequence[complex] = (), note: str = "radius hint", confidence: str = "hint") -> CnrsHDomain:
    """Build a domain metadata object from a simple radius hint."""
    return CnrsHDomain(radius, tuple(complex(z) for z in singularities), note, confidence)


def _as_var_name(var: str | sy.Var) -> str:
    return var.name if isinstance(var, sy.Var) else str(var)


def _contains(expr: Any, var: str) -> bool:
    try:
        return sy._contains_var(expr, var)  # type: ignore[attr-defined]
    except Exception:
        return True


def _eval(expr: sy.Expr, env: Mapping[str, Any] | None) -> complex:
    return _eval_symbolic_scalar(expr, env or {})


def _affine_coeffs(expr: sy.Expr, var: str, env: Mapping[str, Any] | None) -> tuple[complex, complex] | None:
    """Return ``a, b`` for ``a*var + b`` when this can be checked locally."""
    expr = sy.sympify(expr).simplify()
    try:
        deriv = sy.diff(expr, var).simplify()
        if _contains(deriv, var):
            return None
        a = _eval(deriv, env)
        env0 = dict(env or {})
        env0[var] = 0
        b = _eval(expr, env0)
        return a, b
    except Exception:
        return None


def _radius_from_singularity(center: complex, singularity: complex) -> float:
    return abs(complex(singularity) - complex(center))


def _pow_nonnegative_integer(expr: sy.Pow) -> bool:
    if not isinstance(expr.right, sy.Const):
        return False
    z = complex(expr.right.value)
    if abs(z.imag) > 1e-14:
        return False
    n = int(round(z.real))
    return n >= 0 and abs(z.real - n) <= 1e-14


def infer_symbolic_domain(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    center: complex | float | int = 0,
    env: Mapping[str, Any] | None = None,
) -> CnrsHDomain:
    """Infer conservative local-domain metadata for a small symbolic subset.

    Supported exact inferences include polynomials, exp/sin/cos of supported
    arguments, division by affine denominators, and log/sqrt of affine
    arguments.  Unknown cases return a domain with ``radius=None`` rather than
    guessing.
    """
    vname = _as_var_name(var)
    c = complex(center)
    e = sy.sympify(expr).simplify()

    if isinstance(e, sy.Const):
        return CnrsHDomain(INF, (), "constant is entire", "known")

    if isinstance(e, sy.Var):
        if e.name == vname:
            return CnrsHDomain(INF, (), "identity is entire", "known")
        return CnrsHDomain(INF, (), "parameter is entire in expansion variable", "known")

    if isinstance(e, sy.Neg):
        return infer_symbolic_domain(e.arg, vname, center=c, env=env)

    if isinstance(e, (sy.Add, sy.Sub, sy.Mul)):
        return combine_domains(
            infer_symbolic_domain(e.left, vname, center=c, env=env),
            infer_symbolic_domain(e.right, vname, center=c, env=env),
        )

    if isinstance(e, sy.Div):
        num_domain = infer_symbolic_domain(e.left, vname, center=c, env=env)
        den_domain = infer_symbolic_domain(e.right, vname, center=c, env=env)
        aff = _affine_coeffs(e.right, vname, env)
        if aff is not None:
            a, b = aff
            if abs(a) > 1e-14:
                pole = -b / a
                pole_domain = CnrsHDomain(_radius_from_singularity(c, pole), (pole,), f"affine denominator pole at {pole:g}", "known")
                return combine_domains(num_domain, den_domain, pole_domain)
            try:
                if abs(_eval(e.right, {**(env or {}), vname: c})) <= 1e-14:
                    return CnrsHDomain(0.0, (c,), "denominator vanishes at expansion center", "known")
            except Exception:
                pass
        return combine_domains(num_domain, den_domain, CnrsHDomain(None, (), "denominator domain unknown", "unknown"))

    if isinstance(e, sy.Pow):
        base_domain = infer_symbolic_domain(e.left, vname, center=c, env=env)
        if _pow_nonnegative_integer(e):
            return base_domain
        # Non-integer powers are branch-sensitive at base=0 when the base is affine.
        aff = _affine_coeffs(e.left, vname, env)
        if aff is not None:
            a, b = aff
            if abs(a) > 1e-14:
                branch_point = -b / a
                return combine_domains(base_domain, CnrsHDomain(_radius_from_singularity(c, branch_point), (branch_point,), f"power branch point at {branch_point:g}", "known"))
        return combine_domains(base_domain, CnrsHDomain(None, (), "power branch domain unknown", "unknown"))

    if isinstance(e, (sy.Exp, sy.Sin, sy.Cos)):
        return infer_symbolic_domain(e.arg, vname, center=c, env=env)

    if isinstance(e, sy.Log):
        arg_domain = infer_symbolic_domain(e.arg, vname, center=c, env=env)
        aff = _affine_coeffs(e.arg, vname, env)
        if aff is not None:
            a, b = aff
            if abs(a) > 1e-14:
                branch_point = -b / a
                return combine_domains(arg_domain, CnrsHDomain(_radius_from_singularity(c, branch_point), (branch_point,), f"log branch point at {branch_point:g}", "known"))
            try:
                val = _eval(e.arg, {**(env or {}), vname: c})
                if abs(val) <= 1e-14:
                    return CnrsHDomain(0.0, (c,), "log singular at expansion center", "known")
                return arg_domain
            except Exception:
                pass
        return combine_domains(arg_domain, CnrsHDomain(None, (), "log branch domain unknown", "unknown"))

    if isinstance(e, sy.Sqrt):
        arg_domain = infer_symbolic_domain(e.arg, vname, center=c, env=env)
        aff = _affine_coeffs(e.arg, vname, env)
        if aff is not None:
            a, b = aff
            if abs(a) > 1e-14:
                branch_point = -b / a
                return combine_domains(arg_domain, CnrsHDomain(_radius_from_singularity(c, branch_point), (branch_point,), f"sqrt branch point at {branch_point:g}", "known"))
        return combine_domains(arg_domain, CnrsHDomain(None, (), "sqrt branch domain unknown", "unknown"))

    return CnrsHDomain(None, (), f"unsupported domain inference for {type(e).__name__}", "unknown")


def estimate_next_term_error(jet: Any, point: complex | float | int) -> float | None:
    """Estimate a simple next/last-term truncation indicator for a jet.

    This is not a rigorous error bound.  It reports the magnitude of the last
    retained EGF term at ``point`` and is useful as a convergence/diagnostic
    signal when increasing the order.
    """
    try:
        order = jet.order
        if order <= 0:
            return None
        n = order - 1
        u = complex(point) - complex(jet.center)
        coeff = complex(jet.coeff(n))
        return abs(coeff * (u ** n) / math.factorial(n))
    except Exception:
        return None


__all__ = [
    "CnrsHDomain",
    "INF",
    "combine_domains",
    "domain_from_radius",
    "infer_symbolic_domain",
    "estimate_next_term_error",
]
