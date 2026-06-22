"""
cnrs.symbolic
=============

Minimal symbolic differentiation and conservative symbolic integration for the CNRS toolkit.

This module adds an expression-tree layer above the v0.4.0 first-order
``CnrsDual`` automatic-differentiation layer.  The goal is not to replicate a
full computer-algebra system, but to provide a small, inspectable symbolic
calculus that is useful for CNRS and Scale Space workflows:

- symbolic expression trees for +, -, *, /, powers, exp, log, sin, cos, tan,
  and sqrt;
- symbolic differentiation with the chain rule;
- conservative rule-based symbolic integration with unevaluated Integral fallback;
- conservative simplification rules;
- numeric evaluation through ordinary Python/CNRS values;
- dual-number evaluation, so symbolic derivatives can be cross-checked against
  the existing autodiff layer;
- explicit branch-state scaffolding for log/sqrt/power expressions.

Branch note
-----------
The derivative of ``Log_k(u)`` is locally ``u'/u`` away from singularities and
branch cuts; the branch tag affects the value, not that local derivative.  The
symbolic object keeps the branch tag so future CNRS branch-state machinery can
build on it.  v0.4.5 makes this branch state explicit and testable, but it does
not yet implement global path-dependent analytic continuation or full Riemann
surface tracking.

Author: Donald G. Palmer / AI collaboration
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
from typing import Any, Mapping, Union

from .cnrs_complex import CnrsComplex, DEFAULT_L
from . import autodiff as ad

NumberLike = Union[int, float, complex, CnrsComplex]
Env = Mapping[str, Any]


@dataclass(frozen=True)
class BranchState:
    """Explicit branch-state scaffold for symbolic complex functions.

    The current symbolic layer uses simple integer branch labels for local
    choices of logarithm, square root, and power evaluation.  ``winding`` is
    reserved for future path-dependent analytic-continuation work.  This class
    is intentionally small: it records branch choices and makes them visible in
    expression objects without claiming full Riemann-surface tracking.
    """

    log_branch: int = 0
    sqrt_branch: int = 0
    pow_branch: int = 0
    winding: int = 0

    def for_log(self, branch: int | None = None) -> "BranchState":
        b = self.log_branch if branch is None else int(branch)
        return BranchState(b, self.sqrt_branch, self.pow_branch, self.winding)

    def for_sqrt(self, branch: int | None = None) -> "BranchState":
        b = self.sqrt_branch if branch is None else int(branch)
        return BranchState(self.log_branch, b, self.pow_branch, self.winding)

    def for_pow(self, branch: int | None = None) -> "BranchState":
        b = self.pow_branch if branch is None else int(branch)
        return BranchState(self.log_branch, self.sqrt_branch, b, self.winding)

    def __str__(self) -> str:
        return (
            f"BranchState(log={self.log_branch}, sqrt={self.sqrt_branch}, "
            f"pow={self.pow_branch}, winding={self.winding})"
        )


DEFAULT_BRANCH_STATE = BranchState()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_complex_value(x: Any) -> complex:
    if isinstance(x, CnrsComplex):
        return complex(x)
    return complex(x)


def _format_number(z: Any) -> str:
    """Compact display for scalar constants."""
    c = _as_complex_value(z)
    if abs(c.imag) < 1e-15:
        r = c.real
        if abs(r - round(r)) < 1e-15:
            return str(int(round(r)))
        return f"{r:g}"
    if abs(c.real) < 1e-15:
        im = c.imag
        if abs(im - 1) < 1e-15:
            return "i"
        if abs(im + 1) < 1e-15:
            return "-i"
        return f"{im:g}i"
    sign = "+" if c.imag >= 0 else "-"
    return f"{c.real:g}{sign}{abs(c.imag):g}i"


def _is_const(expr: Any, value: complex | None = None) -> bool:
    if not isinstance(expr, Const):
        return False
    if value is None:
        return True
    return abs(_as_complex_value(expr.value) - value) < 1e-15


def _zero() -> "Const":
    return Const(0)


def _one() -> "Const":
    return Const(1)


def sympify(x: Any) -> "Expr":
    """Convert a scalar or Expr into an Expr."""
    if isinstance(x, Expr):
        return x
    if isinstance(x, (int, float, complex, CnrsComplex)):
        return Const(x)
    raise TypeError(f"cannot convert {type(x).__name__} to symbolic expression")




def _var_name(var: str | "Var") -> str:
    return var.name if isinstance(var, Var) else str(var)


def _contains_var(expr: Any, var: str | "Var") -> bool:
    """True if expr syntactically contains variable var."""
    expr = sympify(expr)
    target = _var_name(var)
    if isinstance(expr, Var):
        return expr.name == target
    if isinstance(expr, Const):
        return False
    if isinstance(expr, Neg):
        return _contains_var(expr.arg, target)
    if isinstance(expr, Binary):
        return _contains_var(expr.left, target) or _contains_var(expr.right, target)
    if isinstance(expr, Unary):
        return _contains_var(expr.arg, target)
    if isinstance(expr, Integral):
        # Treat bound variable conservatively: Integral(f dx) contains x as a
        # formal object, but for dependency tests used by integrate() we only
        # need the integrand dependency.
        return _contains_var(expr.integrand, target) or expr.var.name == target
    return False


def _independent_of(expr: Any, var: str | "Var") -> bool:
    return not _contains_var(expr, var)


def _constant_nonzero(expr: Expr) -> complex | None:
    """Return the scalar value of a nonzero Const, else None."""
    if _is_const(expr):
        z = _as_complex_value(expr.value)
        if abs(z) > 1e-15:
            return z
    return None

def _combine_L(*values: Any, default: int = DEFAULT_L) -> int:
    L = default
    for v in values:
        if isinstance(v, CnrsComplex):
            L = max(L, v.L)
        elif isinstance(v, ad.CnrsDual):
            L = max(L, v.L)
    return L


def _branch_state_for(kind: str, branch: int, branch_state: BranchState | None = None) -> BranchState:
    state = DEFAULT_BRANCH_STATE if branch_state is None else branch_state
    if kind == "log":
        return state.for_log(branch)
    if kind == "sqrt":
        return state.for_sqrt(branch)
    if kind == "pow":
        return state.for_pow(branch)
    raise ValueError(f"unknown branch-state kind: {kind}")


def _numeric_binary(op: str, a: Any, b: Any) -> Any:
    """Evaluate a binary op while preserving dual inputs when present."""
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b
    if op == "**":
        if isinstance(a, ad.CnrsDual) or isinstance(b, ad.CnrsDual):
            return a ** b
        return CnrsComplex(_as_complex_value(a) ** _as_complex_value(b), L=_combine_L(a, b))
    raise ValueError(op)


# ---------------------------------------------------------------------------
# Base expression class
# ---------------------------------------------------------------------------

class Expr:
    """Base class for symbolic expressions."""

    __array_priority__ = 1000

    def diff(self, var: str | "Var") -> "Expr":
        raise NotImplementedError

    def simplify(self) -> "Expr":
        return self

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        """
        Evaluate expression using values from env.

        If any variable value is a ``CnrsDual``, evaluation automatically uses
        the autodiff backend and returns a ``CnrsDual``.  Otherwise elementary
        operations return ``CnrsComplex`` values at mantissa length L.
        """
        raise NotImplementedError

    def eval_dual(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        """Alias for eval; pass CnrsDual variables in env to get dual output."""
        return self.eval(env or {}, L=L)

    def substitute(self, mapping: Mapping[str, Any]) -> "Expr":
        """Replace variables by expressions or constants."""
        return self

    # Operators ----------------------------------------------------------
    def __add__(self, other: Any) -> "Expr":
        return Add(self, sympify(other))

    def __radd__(self, other: Any) -> "Expr":
        return Add(sympify(other), self)

    def __sub__(self, other: Any) -> "Expr":
        return Sub(self, sympify(other))

    def __rsub__(self, other: Any) -> "Expr":
        return Sub(sympify(other), self)

    def __mul__(self, other: Any) -> "Expr":
        return Mul(self, sympify(other))

    def __rmul__(self, other: Any) -> "Expr":
        return Mul(sympify(other), self)

    def __truediv__(self, other: Any) -> "Expr":
        return Div(self, sympify(other))

    def __rtruediv__(self, other: Any) -> "Expr":
        return Div(sympify(other), self)

    def __pow__(self, other: Any) -> "Expr":
        return Pow(self, sympify(other))

    def __rpow__(self, other: Any) -> "Expr":
        return Pow(sympify(other), self)

    def __neg__(self) -> "Expr":
        return Neg(self)

    def __pos__(self) -> "Expr":
        return self


@dataclass(frozen=True)
class Const(Expr):
    """Scalar constant."""

    value: Any

    def diff(self, var: str | "Var") -> Expr:
        return _zero()

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        if isinstance(self.value, CnrsComplex):
            return self.value
        return CnrsComplex(self.value, L=L)

    def simplify(self) -> Expr:
        return self

    def __str__(self) -> str:
        return _format_number(self.value)

    def __repr__(self) -> str:
        return f"Const({self.value!r})"


@dataclass(frozen=True)
class Var(Expr):
    """Symbolic variable."""

    name: str

    def diff(self, var: str | "Var") -> Expr:
        target = var.name if isinstance(var, Var) else str(var)
        return _one() if self.name == target else _zero()

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        env = env or {}
        if self.name not in env:
            raise KeyError(f"no value supplied for variable {self.name!r}")
        value = env[self.name]
        if isinstance(value, (CnrsComplex, ad.CnrsDual)):
            return value
        return CnrsComplex(value, L=L)

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        if self.name in mapping:
            return sympify(mapping[self.name])
        return self

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Var({self.name!r})"


@dataclass(frozen=True)
class Neg(Expr):
    arg: Expr

    def __init__(self, arg: Any):
        object.__setattr__(self, "arg", sympify(arg))

    def diff(self, var: str | Var) -> Expr:
        return -self.arg.diff(var)

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            return Const(-_as_complex_value(a.value))
        if isinstance(a, Neg):
            return a.arg.simplify()
        return Neg(a)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        return -self.arg.eval(env, L=L)

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        return Neg(self.arg.substitute(mapping))

    def __str__(self) -> str:
        return f"(-{self.arg})"


# ---------------------------------------------------------------------------
# Binary expressions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    right: Expr
    symbol: str = "?"

    def __init__(self, left: Any, right: Any):
        object.__setattr__(self, "left", sympify(left))
        object.__setattr__(self, "right", sympify(right))

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        return type(self)(self.left.substitute(mapping), self.right.substitute(mapping))

    def __str__(self) -> str:
        return f"({self.left} {self.symbol} {self.right})"


class Add(Binary):
    symbol = "+"

    def diff(self, var: str | Var) -> Expr:
        return self.left.diff(var) + self.right.diff(var)

    def simplify(self) -> Expr:
        a, b = self.left.simplify(), self.right.simplify()
        if _is_const(a, 0):
            return b
        if _is_const(b, 0):
            return a
        if _is_const(a) and _is_const(b):
            return Const(_as_complex_value(a.value) + _as_complex_value(b.value))
        return Add(a, b)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        return _numeric_binary("+", self.left.eval(env, L=L), self.right.eval(env, L=L))


class Sub(Binary):
    symbol = "-"

    def diff(self, var: str | Var) -> Expr:
        return self.left.diff(var) - self.right.diff(var)

    def simplify(self) -> Expr:
        a, b = self.left.simplify(), self.right.simplify()
        if _is_const(b, 0):
            return a
        if _is_const(a, 0):
            return (-b).simplify()
        if _is_const(a) and _is_const(b):
            return Const(_as_complex_value(a.value) - _as_complex_value(b.value))
        return Sub(a, b)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        return _numeric_binary("-", self.left.eval(env, L=L), self.right.eval(env, L=L))


class Mul(Binary):
    symbol = "*"

    def diff(self, var: str | Var) -> Expr:
        return self.left.diff(var) * self.right + self.left * self.right.diff(var)

    def simplify(self) -> Expr:
        a, b = self.left.simplify(), self.right.simplify()
        if _is_const(a, 0) or _is_const(b, 0):
            return _zero()
        if _is_const(a, 1):
            return b
        if _is_const(b, 1):
            return a
        if _is_const(a) and _is_const(b):
            return Const(_as_complex_value(a.value) * _as_complex_value(b.value))
        return Mul(a, b)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        return _numeric_binary("*", self.left.eval(env, L=L), self.right.eval(env, L=L))


class Div(Binary):
    symbol = "/"

    def diff(self, var: str | Var) -> Expr:
        return (self.left.diff(var) * self.right - self.left * self.right.diff(var)) / (self.right ** 2)

    def simplify(self) -> Expr:
        a, b = self.left.simplify(), self.right.simplify()
        if _is_const(a, 0):
            return _zero()
        if _is_const(b, 1):
            return a
        if _is_const(a) and _is_const(b):
            denom = _as_complex_value(b.value)
            if abs(denom) == 0:
                raise ZeroDivisionError("symbolic constant division by zero")
            return Const(_as_complex_value(a.value) / denom)
        return Div(a, b)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        return _numeric_binary("/", self.left.eval(env, L=L), self.right.eval(env, L=L))


@dataclass(frozen=True)
class Pow(Binary):
    """Power expression, with explicit branch state for complex logarithm semantics."""

    branch: int = 0
    branch_state: BranchState = DEFAULT_BRANCH_STATE
    symbol = "^"

    def __init__(self, left: Any, right: Any, branch: int = 0, branch_state: BranchState | None = None):
        object.__setattr__(self, "left", sympify(left))
        object.__setattr__(self, "right", sympify(right))
        b = int(branch)
        object.__setattr__(self, "branch", b)
        object.__setattr__(self, "branch_state", _branch_state_for("pow", b, branch_state))

    def diff(self, var: str | Var) -> Expr:
        u, v = self.left, self.right
        du, dv = u.diff(var), v.diff(var)
        if _is_const(v):
            exponent = _as_complex_value(v.value)
            return Const(exponent) * (u ** Const(exponent - 1)) * du
        return self * (dv * Log(u, branch=self.branch, branch_state=self.branch_state) + v * du / u)

    def simplify(self) -> Expr:
        a, b = self.left.simplify(), self.right.simplify()
        if _is_const(b, 0):
            return _one()
        if _is_const(b, 1):
            return a
        if _is_const(a, 0):
            return _zero()
        if _is_const(a, 1):
            return _one()
        if _is_const(a) and _is_const(b):
            base = _as_complex_value(a.value)
            exponent = _as_complex_value(b.value)
            if abs(base) == 0:
                return Const(base ** exponent)
            return Const(cmath.exp(exponent * ad.branch_log(base, self.branch)))
        return Pow(a, b, branch=self.branch, branch_state=self.branch_state)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        a = self.left.eval(env, L=L)
        b = self.right.eval(env, L=L)
        if isinstance(a, ad.CnrsDual):
            return a.with_branch(self.branch) ** b
        if isinstance(b, ad.CnrsDual):
            return a ** b.with_branch(self.branch)
        base = _as_complex_value(a)
        exponent = _as_complex_value(b)
        if abs(base) == 0:
            return CnrsComplex(base ** exponent, L=_combine_L(a, b, default=L))
        return CnrsComplex(cmath.exp(exponent * ad.branch_log(base, self.branch)), L=_combine_L(a, b, default=L))

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        return Pow(self.left.substitute(mapping), self.right.substitute(mapping), branch=self.branch, branch_state=self.branch_state)

    def __str__(self) -> str:
        suffix = f"; branch={self.branch}" if self.branch else ""
        return f"({self.left}^{self.right}{suffix})"

    def __repr__(self) -> str:
        return f"Pow({self.left!r}, {self.right!r}, branch={self.branch})"


# ---------------------------------------------------------------------------
# Unary functions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Unary(Expr):
    arg: Expr
    name: str = "fn"

    def __init__(self, arg: Any):
        object.__setattr__(self, "arg", sympify(arg))

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        return type(self)(self.arg.substitute(mapping))

    def __str__(self) -> str:
        return f"{self.name}({self.arg})"


class Exp(Unary):
    name = "exp"

    def diff(self, var: str | Var) -> Expr:
        return Exp(self.arg) * self.arg.diff(var)

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            return Const(cmath.exp(_as_complex_value(a.value)))
        return Exp(a)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        v = self.arg.eval(env, L=L)
        if isinstance(v, ad.CnrsDual):
            return ad.exp(v)
        return CnrsComplex(cmath.exp(_as_complex_value(v)), L=_combine_L(v, default=L))


@dataclass(frozen=True)
class Log(Unary):
    branch: int = 0
    branch_state: BranchState = DEFAULT_BRANCH_STATE
    name = "log"

    def __init__(self, arg: Any, branch: int = 0, branch_state: BranchState | None = None):
        object.__setattr__(self, "arg", sympify(arg))
        b = int(branch)
        object.__setattr__(self, "branch", b)
        object.__setattr__(self, "branch_state", _branch_state_for("log", b, branch_state))

    def diff(self, var: str | Var) -> Expr:
        return self.arg.diff(var) / self.arg

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            z = _as_complex_value(a.value)
            if abs(z) == 0:
                raise ZeroDivisionError("log singular at zero")
            return Const(ad.branch_log(z, self.branch))
        # Conservative: do not simplify log(exp(x)) globally over complex values.
        return Log(a, branch=self.branch, branch_state=self.branch_state)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        v = self.arg.eval(env, L=L)
        if isinstance(v, ad.CnrsDual):
            return ad.log(v, branch=self.branch)
        z = _as_complex_value(v)
        if abs(z) == 0:
            raise ZeroDivisionError("log singular at zero")
        return CnrsComplex(ad.branch_log(z, self.branch), L=_combine_L(v, default=L))

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        return Log(self.arg.substitute(mapping), branch=self.branch, branch_state=self.branch_state)

    def __str__(self) -> str:
        suffix = f"_{self.branch}" if self.branch else ""
        return f"log{suffix}({self.arg})"

    def __repr__(self) -> str:
        return f"Log({self.arg!r}, branch={self.branch})"


class Sin(Unary):
    name = "sin"

    def diff(self, var: str | Var) -> Expr:
        return Cos(self.arg) * self.arg.diff(var)

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            return Const(cmath.sin(_as_complex_value(a.value)))
        return Sin(a)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        v = self.arg.eval(env, L=L)
        if isinstance(v, ad.CnrsDual):
            return ad.sin(v)
        return CnrsComplex(cmath.sin(_as_complex_value(v)), L=_combine_L(v, default=L))


class Cos(Unary):
    name = "cos"

    def diff(self, var: str | Var) -> Expr:
        return -Sin(self.arg) * self.arg.diff(var)

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            return Const(cmath.cos(_as_complex_value(a.value)))
        return Cos(a)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        v = self.arg.eval(env, L=L)
        if isinstance(v, ad.CnrsDual):
            return ad.cos(v)
        return CnrsComplex(cmath.cos(_as_complex_value(v)), L=_combine_L(v, default=L))


class Tan(Unary):
    name = "tan"

    def diff(self, var: str | Var) -> Expr:
        return self.arg.diff(var) / (Cos(self.arg) ** 2)

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            return Const(cmath.tan(_as_complex_value(a.value)))
        return Tan(a)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        v = self.arg.eval(env, L=L)
        if isinstance(v, ad.CnrsDual):
            return ad.tan(v)
        return CnrsComplex(cmath.tan(_as_complex_value(v)), L=_combine_L(v, default=L))


@dataclass(frozen=True)
class Sqrt(Unary):
    branch: int = 0
    branch_state: BranchState = DEFAULT_BRANCH_STATE
    name = "sqrt"

    def __init__(self, arg: Any, branch: int = 0, branch_state: BranchState | None = None):
        object.__setattr__(self, "arg", sympify(arg))
        b = int(branch)
        object.__setattr__(self, "branch", b)
        object.__setattr__(self, "branch_state", _branch_state_for("sqrt", b, branch_state))

    def diff(self, var: str | Var) -> Expr:
        return self.arg.diff(var) / (Const(2) * Sqrt(self.arg, branch=self.branch, branch_state=self.branch_state))

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if _is_const(a):
            # Mirror autodiff convention: sqrt is exp(0.5 * log_branch(z)).
            z = _as_complex_value(a.value)
            return Const(cmath.exp(0.5 * ad.branch_log(z, self.branch)))
        return Sqrt(a, branch=self.branch, branch_state=self.branch_state)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        v = self.arg.eval(env, L=L)
        if isinstance(v, ad.CnrsDual):
            return ad.sqrt(v, branch=self.branch)
        z = _as_complex_value(v)
        return CnrsComplex(cmath.exp(0.5 * ad.branch_log(z, self.branch)), L=_combine_L(v, default=L))

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        return Sqrt(self.arg.substitute(mapping), branch=self.branch, branch_state=self.branch_state)

    def __str__(self) -> str:
        suffix = f"_{self.branch}" if self.branch else ""
        return f"sqrt{suffix}({self.arg})"

    def __repr__(self) -> str:
        return f"Sqrt({self.arg!r}, branch={self.branch})"



# ---------------------------------------------------------------------------
# Conservative symbolic integration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Integral(Expr):
    """
    Unevaluated symbolic integral.

    The rule-based ``integrate`` function returns an ``Integral`` object when no
    conservative elementary rule applies.  This avoids pretending to solve
    arbitrary symbolic integration problems.  Differentiating an unevaluated
    integral with respect to its own variable returns the integrand, providing a
    formal fundamental-theorem check for the supported expression layer.
    """

    integrand: Expr
    var: Var

    def __init__(self, integrand: Any, var: str | Var):
        object.__setattr__(self, "integrand", sympify(integrand))
        object.__setattr__(self, "var", var if isinstance(var, Var) else Var(str(var)))

    def diff(self, var: str | Var) -> Expr:
        target = _var_name(var)
        if self.var.name == target:
            return self.integrand
        return Integral(self.integrand.diff(var), self.var)

    def simplify(self) -> Expr:
        return Integral(self.integrand.simplify(), self.var)

    def eval(self, env: Env | None = None, *, L: int = DEFAULT_L) -> Any:
        raise NotImplementedError(
            "unevaluated Integral cannot be numerically evaluated; "
            "use integrate(...).simplify() and check whether a rule applied"
        )

    def substitute(self, mapping: Mapping[str, Any]) -> Expr:
        # Avoid substituting the integration variable itself; this is a simple
        # conservative binding rule, not a full alpha-conversion system.
        filtered = {k: v for k, v in mapping.items() if k != self.var.name}
        return Integral(self.integrand.substitute(filtered), self.var)

    def __str__(self) -> str:
        return f"Integral({self.integrand}, d{self.var})"


def _linear_antiderivative_for_unary(cls: type[Unary], arg: Expr, var: str | Var) -> Expr | None:
    """Integrate f(g(x)) when g'(x) is independent of x.

    This covers both numeric slopes, e.g. exp(2*x+1), and symbolic
    parameter slopes, e.g. exp(k*x), while avoiding cases such as
    exp(x*x).  A symbolic slope is treated under the usual nonzero-parameter
    assumption; if the slope is exactly zero, no rule is applied here.
    """
    du = arg.diff(var).simplify()
    if _is_const(du, 0):
        return None
    if not _independent_of(du, var):
        return None
    if cls is Exp:
        return (Exp(arg) / du).simplify()
    if cls is Sin:
        return ((-Cos(arg)) / du).simplify()
    if cls is Cos:
        return (Sin(arg) / du).simplify()
    return None


def integrate(expr: Any, var: str | Var) -> Expr:
    """
    Conservatively integrate an expression with respect to var.

    Supported elementary rules include constants, linearity, constant-factor
    extraction, powers of the integration variable, 1/x -> log(x), and
    exp/sin/cos of affine arguments whose derivative is a nonzero constant.
    When no rule applies, the result is an unevaluated ``Integral`` object.
    """
    e = sympify(expr).simplify()
    v = var if isinstance(var, Var) else Var(str(var))

    if _independent_of(e, v):
        return (e * v).simplify()

    if isinstance(e, Var) and e.name == v.name:
        return ((v ** Const(2)) / Const(2)).simplify()

    if isinstance(e, Add):
        return (integrate(e.left, v) + integrate(e.right, v)).simplify()

    if isinstance(e, Sub):
        return (integrate(e.left, v) - integrate(e.right, v)).simplify()

    if isinstance(e, Neg):
        return (-integrate(e.arg, v)).simplify()

    if isinstance(e, Mul):
        if _independent_of(e.left, v):
            return (e.left * integrate(e.right, v)).simplify()
        if _independent_of(e.right, v):
            return (e.right * integrate(e.left, v)).simplify()

    if isinstance(e, Div):
        # constant numerator / variable -> c log(variable)
        if _independent_of(e.left, v) and isinstance(e.right, Var) and e.right.name == v.name:
            return (e.left * Log(v)).simplify()
        # f(x) / constant -> integrate(f) / constant
        if _independent_of(e.right, v):
            return (integrate(e.left, v) / e.right).simplify()

    if isinstance(e, Pow):
        if isinstance(e.left, Var) and e.left.name == v.name and _is_const(e.right):
            n = _as_complex_value(e.right.value)
            if abs(n + 1) < 1e-15:
                return Log(v, branch=e.branch)
            return ((v ** Const(n + 1)) / Const(n + 1)).simplify()

    if isinstance(e, Exp):
        out = _linear_antiderivative_for_unary(Exp, e.arg, v)
        if out is not None:
            return out

    if isinstance(e, Sin):
        out = _linear_antiderivative_for_unary(Sin, e.arg, v)
        if out is not None:
            return out

    if isinstance(e, Cos):
        out = _linear_antiderivative_for_unary(Cos, e.arg, v)
        if out is not None:
            return out

    return Integral(e, v)

# ---------------------------------------------------------------------------
# Public constructors/functions
# ---------------------------------------------------------------------------

def exp(x: Any) -> Expr:
    return Exp(x)


def log(x: Any, branch: int = 0, branch_state: BranchState | None = None) -> Expr:
    return Log(x, branch=branch, branch_state=branch_state)


def sin(x: Any) -> Expr:
    return Sin(x)


def cos(x: Any) -> Expr:
    return Cos(x)


def tan(x: Any) -> Expr:
    return Tan(x)


def sqrt(x: Any, branch: int = 0, branch_state: BranchState | None = None) -> Expr:
    return Sqrt(x, branch=branch, branch_state=branch_state)


def pow_branch(base: Any, exponent: Any, branch: int = 0, branch_state: BranchState | None = None) -> Expr:
    return Pow(base, exponent, branch=branch, branch_state=branch_state)


def diff(expr: Any, var: str | Var) -> Expr:
    """Symbolically differentiate expr with respect to var and simplify once."""
    return sympify(expr).diff(var).simplify()


__all__ = [
    "BranchState", "DEFAULT_BRANCH_STATE",
    "Expr", "Const", "Var", "Add", "Sub", "Mul", "Div", "Pow", "Neg",
    "Exp", "Log", "Sin", "Cos", "Tan", "Sqrt", "Integral", "sympify",
    "exp", "log", "sin", "cos", "tan", "sqrt", "pow_branch", "diff", "integrate",
]
