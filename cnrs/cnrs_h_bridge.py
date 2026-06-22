"""
cnrs.cnrs_h_bridge
==================

Minimal bridge between the symbolic calculus layer and CNRS-H coefficient
calculus.

The bridge converts a conservative subset of symbolic expressions into a finite
CNRS-H exponential-generating-function representation around the expansion point
s = 0.  If

    f(s) = sum_{n=0}^{N-1} d_n s^n / n!

then the returned ``CnrsH`` stores ``[d0, d1, ..., d_{N-1}]``.  The coefficients
are the derivatives f^(n)(0), so CNRS-H differentiation is the exact digit-shift
operation on the truncated representation.

Supported expressions are deliberately modest:

- constants and the expansion variable;
- polynomial expressions built from +, -, *, and non-negative integer powers;
- division by expressions independent of the expansion variable;
- exp/sin/cos of affine arguments a*s + b, where a and b are independent of s;
- combinations of the above through addition, subtraction, and multiplication.

Unsupported expressions raise ``UnsupportedBridgeExpression`` rather than
pretending to convert them.  This module is a bridge for tested scientific
workflows, not a general computer-algebra series engine.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Any, Mapping

from .cnrs_h import CnrsH
from . import symbolic as sy


class UnsupportedBridgeExpression(ValueError):
    """Raised when a symbolic expression cannot yet be converted to CNRS-H."""


def _as_var_name(var: str | sy.Var) -> str:
    return var.name if isinstance(var, sy.Var) else str(var)


def _is_zero(z: complex, tol: float = 1e-14) -> bool:
    return abs(z) <= tol


def _trim_to_order(h: CnrsH, order: int) -> CnrsH:
    if order <= 0:
        raise ValueError("order must be positive")
    return h.truncate(order).pad(order)


def _eval_symbolic_scalar(expr: sy.Expr, values: Mapping[str, Any] | None = None) -> complex:
    """Evaluate a scalar symbolic expression using ordinary complex arithmetic.

    This avoids the intentionally approximate CnrsComplex encoding path when the
    bridge needs exact Taylor/EGF coefficients for simple expressions.
    """
    values = values or {}
    e = sy.sympify(expr).simplify()
    if isinstance(e, sy.Const):
        return complex(e.value)
    if isinstance(e, sy.Var):
        if e.name not in values:
            raise KeyError(f"no value supplied for variable {e.name!r}")
        return complex(values[e.name])
    if isinstance(e, sy.Neg):
        return -_eval_symbolic_scalar(e.arg, values)
    if isinstance(e, sy.Add):
        return _eval_symbolic_scalar(e.left, values) + _eval_symbolic_scalar(e.right, values)
    if isinstance(e, sy.Sub):
        return _eval_symbolic_scalar(e.left, values) - _eval_symbolic_scalar(e.right, values)
    if isinstance(e, sy.Mul):
        return _eval_symbolic_scalar(e.left, values) * _eval_symbolic_scalar(e.right, values)
    if isinstance(e, sy.Div):
        return _eval_symbolic_scalar(e.left, values) / _eval_symbolic_scalar(e.right, values)
    if isinstance(e, sy.Pow):
        base = _eval_symbolic_scalar(e.left, values)
        exponent = _eval_symbolic_scalar(e.right, values)
        if abs(base) == 0:
            return base ** exponent
        return cmath.exp(exponent * sy.ad.branch_log(base, e.branch))
    if isinstance(e, sy.Exp):
        return cmath.exp(_eval_symbolic_scalar(e.arg, values))
    if isinstance(e, sy.Log):
        return sy.ad.branch_log(_eval_symbolic_scalar(e.arg, values), e.branch)
    if isinstance(e, sy.Sin):
        return cmath.sin(_eval_symbolic_scalar(e.arg, values))
    if isinstance(e, sy.Cos):
        return cmath.cos(_eval_symbolic_scalar(e.arg, values))
    if isinstance(e, sy.Tan):
        return cmath.tan(_eval_symbolic_scalar(e.arg, values))
    if isinstance(e, sy.Sqrt):
        z = _eval_symbolic_scalar(e.arg, values)
        return cmath.exp(0.5 * sy.ad.branch_log(z, e.branch))
    raise UnsupportedBridgeExpression(f"cannot scalar-evaluate expression: {e!r}")


def _eval_independent(expr: sy.Expr, var: str, env: Mapping[str, Any] | None, *, L: int) -> complex:
    """Evaluate an expression that must not contain the expansion variable."""
    if sy._contains_var(expr, var):  # type: ignore[attr-defined]
        raise UnsupportedBridgeExpression(f"expression depends on expansion variable {var!r}: {expr}")
    env2 = dict(env or {})
    # Supply a harmless value for the expansion variable if a nested expression
    # tries to evaluate it through a branch that was already checked.
    env2.setdefault(var, 0)
    return _eval_symbolic_scalar(expr, env2)


def _const_h(value: complex, order: int) -> CnrsH:
    return CnrsH.from_list([value] + [0] * (order - 1))


def _var_h(order: int) -> CnrsH:
    return CnrsH.identity().pad(order).truncate(order)


def _linear_coeffs(expr: sy.Expr, var: str, env: Mapping[str, Any] | None, *, L: int) -> tuple[complex, complex]:
    """Return (a, b) for affine expression a*var + b.

    The detection is derivative-based and conservative: the derivative must be
    independent of var, and expr - a*var must also be independent of var.
    This supports forms such as k*s, s/L, k*s+b, and constants.
    """
    expr = sy.sympify(expr).simplify()
    deriv_expr = expr.diff(var).simplify()
    if sy._contains_var(deriv_expr, var):  # type: ignore[attr-defined]
        raise UnsupportedBridgeExpression(f"non-affine argument: {expr}")
    a = _eval_independent(deriv_expr, var, env, L=L)
    # Evaluate the intercept at var=0.  The derivative check above rules out
    # nonlinear dependence for the supported symbolic layer; using direct
    # evaluation avoids requiring a full algebraic simplifier to prove that
    # (k*s - k*s) is zero.
    env0 = dict(env or {})
    env0[var] = 0
    b = _eval_symbolic_scalar(expr, env0)
    return a, b


def _pow_nonnegative_integer(expr: sy.Pow) -> int | None:
    if not isinstance(expr.right, sy.Const):
        return None
    z = complex(expr.right.value)
    if abs(z.imag) > 1e-14:
        return None
    n_float = z.real
    n = int(round(n_float))
    if n < 0 or abs(n_float - n) > 1e-14:
        return None
    return n


def cnrs_h_from_symbolic(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    L: int = 18,
) -> CnrsH:
    """Convert a supported symbolic expression to a finite ``CnrsH`` series.

    Parameters
    ----------
    expr:
        Symbolic expression or scalar.
    var:
        Expansion variable.  The CNRS-H representation is around ``var = 0``.
    order:
        Number of EGF coefficients to keep.
    env:
        Numeric values for symbolic parameters other than ``var``.
    L:
        Mantissa length passed through to symbolic numeric evaluation.

    Returns
    -------
    CnrsH
        A finite EGF coefficient representation of the supported expression.
    """
    if order <= 0:
        raise ValueError("order must be positive")
    vname = _as_var_name(var)
    e = sy.sympify(expr).simplify()

    if isinstance(e, sy.Const):
        return _const_h(complex(e.value), order)

    if isinstance(e, sy.Var):
        if e.name == vname:
            return _var_h(order)
        return _const_h(_eval_independent(e, vname, env, L=L), order)

    if isinstance(e, sy.Neg):
        return -cnrs_h_from_symbolic(e.arg, vname, order=order, env=env, L=L)

    if isinstance(e, sy.Add):
        return _trim_to_order(
            cnrs_h_from_symbolic(e.left, vname, order=order, env=env, L=L)
            + cnrs_h_from_symbolic(e.right, vname, order=order, env=env, L=L),
            order,
        )

    if isinstance(e, sy.Sub):
        return _trim_to_order(
            cnrs_h_from_symbolic(e.left, vname, order=order, env=env, L=L)
            - cnrs_h_from_symbolic(e.right, vname, order=order, env=env, L=L),
            order,
        )

    if isinstance(e, sy.Mul):
        return _trim_to_order(
            cnrs_h_from_symbolic(e.left, vname, order=order, env=env, L=L)
            * cnrs_h_from_symbolic(e.right, vname, order=order, env=env, L=L),
            order,
        )

    if isinstance(e, sy.Div):
        if sy._contains_var(e.right, vname):  # type: ignore[attr-defined]
            raise UnsupportedBridgeExpression(f"division by variable-dependent expression is not supported: {e}")
        denom = _eval_independent(e.right, vname, env, L=L)
        if _is_zero(denom):
            raise ZeroDivisionError("division by zero in CNRS-H bridge")
        return _trim_to_order(
            cnrs_h_from_symbolic(e.left, vname, order=order, env=env, L=L) * (1 / denom),
            order,
        )

    if isinstance(e, sy.Pow):
        n = _pow_nonnegative_integer(e)
        if n is None:
            raise UnsupportedBridgeExpression(f"only non-negative integer powers are supported: {e}")
        base_h = cnrs_h_from_symbolic(e.left, vname, order=order, env=env, L=L)
        out = CnrsH.one().pad(order)
        for _ in range(n):
            out = _trim_to_order(out * base_h, order)
        return out

    if isinstance(e, sy.Exp):
        a, b = _linear_coeffs(e.arg, vname, env, L=L)
        eb = cmath.exp(b)
        coeffs = [eb * (a ** n) for n in range(order)]
        return CnrsH.from_list(coeffs)

    if isinstance(e, sy.Sin):
        a, b = _linear_coeffs(e.arg, vname, env, L=L)
        coeffs = [
            (a ** n) * cmath.sin(b + n * math.pi / 2)
            for n in range(order)
        ]
        return CnrsH.from_list(coeffs)

    if isinstance(e, sy.Cos):
        a, b = _linear_coeffs(e.arg, vname, env, L=L)
        coeffs = [
            (a ** n) * cmath.cos(b + n * math.pi / 2)
            for n in range(order)
        ]
        return CnrsH.from_list(coeffs)

    raise UnsupportedBridgeExpression(f"unsupported expression for CNRS-H bridge: {e!r}")


def symbolic_derivative_to_cnrs_h(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    L: int = 18,
) -> CnrsH:
    """Convert the symbolic derivative of ``expr`` into CNRS-H form."""
    return cnrs_h_from_symbolic(sy.diff(expr, var), var, order=order, env=env, L=L)


def cnrs_h_derivative_of_symbolic(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    L: int = 18,
) -> CnrsH:
    """Convert ``expr`` to CNRS-H first, then apply CNRS-H differentiation."""
    # Use one extra term so the derivative has the requested number of terms.
    return cnrs_h_from_symbolic(expr, var, order=order + 1, env=env, L=L).differentiate().truncate(order).pad(order)


def symbolic_integral_to_cnrs_h(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    L: int = 18,
) -> CnrsH:
    """Convert the conservative symbolic integral of ``expr`` into CNRS-H form."""
    integral = sy.integrate(expr, var).simplify()
    if isinstance(integral, sy.Integral):
        raise UnsupportedBridgeExpression(f"symbolic integrator returned unevaluated integral: {integral}")
    return cnrs_h_from_symbolic(integral, var, order=order, env=env, L=L)


def cnrs_h_integral_of_symbolic(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    constant: complex = 0,
    L: int = 18,
) -> CnrsH:
    """Convert ``expr`` to CNRS-H first, then apply CNRS-H integration."""
    # The integral will be one term longer; truncate back to requested order.
    return cnrs_h_from_symbolic(expr, var, order=max(order - 1, 1), env=env, L=L).integrate(constant).truncate(order).pad(order)


def max_coeff_error(a: CnrsH, b: CnrsH) -> float:
    """Maximum absolute coefficient difference over the longer coefficient list."""
    n = max(a.length, b.length)
    return max(abs(complex(a.coeff(i)) - complex(b.coeff(i))) for i in range(n)) if n else 0.0


@dataclass(frozen=True)
class BridgeComparison:
    """Result of a symbolic-vs-CNRS-H bridge comparison."""

    symbolic_path: CnrsH
    cnrs_h_path: CnrsH
    max_error: float
    passed: bool


def compare_symbolic_and_cnrs_h_derivative(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    atol: float = 1e-10,
    L: int = 18,
) -> BridgeComparison:
    """Check whether symbolic differentiation commutes with CNRS-H conversion."""
    left = symbolic_derivative_to_cnrs_h(expr, var, order=order, env=env, L=L)
    right = cnrs_h_derivative_of_symbolic(expr, var, order=order, env=env, L=L)
    err = max_coeff_error(left, right)
    return BridgeComparison(left, right, err, err <= atol)


def compare_symbolic_and_cnrs_h_integral(
    expr: Any,
    var: str | sy.Var = "s",
    *,
    order: int = 12,
    env: Mapping[str, Any] | None = None,
    atol: float = 1e-10,
    L: int = 18,
) -> BridgeComparison:
    """Check whether conservative symbolic integration matches CNRS-H integration."""
    left = symbolic_integral_to_cnrs_h(expr, var, order=order, env=env, L=L)
    # Constants of integration are arbitrary.  Align the CNRS-H integration
    # constant with the symbolic antiderivative's constant term before
    # comparing coefficients.
    right = cnrs_h_integral_of_symbolic(expr, var, order=order, env=env, constant=left.coeff(0), L=L)
    err = max_coeff_error(left, right)
    return BridgeComparison(left, right, err, err <= atol)


def evaluate_cnrsh_series(h: CnrsH, x: complex) -> complex:
    """Small readability wrapper around ``CnrsH.evaluate``."""
    return h.evaluate(x)


__all__ = [
    "UnsupportedBridgeExpression",
    "BridgeComparison",
    "cnrs_h_from_symbolic",
    "symbolic_derivative_to_cnrs_h",
    "cnrs_h_derivative_of_symbolic",
    "symbolic_integral_to_cnrs_h",
    "cnrs_h_integral_of_symbolic",
    "compare_symbolic_and_cnrs_h_derivative",
    "compare_symbolic_and_cnrs_h_integral",
    "max_coeff_error",
    "evaluate_cnrsh_series",
]
