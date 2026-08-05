"""Algebraic-curve input and finite branch-point detection for CNRS.

This module implements the first two automatic-construction stages for a
finite algebraic Riemann surface defined by ``P(z, w) = 0``:

1. parse and validate a bivariate polynomial curve;
2. compute candidate finite branch points from ``P = 0`` and ``dP/dw = 0``.

The calculation is exact when SymPy can factor/solve the relevant resultant.
A numerical root fallback is available for higher-degree resultants.  The
module deliberately does not yet infer monodromy permutations, construct
Puiseux charts, analyze the point at infinity, or normalize singular curves.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


class AlgebraicCurveError(ValueError):
    """Raised for invalid curves or unsuccessful branch analysis."""


def _sympy():
    try:
        import sympy as sp
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise AlgebraicCurveError(
            "algebraic-curve analysis requires SymPy; install cnrs[algebraic]"
        ) from exc
    return sp


@dataclass(frozen=True)
class RamificationPoint:
    """A finite solution of ``P(z,w)=0`` and ``P_w(z,w)=0``.

    ``multiplicity`` is the multiplicity of ``w`` as a root of ``P(z0,w)``
    when it can be determined exactly.  ``residual`` records the maximum
    numerical residual in the two defining equations.
    """

    z: Any
    w: Any
    multiplicity: int | None
    residual: float
    exact: bool


@dataclass(frozen=True)
class BranchPoint:
    """A projected finite branch value with its ramification points."""

    z: Any
    ramification_points: tuple[RamificationPoint, ...]
    resultant_multiplicity: int | None
    exact: bool

    @property
    def total_ramification_excess(self) -> int | None:
        multiplicities = [p.multiplicity for p in self.ramification_points]
        if any(m is None for m in multiplicities):
            return None
        return sum(int(m) - 1 for m in multiplicities)


@dataclass(frozen=True)
class BranchAnalysis:
    """Result of finite branch-point analysis for an algebraic curve."""

    curve: "AlgebraicCurve"
    derivative_w: Any
    resultant: Any
    discriminant: Any | None
    branch_points: tuple[BranchPoint, ...]
    method: str
    warnings: tuple[str, ...] = ()

    @property
    def finite_branch_values(self) -> tuple[Any, ...]:
        return tuple(point.z for point in self.branch_points)


@dataclass(frozen=True)
class AlgebraicCurve:
    """A polynomial relation ``P(z,w)=0`` over a SymPy coefficient domain."""

    expression: Any
    z: Any
    w: Any
    polynomial: Any
    name: str = "algebraic curve"

    @classmethod
    def from_expression(
        cls,
        expression: Any,
        *,
        z: str | Any = "z",
        w: str | Any = "w",
        name: str = "algebraic curve",
        domain: str | None = None,
    ) -> "AlgebraicCurve":
        sp = _sympy()
        z_symbol = sp.Symbol(z) if isinstance(z, str) else z
        w_symbol = sp.Symbol(w) if isinstance(w, str) else w
        if z_symbol == w_symbol:
            raise AlgebraicCurveError("z and w must be different symbols")

        if isinstance(expression, str):
            try:
                expr = sp.sympify(expression, locals={str(z_symbol): z_symbol, str(w_symbol): w_symbol})
            except Exception as exc:
                raise AlgebraicCurveError(f"could not parse polynomial expression: {exc}") from exc
        else:
            expr = sp.sympify(expression)

        unknown_symbols = expr.free_symbols - {z_symbol, w_symbol}
        if unknown_symbols:
            raise AlgebraicCurveError(
                "curve contains unresolved coefficient symbols: "
                + ", ".join(sorted(map(str, unknown_symbols)))
            )
        if expr == 0:
            raise AlgebraicCurveError("curve polynomial cannot be identically zero")

        try:
            poly = sp.Poly(expr, w_symbol, z_symbol, domain=domain) if domain else sp.Poly(expr, w_symbol, z_symbol)
        except Exception as exc:
            raise AlgebraicCurveError("expression must be polynomial in z and w") from exc

        if poly.degree(w_symbol) < 1:
            raise AlgebraicCurveError("curve must have positive degree in w")
        return cls(sp.expand(expr), z_symbol, w_symbol, poly, str(name))

    @property
    def degree_w(self) -> int:
        return int(self.polynomial.degree(self.w))

    @property
    def degree_z(self) -> int:
        return int(self.polynomial.degree(self.z))

    def derivative_w(self) -> Any:
        sp = _sympy()
        return sp.diff(self.expression, self.w)

    def resultant_w(self) -> Any:
        sp = _sympy()
        derivative = self.derivative_w()
        result = sp.resultant(self.expression, derivative, self.w)
        return sp.factor(result)

    def discriminant_w(self) -> Any | None:
        sp = _sympy()
        try:
            return sp.factor(sp.discriminant(self.expression, self.w))
        except Exception:
            return None

    def analyze_finite_branch_points(
        self,
        *,
        numerical: bool = False,
        precision: int = 50,
        tolerance: float = 1e-10,
        maxsteps: int = 200,
    ) -> BranchAnalysis:
        """Compute finite critical values of the projection ``(z,w) -> z``.

        Candidate values are roots of ``Res_w(P, P_w)``.  For each candidate
        ``z0``, the method identifies common roots in ``w`` and reports the
        corresponding ramification points.

        Exact mode is preferred.  Set ``numerical=True`` to use ``nroots`` for
        the resultant and specialized ``w`` polynomials when exact roots are
        unavailable or inconvenient.
        """

        sp = _sympy()
        derivative = self.derivative_w()
        resultant = self.resultant_w()
        discriminant = self.discriminant_w()
        warnings: list[str] = []

        if sp.simplify(resultant) == 0:
            raise AlgebraicCurveError(
                "resultant is identically zero; the curve is non-squarefree in w "
                "or has a repeated component. Normalize/factor the curve first."
            )

        resultant_poly = sp.Poly(resultant, self.z)
        if resultant_poly.degree() <= 0:
            return BranchAnalysis(self, derivative, resultant, discriminant, (), "exact", ())

        if numerical:
            z_roots = _numeric_roots_with_multiplicity(resultant_poly, precision, maxsteps)
            method = "numerical-resultant"
        else:
            z_roots = _exact_roots_with_multiplicity(resultant_poly)
            if z_roots is None:
                z_roots = _numeric_roots_with_multiplicity(resultant_poly, precision, maxsteps)
                method = "numerical-resultant-fallback"
                warnings.append("exact resultant roots were unavailable; numerical roots were used")
            else:
                method = "exact-resultant"

        branch_points: list[BranchPoint] = []
        for z0, z_mult, z_exact in z_roots:
            p_at = sp.Poly(sp.expand(self.expression.subs(self.z, z0)), self.w)
            dp_at = sp.Poly(sp.expand(derivative.subs(self.z, z0)), self.w)
            if p_at.is_zero:
                warnings.append(f"specialization P({z0},w) vanished identically; candidate skipped")
                continue

            if z_exact and not numerical:
                common = sp.gcd(p_at, dp_at)
                roots_dict = sp.roots(common.as_expr(), self.w)
                if sum(roots_dict.values()) < common.degree():
                    numeric_common = _numeric_roots_with_multiplicity(common, precision, maxsteps)
                    w_roots = [(root, mult, False) for root, mult, _ in numeric_common]
                    warnings.append(f"some ramification roots over z={z0} required numerical fallback")
                else:
                    w_roots = [(root, int(mult), True) for root, mult in roots_dict.items()]
            else:
                w_roots = _common_numeric_w_roots(p_at, dp_at, precision, tolerance, maxsteps)

            ramification: list[RamificationPoint] = []
            for w0, common_mult, exact in w_roots:
                multiplicity = _root_multiplicity(p_at, w0, exact=exact, tolerance=tolerance)
                if multiplicity is None and common_mult is not None:
                    multiplicity = int(common_mult) + 1
                residual = _pair_residual(self.expression, derivative, self.z, self.w, z0, w0, precision)
                if residual <= tolerance * 100 or exact:
                    ramification.append(
                        RamificationPoint(z0, w0, multiplicity, residual, bool(exact and z_exact))
                    )

            if ramification:
                branch_points.append(
                    BranchPoint(z0, tuple(ramification), int(z_mult) if z_mult is not None else None, bool(z_exact and all(p.exact for p in ramification)))
                )
            else:
                warnings.append(f"resultant root z={z0} produced no verified common P/P_w root")

        branch_points.sort(key=lambda point: _complex_sort_key(point.z, precision))
        return BranchAnalysis(
            self,
            derivative,
            resultant,
            discriminant,
            tuple(branch_points),
            method,
            tuple(warnings),
        )


def _exact_roots_with_multiplicity(poly: Any) -> list[tuple[Any, int, bool]] | None:
    sp = _sympy()
    roots = sp.roots(poly.as_expr(), poly.gens[0])
    if sum(int(v) for v in roots.values()) != poly.degree():
        return None
    return [(root, int(mult), True) for root, mult in roots.items()]


def _numeric_roots_with_multiplicity(poly: Any, precision: int, maxsteps: int) -> list[tuple[Any, int, bool]]:
    sp = _sympy()
    try:
        roots = list(poly.nroots(n=precision, maxsteps=maxsteps))
    except Exception as exc:
        raise AlgebraicCurveError(f"numerical root calculation failed: {exc}") from exc
    clusters: list[list[Any]] = []
    cluster_tol = 10.0 ** (-max(8, min(14, precision // 3)))
    for root in roots:
        value = complex(root)
        for cluster in clusters:
            if abs(value - complex(cluster[0])) <= cluster_tol:
                cluster.append(root)
                break
        else:
            clusters.append([root])
    return [(sp.N(sum(cluster) / len(cluster), precision), len(cluster), False) for cluster in clusters]


def _common_numeric_w_roots(p_at: Any, dp_at: Any, precision: int, tolerance: float, maxsteps: int) -> list[tuple[Any, int | None, bool]]:
    sp = _sympy()
    roots = _numeric_roots_with_multiplicity(p_at, precision, maxsteps)
    out: list[tuple[Any, int | None, bool]] = []
    for root, p_mult, _ in roots:
        residual = abs(complex(sp.N(dp_at.as_expr().subs(p_at.gens[0], root), precision)))
        if residual <= tolerance * max(1.0, abs(complex(root))):
            out.append((root, max(1, int(p_mult) - 1), False))
    return out


def _root_multiplicity(poly: Any, root: Any, *, exact: bool, tolerance: float) -> int | None:
    sp = _sympy()
    if exact:
        try:
            return int(sp.polys.polytools.degree(sp.gcd(poly, sp.Poly((poly.gens[0] - root) ** poly.degree(), poly.gens[0]))))
        except Exception:
            pass
        count = 0
        q = poly
        while q.degree() >= 0:
            value = sp.simplify(q.as_expr().subs(poly.gens[0], root))
            if value != 0:
                break
            count += 1
            q = q.diff()
        return count or None

    count = 0
    q = poly
    scale = max(1.0, max((abs(complex(c)) for c in q.all_coeffs()), default=1.0))
    while q.degree() >= 0:
        value = abs(complex(sp.N(q.as_expr().subs(poly.gens[0], root), 40)))
        if value > tolerance * scale:
            break
        count += 1
        q = q.diff()
    return count or None


def _pair_residual(expr: Any, derivative: Any, z: Any, w: Any, z0: Any, w0: Any, precision: int) -> float:
    sp = _sympy()
    substitutions = {z: z0, w: w0}
    p_res = abs(complex(sp.N(expr.subs(substitutions), precision)))
    d_res = abs(complex(sp.N(derivative.subs(substitutions), precision)))
    return float(max(p_res, d_res))


def _complex_sort_key(value: Any, precision: int) -> tuple[float, float]:
    sp = _sympy()
    z = complex(sp.N(value, precision))
    return (round(z.real, 14), round(z.imag, 14))


def algebraic_curve(
    expression: Any,
    *,
    z: str | Any = "z",
    w: str | Any = "w",
    name: str = "algebraic curve",
) -> AlgebraicCurve:
    """Convenience constructor for :class:`AlgebraicCurve`."""

    return AlgebraicCurve.from_expression(expression, z=z, w=w, name=name)


def finite_branch_points(
    expression: Any,
    *,
    z: str | Any = "z",
    w: str | Any = "w",
    name: str = "algebraic curve",
    numerical: bool = False,
    precision: int = 50,
    tolerance: float = 1e-10,
) -> BranchAnalysis:
    """Parse ``P(z,w)`` and return its finite branch-point analysis."""

    curve = algebraic_curve(expression, z=z, w=w, name=name)
    return curve.analyze_finite_branch_points(
        numerical=numerical,
        precision=precision,
        tolerance=tolerance,
    )
