"""
cnrs.autodiff
=============

First-order automatic differentiation for the CNRS toolkit.

This module adds chain-rule capability by using a dual-number style wrapper:

    x -> (value, derivative)

where both ``value`` and ``derivative`` are stored as ``CnrsComplex`` values.
The layer is intentionally pragmatic: it gives scientific workflows a
chain-rule interface now, while leaving exact CNRS-H/function-coefficient
chain rules for later formal development.

Scope
-----
- First-order derivatives of scalar complex-valued functions of one scalar
  real/complex variable.
- Arithmetic operators: +, -, *, /, powers.
- Elementary functions: exp, log, sin, cos, tan, sqrt.
- Optional integer branch index for log/sqrt/power experiments.

This is not a full symbolic algebra system. It is automatic differentiation
through composed numerical calculations.

Example
-------
>>> from cnrs.autodiff import CnrsDual, exp
>>> x = CnrsDual.variable(2.0)
>>> y = exp(x * x)
>>> complex(y.deriv)
(218.39260013257694+0j)   # approximately 4*exp(4)

Author: Donald G. Palmer / AI collaboration
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
from typing import Any, Union

from .cnrs_complex import CnrsComplex, DEFAULT_L

Scalar = Union[int, float, complex, CnrsComplex]


def _as_complex(x: Scalar) -> complex:
    """Return a Python complex value for a scalar CNRS-compatible object."""
    if isinstance(x, CnrsComplex):
        return complex(x)
    return complex(x)


def _choose_L(*values: Any, default: int = DEFAULT_L) -> int:
    """Choose the maximum mantissa length visible among inputs."""
    L = default
    for v in values:
        if isinstance(v, CnrsDual):
            L = max(L, v.L)
        elif isinstance(v, CnrsComplex):
            L = max(L, v.L)
    return L


def _cz(value: Scalar, L: int) -> CnrsComplex:
    """Encode value as CnrsComplex at mantissa length L."""
    if isinstance(value, CnrsComplex) and value.L == L:
        return value
    return CnrsComplex(_as_complex(value), L=L)


@dataclass(frozen=True)
class CnrsDual:
    """
    First-order CNRS automatic-differentiation value.

    Parameters
    ----------
    value:
        CNRS complex value f(x).
    deriv:
        CNRS complex derivative df/dx.
    branch:
        Integer branch tag used by branch-sensitive functions.  The current
        implementation applies it to log as ``log(z) + 2*pi*i*branch``.
        More detailed CNRS branch-state tracking can be layered here later.
    L:
        Optional mantissa length.  If omitted, the maximum L from ``value`` and
        ``deriv`` is used, falling back to cnrs_complex.DEFAULT_L.

    Notes
    -----
    This class implements chain-rule arithmetic over ``CnrsComplex``.  It is
    deliberately a numerical autodiff layer, not a symbolic simplifier.
    """

    value: CnrsComplex
    deriv: CnrsComplex
    branch: int = 0

    def __init__(
        self,
        value: Scalar,
        deriv: Scalar = 0,
        branch: int = 0,
        L: int | None = None,
    ):
        chosen_L = _choose_L(value, deriv) if L is None else L
        object.__setattr__(self, "value", _cz(value, chosen_L))
        object.__setattr__(self, "deriv", _cz(deriv, chosen_L))
        object.__setattr__(self, "branch", int(branch))

    @classmethod
    def variable(cls, value: Scalar, L: int = DEFAULT_L, branch: int = 0) -> "CnrsDual":
        """Create an independent variable with derivative 1."""
        return cls(value, 1, branch=branch, L=L)

    @classmethod
    def constant(cls, value: Scalar, L: int = DEFAULT_L, branch: int = 0) -> "CnrsDual":
        """Create a constant with derivative 0."""
        return cls(value, 0, branch=branch, L=L)

    @property
    def L(self) -> int:
        """Mantissa length shared by value and derivative."""
        return max(self.value.L, self.deriv.L)

    def as_tuple(self) -> tuple[complex, complex]:
        """Return decoded ``(value, derivative)`` as Python complex values."""
        return complex(self.value), complex(self.deriv)

    def with_branch(self, branch: int) -> "CnrsDual":
        """Return the same dual value with a different branch tag."""
        return CnrsDual(self.value, self.deriv, branch=branch, L=self.L)

    def _coerce_dual(self, other: Any) -> "CnrsDual":
        if isinstance(other, CnrsDual):
            return other
        return CnrsDual.constant(other, L=self.L)

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def __add__(self, other: Any) -> "CnrsDual":
        other = self._coerce_dual(other)
        L = _choose_L(self, other)
        return CnrsDual(
            _as_complex(self.value) + _as_complex(other.value),
            _as_complex(self.deriv) + _as_complex(other.deriv),
            branch=self.branch,
            L=L,
        )

    def __radd__(self, other: Any) -> "CnrsDual":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "CnrsDual":
        other = self._coerce_dual(other)
        L = _choose_L(self, other)
        return CnrsDual(
            _as_complex(self.value) - _as_complex(other.value),
            _as_complex(self.deriv) - _as_complex(other.deriv),
            branch=self.branch,
            L=L,
        )

    def __rsub__(self, other: Any) -> "CnrsDual":
        other = self._coerce_dual(other)
        return other.__sub__(self)

    def __neg__(self) -> "CnrsDual":
        return CnrsDual(-_as_complex(self.value), -_as_complex(self.deriv), branch=self.branch, L=self.L)

    def __pos__(self) -> "CnrsDual":
        return self

    def __mul__(self, other: Any) -> "CnrsDual":
        other = self._coerce_dual(other)
        L = _choose_L(self, other)
        u, du = self.as_tuple()
        v, dv = other.as_tuple()
        return CnrsDual(u * v, du * v + u * dv, branch=self.branch, L=L)

    def __rmul__(self, other: Any) -> "CnrsDual":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "CnrsDual":
        other = self._coerce_dual(other)
        L = _choose_L(self, other)
        u, du = self.as_tuple()
        v, dv = other.as_tuple()
        if abs(v) == 0:
            raise ZeroDivisionError("CnrsDual division by zero")
        return CnrsDual(u / v, (du * v - u * dv) / (v * v), branch=self.branch, L=L)

    def __rtruediv__(self, other: Any) -> "CnrsDual":
        other = self._coerce_dual(other)
        return other.__truediv__(self)

    def __pow__(self, exponent: Any) -> "CnrsDual":
        """
        Power rule.

        If exponent is a scalar a:
            d(u^a) = a*u^(a-1)*u'

        If exponent is another CnrsDual v:
            d(u^v) = u^v * (v' * Log(u) + v * u'/u)

        The dual-exponent case uses this module's branch-aware log.
        """
        if isinstance(exponent, CnrsDual):
            u, du = self.as_tuple()
            v, dv = exponent.as_tuple()
            if abs(u) == 0:
                raise ZeroDivisionError("dual power with variable exponent at base zero")
            L = _choose_L(self, exponent)
            val = u ** v
            # Use branch-aware logarithm for derivative.
            log_u = branch_log(u, self.branch)
            deriv = val * (dv * log_u + v * du / u)
            return CnrsDual(val, deriv, branch=self.branch, L=L)

        a = _as_complex(exponent)
        u, du = self.as_tuple()
        L = _choose_L(self, exponent)
        if abs(u) == 0 and a != 0:
            # derivative may be singular for many a. Let Python raise when applicable.
            val = u ** a
            deriv = a * (u ** (a - 1)) * du
        else:
            val = u ** a
            deriv = a * (u ** (a - 1)) * du if a != 0 else 0
        return CnrsDual(val, deriv, branch=self.branch, L=L)

    def __rpow__(self, base: Any) -> "CnrsDual":
        base_dual = self._coerce_dual(base)
        return base_dual.__pow__(self)

    def __complex__(self) -> complex:
        """Decode the value component as Python complex."""
        return complex(self.value)

    def __repr__(self) -> str:
        v, d = self.as_tuple()
        return f"CnrsDual(value={v!r}, deriv={d!r}, branch={self.branch}, L={self.L})"

    def __str__(self) -> str:
        v, d = self.as_tuple()
        return f"CnrsDual(value={v.real:+.6g}{v.imag:+.6g}j, deriv={d.real:+.6g}{d.imag:+.6g}j, branch={self.branch})"


def as_dual(x: Any, *, variable: bool = False, L: int = DEFAULT_L) -> CnrsDual:
    """
    Convert a scalar or CnrsDual into a CnrsDual.

    Parameters
    ----------
    x:
        Scalar or CnrsDual.
    variable:
        If True, scalar inputs are treated as independent variables.
        If False, scalar inputs are constants.
    L:
        Mantissa length for scalar inputs.
    """
    if isinstance(x, CnrsDual):
        return x
    return CnrsDual.variable(x, L=L) if variable else CnrsDual.constant(x, L=L)


def branch_log(z: complex, branch: int = 0) -> complex:
    """Complex logarithm with explicit integer branch."""
    return cmath.log(z) + (2j * cmath.pi * int(branch))


# ---------------------------------------------------------------------------
# Elementary functions
# ---------------------------------------------------------------------------

def exp(u: Any) -> CnrsDual:
    """Chain-rule exponential: d exp(u) = exp(u) * u'."""
    u = as_dual(u)
    val = cmath.exp(complex(u.value))
    return CnrsDual(val, val * complex(u.deriv), branch=u.branch, L=u.L)


def log(u: Any, branch: int | None = None) -> CnrsDual:
    """
    Branch-aware logarithm.

    d log(u) = u'/u.  The derivative is branch-independent away from branch
    cuts, while the value includes ``2*pi*i*branch``.
    """
    u = as_dual(u)
    b = u.branch if branch is None else int(branch)
    z = complex(u.value)
    if abs(z) == 0:
        raise ZeroDivisionError("log derivative is singular at zero")
    return CnrsDual(branch_log(z, b), complex(u.deriv) / z, branch=b, L=u.L)


def sin(u: Any) -> CnrsDual:
    """Chain-rule sine: d sin(u) = cos(u) * u'."""
    u = as_dual(u)
    z = complex(u.value)
    return CnrsDual(cmath.sin(z), cmath.cos(z) * complex(u.deriv), branch=u.branch, L=u.L)


def cos(u: Any) -> CnrsDual:
    """Chain-rule cosine: d cos(u) = -sin(u) * u'."""
    u = as_dual(u)
    z = complex(u.value)
    return CnrsDual(cmath.cos(z), -cmath.sin(z) * complex(u.deriv), branch=u.branch, L=u.L)


def tan(u: Any) -> CnrsDual:
    """Chain-rule tangent: d tan(u) = u'/cos(u)^2."""
    u = as_dual(u)
    z = complex(u.value)
    c = cmath.cos(z)
    if abs(c) == 0:
        raise ZeroDivisionError("tan derivative singular where cos(u)=0")
    return CnrsDual(cmath.tan(z), complex(u.deriv) / (c * c), branch=u.branch, L=u.L)


def sqrt(u: Any, branch: int | None = None) -> CnrsDual:
    """
    Branch-aware square root.

    The value is computed as ``exp(0.5 * log(u, branch))`` to keep branch
    handling consistent with the logarithm. The derivative is computed
    directly as ``0.5 * u' / sqrt(u)`` rather than propagated through a
    second exp/log round-trip -- algebraically identical, since
    d/dx exp(0.5*log(u)) = exp(0.5*log(u)) * 0.5*u'/u = sqrt(u) * 0.5*u'/u
    = 0.5*u'/sqrt(u), but this avoids an extra complex exp() and log() call
    and the (tiny but nonzero) extra floating-point error each introduces.
    """
    u = as_dual(u)
    b = u.branch if branch is None else int(branch)
    z = complex(u.value)
    if abs(z) == 0:
        raise ZeroDivisionError("sqrt derivative is singular at zero")
    root = cmath.exp(0.5 * branch_log(z, b))
    deriv = 0.5 * complex(u.deriv) / root
    return CnrsDual(root, deriv, branch=b, L=u.L)


def pow_const(u: Any, exponent: Scalar) -> CnrsDual:
    """Convenience wrapper for scalar-exponent powers."""
    return as_dual(u).__pow__(exponent)


def compose(outer, inner):
    """
    Compose unary autodiff-aware functions.

    ``compose(f, g)(x)`` returns ``f(g(x))``.  This is a convenience helper
    for examples and tests; the chain rule is handled by CnrsDual itself.
    """
    def _composed(x):
        return outer(inner(x))
    return _composed


def derivative(func, x: Scalar, *, L: int = DEFAULT_L, branch: int = 0) -> CnrsComplex:
    """
    Evaluate the first derivative of a unary function at x.

    The function must accept and return a CnrsDual, or accept a CnrsDual and
    use this module's elementary functions.

    Returns
    -------
    CnrsComplex
        The derivative component f'(x).
    """
    y = func(CnrsDual.variable(x, L=L, branch=branch))
    if not isinstance(y, CnrsDual):
        raise TypeError("derivative() expected func(CnrsDual) to return CnrsDual")
    return y.deriv


def value_and_derivative(func, x: Scalar, *, L: int = DEFAULT_L, branch: int = 0) -> tuple[CnrsComplex, CnrsComplex]:
    """
    Evaluate both value and first derivative of a unary function at x.

    Returns ``(f(x), f'(x))`` as ``CnrsComplex`` objects.
    """
    y = func(CnrsDual.variable(x, L=L, branch=branch))
    if not isinstance(y, CnrsDual):
        raise TypeError("value_and_derivative() expected func(CnrsDual) to return CnrsDual")
    return y.value, y.deriv
