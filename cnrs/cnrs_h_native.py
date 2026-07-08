"""
cnrs_h_native.py
================
CnrsHNative: CNRS-H calculus with CNRS-A native coefficient arithmetic.

Unlike ``CnrsH``, which stores EGF coefficients as plain Python
``int``/``float``/``complex``, ``CnrsHNative`` stores each coefficient as a
``CVal`` — a CNRS-A digit string in base z0 = -2 + i.  All coefficient
arithmetic is routed through the native CNRS-A layers:

  - addition        uses bounded-input CNRS-A addition (``add_cnrs``)
  - negation        multiplies by the CNRS-A representation of -1 (``mul_cnrs``)
  - subtraction     a + (-b): native negation followed by CNRS-A addition
  - multiplication  convolution followed by general CNRS-A normalisation (``mul_cnrs``)

The structural CNRS-H operations remain unchanged:

  - differentiation = drop d_0              (exact, O(n))
  - integration     = prepend constant C    (exact, O(1))
  - evaluation at a point s                 uses Python complex arithmetic

Scope: Gaussian-integer coefficients only.  Coefficients that are not
Gaussian integers (e.g. complex eigenvalues) cannot be stored in a ``CVal``
exactly and will raise ``NonGaussianCoefficientError``.

Interoperability:
  - ``CnrsHNative.from_cnrs_h(h)``  converts a ``CnrsH`` (Gaussian-int coeffs)
  - ``to_cnrs_h()``                  converts back for use in existing code
  - ``verify_leibniz(f, g, order)``  checks D(f*g) = Df*g + f*Dg natively

The Leibniz rule and EGF convolution identities are verified entirely in
CNRS-A coefficient space, with no Python arithmetic on the coefficients
themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, factorial
from typing import Sequence, Union

from .cnrs_value import CVal
from .cnrs_h import CnrsH


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class NonGaussianCoefficientError(ValueError):
    """Raised when a coefficient is not a Gaussian integer."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ZERO_CVAL = CVal.from_gaussian(0 + 0j)
_ONE_CVAL  = CVal.from_gaussian(1 + 0j)


def _to_cval(c: Union[int, float, complex, CVal]) -> CVal:
    """Convert a value to CVal, requiring it be a Gaussian integer."""
    if isinstance(c, CVal):
        return c
    z = complex(c)
    if abs(z.real - round(z.real)) > 1e-9 or abs(z.imag - round(z.imag)) > 1e-9:
        raise NonGaussianCoefficientError(
            f"Coefficient {c!r} is not a Gaussian integer and cannot be "
            f"stored in CnrsHNative. Use CnrsH for float/complex coefficients."
        )
    return CVal.from_gaussian(complex(round(z.real), round(z.imag)))


def _cval_neg(v: CVal) -> CVal:
    """Negate a CVal via CVal.__neg__ (mul_cnrs with -1 = '144')."""
    return -v


def _cval_sub(a: CVal, b: CVal) -> CVal:
    """Subtract two CVals via CVal.__sub__ (a + (-b), fully native)."""
    return a - b


# ---------------------------------------------------------------------------
# CnrsHNative
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CnrsHNative:
    """
    CNRS-H function object with CNRS-A native coefficient arithmetic.

    Stores EGF coefficients [d0, d1, ..., dN] as ``CVal`` objects.
    The represented function is:

        f(s) = sum_{n=0}^{N} d_n * s^n / n!

    Differentiation and integration are exact structural operations.
    Coefficient addition and multiplication are routed through the
    CNRS-A addition and general multiplication/normalisation layers.
    """
    coeffs: tuple  # tuple of CVal

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @staticmethod
    def from_gaussian_list(ds: Sequence[Union[int, float, complex]]) -> "CnrsHNative":
        """Build from a list of Gaussian integers (ints or Gaussian-int complex)."""
        return CnrsHNative(tuple(_to_cval(d) for d in ds))

    @staticmethod
    def zero(length: int = 1) -> "CnrsHNative":
        """Zero function with ``length`` coefficients."""
        return CnrsHNative(tuple(_ZERO_CVAL for _ in range(length)))

    @staticmethod
    def one() -> "CnrsHNative":
        """Constant function f(s) = 1."""
        return CnrsHNative((_ONE_CVAL,))

    @staticmethod
    def identity() -> "CnrsHNative":
        """Identity function f(s) = s.  Coefficients: [0, 1]."""
        return CnrsHNative((_ZERO_CVAL, _ONE_CVAL))

    @staticmethod
    def constant(value: Union[int, complex, CVal], length: int = 1) -> "CnrsHNative":
        """Constant function f(s) = value."""
        v = _to_cval(value) if not isinstance(value, CVal) else value
        return CnrsHNative((v,) + tuple(_ZERO_CVAL for _ in range(length - 1)))

    @staticmethod
    def eigen_exponential(alpha: Union[int, complex, CVal] = 1, terms: int = 10) -> "CnrsHNative":
        """Truncated native EGF for ``exp(alpha * s)``.

        Coefficients are ``alpha**n`` and must remain Gaussian integers so
        they can be represented exactly as :class:`CVal` objects.
        """
        if terms < 1:
            raise ValueError("terms must be at least 1")
        a = alpha.to_gaussian() if isinstance(alpha, CVal) else complex(alpha)
        return CnrsHNative(tuple(_to_cval(a ** n) for n in range(terms)))

    @staticmethod
    def from_cnrs_h(h: CnrsH) -> "CnrsHNative":
        """Convert a ``CnrsH`` to ``CnrsHNative``.

        Requires all coefficients to be Gaussian integers.  Raises
        ``NonGaussianCoefficientError`` otherwise.
        """
        return CnrsHNative(tuple(_to_cval(c) for c in h.coeffs))

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def length(self) -> int:
        return len(self.coeffs)

    def coeff(self, n: int) -> CVal:
        """Return coefficient d_n, or the zero CVal if out of range."""
        return self.coeffs[n] if n < len(self.coeffs) else _ZERO_CVAL

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def to_cnrs_h(self) -> CnrsH:
        """Convert to ``CnrsH`` (Python-number coefficients) for interop."""
        return CnrsH(tuple(c.to_gaussian() for c in self.coeffs))

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, s: complex) -> complex:
        """Evaluate f(s) = sum d_n * s^n / n! using Python complex arithmetic.

        The coefficients are decoded from their CNRS-A representations.
        This is the one place where Python arithmetic is unavoidable:
        ``s`` is a real/complex point, not a CNRS-A value.
        """
        result = complex(0)
        s_power = complex(1)
        fact = 1
        for n, d in enumerate(self.coeffs):
            if n > 0:
                s_power *= s
                fact *= n
            result += d.to_gaussian() * s_power / fact
        return result

    def __call__(self, s: complex) -> complex:
        return self.evaluate(s)

    # ------------------------------------------------------------------
    # CNRS-H calculus — exact structural operations
    # ------------------------------------------------------------------

    def differentiate(self) -> "CnrsHNative":
        """Drop d_0 — exact CNRS-H differentiation.

        [d0, d1, ..., dN]  ->  [d1, d2, ..., dN]

        The dropped d_0 is the constant term, exactly as in ordinary
        calculus.  No arithmetic is performed on the coefficients.
        """
        if len(self.coeffs) <= 1:
            return CnrsHNative((_ZERO_CVAL,))
        return CnrsHNative(self.coeffs[1:])

    #: Alias matching CNRS programme notation.
    D = differentiate

    def integrate(self, constant: Union[int, complex, CVal] = 0) -> "CnrsHNative":
        """Prepend integration constant C — exact CNRS-H integration.

        [d0, d1, ..., dN]  ->  [C, d0, d1, ..., dN]

        No arithmetic is performed on the existing coefficients.
        """
        c = _to_cval(constant) if not isinstance(constant, CVal) else constant
        return CnrsHNative((c,) + self.coeffs)

    def nth_derivative(self, n: int) -> "CnrsHNative":
        """Drop first n coefficients — exact n-th derivative."""
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return self
        if n >= len(self.coeffs):
            return CnrsHNative((_ZERO_CVAL,))
        return CnrsHNative(self.coeffs[n:])

    # ------------------------------------------------------------------
    # CNRS-A native coefficient arithmetic
    # ------------------------------------------------------------------

    def __add__(self, other: "CnrsHNative") -> "CnrsHNative":
        """Pointwise coefficient addition via CNRS-A native addition."""
        n = max(len(self.coeffs), len(other.coeffs))
        result = tuple(self.coeff(i) + other.coeff(i) for i in range(n))
        return CnrsHNative(result)

    def __sub__(self, other: "CnrsHNative") -> "CnrsHNative":
        """Pointwise coefficient subtraction (via CNRS-A native arithmetic)."""
        n = max(len(self.coeffs), len(other.coeffs))
        result = tuple(_cval_sub(self.coeff(i), other.coeff(i)) for i in range(n))
        return CnrsHNative(result)

    def __neg__(self) -> "CnrsHNative":
        """Negate all coefficients (via CNRS-A native arithmetic)."""
        return CnrsHNative(tuple(_cval_neg(c) for c in self.coeffs))

    def __mul__(self, other: object) -> "CnrsHNative":
        """EGF binomial convolution — CNRS-A native for CnrsHNative operands.

        c_n = sum_{k=0}^{n} C(n,k) * a_k * b_{n-k}

        All multiplications and additions on coefficients are routed through
        ``CVal.__mul__`` (mul_cnrs) and ``CVal.__add__`` (add_cnrs) respectively.

        For scalar integers, the scalar is converted to a ``CVal`` first.
        """
        if isinstance(other, CnrsHNative):
            return self._egf_convolve_native(other)
        if isinstance(other, (int, complex)) or (
            isinstance(other, float) and other == round(other)
        ):
            scalar = _to_cval(other)
            return CnrsHNative(tuple(scalar * c for c in self.coeffs))
        return NotImplemented

    def __rmul__(self, other: object) -> "CnrsHNative":
        return self.__mul__(other)

    def _egf_convolve_native(self, other: "CnrsHNative") -> "CnrsHNative":
        """CNRS-A native EGF binomial convolution.

        Every multiply is ``CVal * CVal`` -> ``CVal`` (mul_cnrs).
        Every add    is ``CVal + CVal`` -> ``CVal`` (CNRS-A addition).
        Binomial coefficients C(n,k) are converted to ``CVal`` via
        ``CVal.from_gaussian``.
        """
        na = len(self.coeffs)
        nb = len(other.coeffs)
        nc = na + nb - 1
        c = [_ZERO_CVAL] * nc

        for i in range(na):
            for j in range(nb):
                # C(i+j, i) as a CNRS-A value
                binom = CVal.from_gaussian(complex(comb(i + j, i), 0))
                # All three multiplications are CNRS-A native
                term = binom * self.coeffs[i] * other.coeffs[j]
                # Addition is CNRS-A native
                c[i + j] = c[i + j] + term

        return CnrsHNative(tuple(c))

    # ------------------------------------------------------------------
    # Truncation and padding
    # ------------------------------------------------------------------

    def truncate(self, n: int) -> "CnrsHNative":
        """Keep only the first n coefficients."""
        return CnrsHNative(self.coeffs[:n])

    def pad(self, n: int) -> "CnrsHNative":
        """Extend to length n by appending zero CVals."""
        if len(self.coeffs) >= n:
            return self
        return CnrsHNative(
            self.coeffs + tuple(_ZERO_CVAL for _ in range(n - len(self.coeffs)))
        )

    # ------------------------------------------------------------------
    # Display and equality
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CnrsHNative):
            return NotImplemented
        n = max(len(self.coeffs), len(other.coeffs))
        return all(
            self.coeff(i).to_gaussian() == other.coeff(i).to_gaussian()
            for i in range(n)
        )

    def __str__(self) -> str:
        cs = [str(c) for c in self.coeffs]
        while len(cs) > 1 and cs[-1] == "0":
            cs.pop()
        return f"CnrsHNative([{', '.join(cs)}])"

    def __repr__(self) -> str:
        return str(self)

    def pretty(self, var: str = "s") -> str:
        """Human-readable EGF polynomial form."""
        terms = []
        for n, d in enumerate(self.coeffs):
            g = d.to_gaussian()
            if g == 0:
                continue
            coeff_str = f"{int(g.real):+d}" if g.imag == 0 else f"+({g})"
            if n == 0:
                terms.append(coeff_str.lstrip("+"))
            elif n == 1:
                terms.append(f"{coeff_str}*{var}")
            else:
                terms.append(f"{coeff_str}*{var}^{n}/{factorial(n)}")
        return " ".join(terms) if terms else "0"


# ---------------------------------------------------------------------------
# Native composition via Faà di Bruno's formula
# ---------------------------------------------------------------------------

def _bell_table(g_coeffs: tuple, order: int) -> list:
    """Build the partial Bell polynomial table B[n][k] as CVals.

    Recurrence (integer arithmetic throughout):

        B[n][k] = sum_{m=1}^{n-k+1}  C(n-1, m-1) * g_m * B[n-m][k-1]

    with B[0][0] = 1,  B[n][0] = 0 (n > 0),  B[0][k] = 0 (k > 0).

    The partial Bell polynomials B_{n,k}(x_1,...,x_{n-k+1}) have INTEGER
    polynomial coefficients (verified symbolically up to n=6).  Evaluated at
    Gaussian-integer EGF coefficients they therefore return Gaussian integers,
    keeping all arithmetic inside CVal (CNRS-A native).
    """
    N = order + 1
    # B[n][k] is a CVal; initialise to zero
    B = [[_ZERO_CVAL] * N for _ in range(N)]
    B[0][0] = _ONE_CVAL

    for n in range(1, N):
        for k in range(1, n + 1):
            val = _ZERO_CVAL
            for m in range(1, n - k + 2):   # m = 1 .. n-k+1
                if m >= len(g_coeffs):
                    continue
                g_m = g_coeffs[m]
                if g_m == _ZERO_CVAL:
                    continue
                binom = _to_cval(comb(n - 1, m - 1))
                val = val + binom * g_m * B[n - m][k - 1]
            B[n][k] = val

    return B


def compose_native(
    f: "CnrsHNative",
    g: "CnrsHNative",
    order: int,
) -> "CnrsHNative":
    """Compose two CnrsHNative series: compute h(s) = f(g(s)).

    Uses Faà di Bruno's formula with the Bell-polynomial recurrence:

        h_0 = f_0          (= f(g(0)) since g(0) = 0)
        h_n = sum_{k=1}^n  f_k * B_{n,k}(g_1, ..., g_{n-k+1})   n >= 1

    All arithmetic (binomial coefficients, Bell values, final sum) is
    performed via CVal.  No Python arithmetic touches the EGF coefficients.

    Parameters
    ----------
    f : outer function (EGF coefficients as CVal)
    g : inner function (EGF coefficients as CVal); must satisfy g_0 = 0
    order : number of output EGF terms (0 .. order inclusive)

    Raises
    ------
    ValueError
        If g.coeff(0) != 0 (composition only defined when g(0) = 0 here).
    NonGaussianCoefficientError
        Propagated if any coefficient is not a Gaussian integer.
    """
    if g.coeff(0).to_gaussian() != 0:
        raise ValueError(
            "compose_native requires g(0) = 0 (i.e. g.coeff(0) = 0). "
            "Shift g by its constant term before composing."
        )

    g_padded = g.pad(order + 1).coeffs   # index 0 .. order
    B = _bell_table(g_padded, order)

    # h_0 = f(g(0)) = f(0) = f_0
    h_coeffs = [f.coeff(0)]

    for n in range(1, order + 1):
        h_n = _ZERO_CVAL
        for k in range(1, n + 1):
            f_k = f.coeff(k)
            if f_k == _ZERO_CVAL:
                continue
            h_n = h_n + f_k * B[n][k]
        h_coeffs.append(h_n)

    return CnrsHNative(tuple(h_coeffs))


# ---------------------------------------------------------------------------
# Native chain rule verification: D(f∘g) = (Df∘g) * Dg
# ---------------------------------------------------------------------------

def verify_chain_rule_native(
    f: "CnrsHNative",
    g: "CnrsHNative",
    *,
    order: int = 6,
    atol: float = 1e-10,
) -> dict:
    """Verify D(f∘g) = (Df∘g) * Dg entirely in CNRS-A coefficient space.

    Both sides are computed via compose_native and the native EGF product,
    with no Python arithmetic on coefficients.

    Returns
    -------
    dict with keys:
      lhs        : CnrsHNative  — D(f∘g) truncated to order terms
      rhs        : CnrsHNative  — (Df∘g)*Dg truncated to order terms
      max_error  : float        — max |lhs_n - rhs_n| over Gaussian values
      passed     : bool
      strings_match : bool      — True iff every coefficient digit string
                                  is identical (stricter than numeric check)
    """
    # LHS: D(f ∘ g)
    fog  = compose_native(f, g, order + 1)
    lhs  = fog.differentiate().truncate(order).pad(order)

    # RHS: (Df ∘ g) * Dg
    df        = f.differentiate()
    dfog      = compose_native(df, g, order).truncate(order).pad(order)
    dg        = g.differentiate().truncate(order).pad(order)
    rhs_full  = (dfog * dg).truncate(order).pad(order)
    rhs       = rhs_full

    errors = [
        abs(lhs.coeff(i).to_gaussian() - rhs.coeff(i).to_gaussian())
        for i in range(order)
    ]
    max_error = max(errors) if errors else 0.0
    strings_match = all(lhs.coeff(i).s == rhs.coeff(i).s for i in range(order))

    return {
        "lhs": lhs,
        "rhs": rhs,
        "max_error": max_error,
        "passed": max_error <= atol,
        "strings_match": strings_match,
    }


# ---------------------------------------------------------------------------
# Native Leibniz verification
# ---------------------------------------------------------------------------

def verify_leibniz(
    f: CnrsHNative,
    g: CnrsHNative,
    *,
    order: int = 8,
    atol: float = 1e-10,
) -> dict:
    """Verify D(f*g) = Df*g + f*Dg entirely in CNRS-A coefficient space.

    Both sides are computed natively.  The comparison converts final
    coefficients to Gaussian (Python complex) for the numeric tolerance check.

    Returns a dict with keys:
      lhs        : CnrsHNative  (D(f*g), truncated to order)
      rhs        : CnrsHNative  (Df*g + f*Dg, truncated to order)
      max_error  : float        (max abs coefficient difference)
      passed     : bool
    """
    ft = f.truncate(order + 1).pad(order + 1)
    gt = g.truncate(order + 1).pad(order + 1)

    lhs = (ft * gt).differentiate().truncate(order).pad(order)

    df = ft.differentiate().truncate(order).pad(order)
    dg = gt.differentiate().truncate(order).pad(order)
    gt_t = gt.truncate(order).pad(order)
    ft_t = ft.truncate(order).pad(order)

    rhs = (df * gt_t + ft_t * dg).truncate(order).pad(order)

    errors = [
        abs(lhs.coeff(i).to_gaussian() - rhs.coeff(i).to_gaussian())
        for i in range(order)
    ]
    max_error = max(errors) if errors else 0.0

    return {
        "lhs": lhs,
        "rhs": rhs,
        "max_error": max_error,
        "passed": max_error <= atol,
    }


# ---------------------------------------------------------------------------
# Native Lagrange inversion: g such that f(g(s)) = s
# ---------------------------------------------------------------------------

# Gaussian integer units: the only values whose reciprocal is also a
# Gaussian integer.  1/u for u in _GAUSSIAN_UNITS gives another unit.
_GAUSSIAN_UNITS: dict[complex, complex] = {
    1+0j:  1+0j,
    -1+0j: -1+0j,
    0+1j:  0-1j,
    0-1j:  0+1j,
}


class InversionError(ValueError):
    """Raised when the series cannot be inverted in Gaussian-integer arithmetic."""


def invert_native(f: "CnrsHNative", order: int) -> "CnrsHNative":
    """Compute the compositional inverse g of f in CNRS-A native arithmetic.

    Returns g such that f(g(s)) = s, computed to ``order`` EGF coefficients.

    All arithmetic is routed through ``CVal`` (CNRS-A digit strings) via
    ``add_cnrs`` / ``mul_cnrs``.  No Python arithmetic touches the EGF
    coefficients directly.

    Requirements
    ------------
    f.coeff(0) = 0
        f(0) = 0 is necessary for a compositional inverse to exist as a
        formal power series.
    f.coeff(1) ∈ {1, −1, i, −i}
        f′(0) must be a Gaussian integer unit so that 1/f′(0) is also a
        Gaussian integer.  Non-unit f′(0) would produce non-integer
        coefficients for g, which cannot be stored in CnrsHNative.

    Algorithm
    ---------
    The recurrence follows directly from f(g(s)) = s expanded via Faà di
    Bruno's formula.  Writing (f ∘ g)_n for the n-th EGF coefficient of the
    composition::

        (f ∘ g)_n = Σ_{k=1}^n  f_k · B_{n,k}(g_1, …, g_{n-k+1})

    Setting this equal to the identity series (1 for n=1, 0 for n≥2) and
    using B_{n,1}(g_1,…,g_n) = g_n gives::

        g_1 = 1 / f_1
        g_n = −(1/f_1) · Σ_{k=2}^n  f_k · B_{n,k}(g_1, …, g_{n-k+1})

    For k ≥ 2 the Bell argument g_{n-k+1} ≤ g_{n-1}, so the sum uses only
    already-computed coefficients.  The Bell table is built incrementally
    alongside the g coefficients, keeping everything within a single pass.

    Parameters
    ----------
    f : CnrsHNative
        The series to invert.  Must satisfy f(0) = 0 and f′(0) ∈ {1,−1,i,−i}.
    order : int
        Number of output EGF coefficients (indices 0 … order−1).

    Returns
    -------
    CnrsHNative
        The compositional inverse g, with g.coeff(0) = 0.

    Raises
    ------
    InversionError
        If f(0) ≠ 0 or f′(0) is not a Gaussian integer unit.
    """
    if order <= 0:
        raise ValueError("order must be positive")

    # --- validate f(0) = 0 ---
    f0 = f.coeff(0).to_gaussian()
    if f0 != 0:
        raise InversionError(
            f"invert_native requires f(0) = 0 (f.coeff(0) = 0); got {f0!r}. "
            "Shift f by its constant term before inverting."
        )

    # --- validate f'(0) is a Gaussian unit ---
    f1_gaussian = f.coeff(1).to_gaussian()
    if f1_gaussian not in _GAUSSIAN_UNITS:
        raise InversionError(
            f"invert_native requires f′(0) = f.coeff(1) to be a Gaussian "
            f"integer unit {{1, −1, i, −i}}; got {f1_gaussian!r}. "
            "Non-unit f′(0) produces non-integer inverse coefficients."
        )
    inv_f1 = _to_cval(_GAUSSIAN_UNITS[f1_gaussian])   # 1/f_1 as CVal

    # --- g array: g_coeffs[n] = g_n (1-indexed EGF coefficient) ---
    # Index 0 is unused (g_0 = 0); we size to order+1 for convenient indexing.
    g_coeffs: list[CVal] = [_ZERO_CVAL] * (order + 1)
    g_coeffs[1] = inv_f1   # g_1 = 1/f_1

    # --- Bell table: B[n][k] as in _bell_table, built incrementally ---
    # We maintain B[n][k] for n = 0..order, k = 0..order.
    # At each step n we can compute B[n][k] for k ≥ 2 from g_1..g_{n-k+1}
    # (already known), then compute g_n, then fill B[n][1] = g_n.
    N = order + 1
    B: list[list[CVal]] = [[_ZERO_CVAL] * N for _ in range(N)]
    B[0][0] = _ONE_CVAL
    # B[1][1] = g_1 (set after g_1 is known)
    if order >= 1:
        B[1][1] = g_coeffs[1]

    for n in range(2, order):
        # Step 1: compute B[n][k] for k = 2..n using g_1..g_{n-k+1} (known)
        for k in range(2, n + 1):
            val = _ZERO_CVAL
            for m in range(1, n - k + 2):   # m = 1 .. n-k+1
                g_m = g_coeffs[m] if m <= order else _ZERO_CVAL
                if g_m == _ZERO_CVAL:
                    continue
                binom = _to_cval(comb(n - 1, m - 1))
                val = val + binom * g_m * B[n - m][k - 1]
            B[n][k] = val

        # Step 2: compute g_n = -(1/f_1) * Σ_{k=2}^n f_k * B[n][k]
        correction = _ZERO_CVAL
        for k in range(2, n + 1):
            f_k = f.coeff(k)
            if f_k == _ZERO_CVAL:
                continue
            correction = correction + f_k * B[n][k]
        g_n = -(inv_f1 * correction)
        g_coeffs[n] = g_n

        # Step 3: fill B[n][1] = g_n (needed by future iterations)
        B[n][1] = g_n

    # --- assemble output: [g_0, g_1, ..., g_{order-1}] ---
    out = tuple(g_coeffs[i] for i in range(order))
    return CnrsHNative(out)


def verify_inversion(
    f: "CnrsHNative",
    order: int,
    *,
    atol: float = 1e-10,
) -> dict:
    """Verify that g = invert_native(f) satisfies f(g(s)) = s at the
    coefficient level, entirely within CNRS-A arithmetic.

    The identity series has EGF coefficients [0, 1, 0, 0, …].
    Both f(g(s)) and the identity are compared coefficient-by-coefficient
    as digit strings (strictest check) and as Gaussian values (numeric).

    Parameters
    ----------
    f : CnrsHNative — the series to invert
    order : int     — number of EGF coefficients to verify
    atol : float    — tolerance for the numeric check

    Returns
    -------
    dict with keys:
      g              : CnrsHNative — the computed inverse
      fog            : CnrsHNative — f(g(s)) truncated to order terms
      max_error      : float       — max |fog_n − id_n| over Gaussian values
      passed         : bool        — True if max_error ≤ atol
      strings_match  : bool        — True iff every digit string is exact
    """
    g = invert_native(f, order)
    fog = compose_native(f, g, order - 1).pad(order)

    # Identity: coeff 0 → 0, coeff 1 → 1, rest → 0
    identity_vals = [0] * order
    if order > 1:
        identity_vals[1] = 1

    errors = [
        abs(fog.coeff(n).to_gaussian() - identity_vals[n])
        for n in range(order)
    ]
    max_error = max(errors) if errors else 0.0

    # Digit-string check: exact match with the identity CVal strings
    id_cvals = [_ZERO_CVAL] * order
    if order > 1:
        id_cvals[1] = _ONE_CVAL
    strings_match = all(fog.coeff(n).s == id_cvals[n].s for n in range(order))

    return {
        "g": g,
        "fog": fog,
        "max_error": max_error,
        "passed": max_error <= atol,
        "strings_match": strings_match,
    }


# ---------------------------------------------------------------------------
# Coefficient-space diagnostic
# ---------------------------------------------------------------------------

def coeff_strings(h: CnrsHNative) -> list[str]:
    """Return the raw CNRS-A digit strings for each coefficient."""
    return [c.s for c in h.coeffs]


__all__ = [
    "CnrsHNative",
    "NonGaussianCoefficientError",
    "InversionError",
    "compose_native",
    "invert_native",
    "verify_inversion",
    "verify_chain_rule_native",
    "verify_leibniz",
    "coeff_strings",
]
