"""
cnrs_ode.py
===========
ODE solver for the CNRS scientific toolkit.

Uses the CNRS-H coefficient recurrence to solve linear ODEs exactly
(up to floating-point precision) within the natural domain s ∈ [0, s_max],
where s_max depends on the number of terms and the eigenvalue magnitude.

The key insight (from Phase C, Session 42): in the CNRS-H EGF convention,
differentiation is an exact coefficient shift.  A linear ODE therefore
becomes a recurrence relation on EGF coefficients — no integration, no
step-size control, no stability analysis.

    y' = λy              →  c[n+1] = λ · c[n]
    y' = λy + f(s)       →  c[n+1] = λ · c[n] + f[n]
    y'' + 2γy' + ω²y = 0 →  c[n+2] = −2γ · c[n+1] − ω² · c[n]

All solutions are returned as OdeSolution objects, which provide:
  - evaluation at any s in the natural domain
  - exact coefficient-level derivative (digit shift)
  - all five observable maps: |y|², Re(y), Im(y), phase, phase_current

Natural domain
--------------
The CNRS-H stream is a truncated EGF series.  With ``terms`` coefficients
and eigenvalue magnitude |λ|, the solution is accurate to tolerance ``tol``
for s ≲ s_max, where:

    s_max ≈ (terms! · tol)^{1/terms} / |λ|

At 25 terms with tol=1e-6:
    |λ| = 1  →  s_max ≈ 5.9 nats
    |λ| = 2  →  s_max ≈ 2.9 nats

For Scale Space applications (s measured in nats, typical range [0, 1]),
25 terms is more than adequate for |λ| ≤ 5.

Public API
----------
Solvers:
    cnrs_solve_linear(lam, y0, terms=25)
        First-order: y' = λy, y(0) = y0.

    cnrs_solve_driven(lam, y0, forcing, terms=25)
        Driven first-order: y' = λy + f(s), y(0) = y0.
        forcing may be a CnrsH stream, a list of EGF coefficients,
        or a callable f(s).

    cnrs_solve_second_order(gamma, omega, y0, dy0, terms=25)
        Damped oscillator: y'' + 2γy' + ω²y = 0.

Result object:
    OdeSolution
        .evaluate(s)        complex value at s
        .derivative()       OdeSolution for dy/ds
        .eigenvalue()       λ extracted from c[1]/c[0] (first-order only)
        .coeffs             tuple of EGF coefficients
        .s_max              approximate upper limit of reliable domain
        .modulus_sq(s)      |y(s)|² as float
        .real_part(s)       Re(y(s)) as float
        .imag_part(s)       Im(y(s)) as float
        .phase(s)           arg(y(s)) in (-π, π]
        .phase_rate(s)      d(arg y)/ds = Im(y'/y)
        .phase_current(s)   |y|² · d(arg y)/ds  (phase-current proxy)

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 42, 2026-06-06
"""

from __future__ import annotations

import cmath
import math
import warnings
from typing import Callable, Optional, Sequence, Union

from .cnrs_h import CnrsH

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

_Scalar = Union[int, float, complex]
_Forcing = Union[CnrsH, Sequence[_Scalar], Callable[[float], complex], None]

DEFAULT_TERMS: int = 25
_TOL_DOMAIN: float = 1e-6


# ---------------------------------------------------------------------------
# Domain safety helper
# ---------------------------------------------------------------------------

def _s_max(terms: int, lam_mag: float, tol: float = _TOL_DOMAIN) -> float:
    """
    Approximate upper bound on s for reliable evaluation of a CNRS-H stream
    with ``terms`` coefficients representing exp(λs) with |λ| = lam_mag.

    Based on the crude bound: the tail term |λs|^terms / terms! < tol.
    """
    if lam_mag == 0:
        return float("inf")
    try:
        return (math.factorial(terms) * tol) ** (1.0 / terms) / lam_mag
    except (OverflowError, ValueError):
        return float("inf")


# ---------------------------------------------------------------------------
# OdeSolution
# ---------------------------------------------------------------------------

class OdeSolution:
    """
    Solution to a linear ODE, stored as a CNRS-H EGF coefficient stream.

    Constructed by the cnrs_solve_* functions; not intended for direct
    instantiation.

    Parameters
    ----------
    stream : CnrsH
        The EGF coefficient stream representing the solution.
    s_max : float
        Approximate upper limit of reliable domain in nats.
    label : str
        Human-readable description of the ODE.
    """

    def __init__(self, stream: CnrsH, s_max: float, label: str = ""):
        self._stream = stream
        self._s_max = s_max
        self._label = label

    # ------------------------------------------------------------------
    # Core access
    # ------------------------------------------------------------------

    @property
    def coeffs(self):
        """EGF coefficient tuple (c[0], c[1], ..., c[N-1])."""
        return self._stream.coeffs

    @property
    def s_max(self) -> float:
        """Approximate upper limit of reliable evaluation domain in nats."""
        return self._s_max

    @property
    def cnrs_h(self) -> CnrsH:
        """The underlying CnrsH stream."""
        return self._stream

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, s: float, warn: bool = True) -> complex:
        """
        Evaluate the solution at scale coordinate s.

        Parameters
        ----------
        s : float   Scale coordinate in nats.
        warn : bool  If True, warn when s exceeds the reliable domain.

        Returns
        -------
        complex
        """
        s_real = float(s.real) if hasattr(s, "real") else float(s)
        if warn and s_real > self._s_max * 1.1:
            warnings.warn(
                f"Evaluating OdeSolution at s={s:.3f} nats, which exceeds "
                f"the reliable domain s_max≈{self._s_max:.3f} nats for "
                f"{len(self.coeffs)} terms.  Results may be inaccurate.  "
                "Increase `terms` or use a step-and-shift strategy.",
                stacklevel=2,
            )
        return self._stream.evaluate(s)

    # ------------------------------------------------------------------
    # Derivative
    # ------------------------------------------------------------------

    def derivative(self) -> "OdeSolution":
        """
        Return an OdeSolution for dy/ds (exact digit-shift differentiation).

        The derivative stream has one fewer coefficient than the original.
        """
        return OdeSolution(
            self._stream.differentiate(),
            self._s_max,
            label=f"d/ds [{self._label}]",
        )

    # ------------------------------------------------------------------
    # Eigenvalue extraction
    # ------------------------------------------------------------------

    def eigenvalue(self) -> complex:
        """
        Extract the complex eigenvalue λ from the coefficient stream.

        For y' = λy: λ = c[1] / c[0].  Exact to machine precision.

        Raises ValueError if c[0] is zero (trivial solution).
        """
        c = self._stream.coeffs
        if len(c) < 2:
            raise ValueError("Need at least 2 coefficients to extract eigenvalue.")
        if abs(c[0]) == 0:
            raise ValueError(
                "c[0] = 0: cannot extract eigenvalue from trivial solution."
            )
        return c[1] / c[0]

    # ------------------------------------------------------------------
    # Observable maps
    # ------------------------------------------------------------------

    def modulus_sq(self, s: float) -> float:
        """|y(s)|² as a Python float."""
        return abs(self.evaluate(s)) ** 2

    def real_part(self, s: float) -> float:
        """Re(y(s)) as a Python float."""
        return self.evaluate(s).real

    def imag_part(self, s: float) -> float:
        """Im(y(s)) as a Python float."""
        return self.evaluate(s).imag

    def phase(self, s: float) -> float:
        """arg(y(s)) in (−π, π] as a Python float."""
        return cmath.phase(self.evaluate(s))

    def phase_rate(self, s: float) -> float:
        """
        d(arg y)/ds = Im(y'/y) at scale coordinate s.

        For y = exp(λs): phase_rate = Im(λ) = ω (exact from eigenvalue).
        For general solutions: computed from the digit-shift derivative.
        """
        y = self.evaluate(s)
        if abs(y) < 1e-30:
            return 0.0
        dy = self.derivative().evaluate(s)
        return (dy / y).imag

    def phase_current(self, s: float) -> float:
        """
        Phase-current proxy J(s) = |y(s)|² · d(arg y)/ds.

        In Scale Space context: J_A = f² ∇_A θ, the configurational
        current from the complex scale potential Ψ_s = f·exp(iθ).
        """
        return self.modulus_sq(s) * self.phase_rate(s)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        n = len(self.coeffs)
        return (
            f"OdeSolution({self._label!r}, {n} terms, "
            f"s_max≈{self._s_max:.2f} nats)"
        )

    def summary(self, s_values: Optional[Sequence[float]] = None) -> str:
        """
        Return a human-readable table of all observables at sample points.

        Parameters
        ----------
        s_values : sequence of float, optional
            Sample points.  Defaults to [0, 0.25, 0.5, 0.75, 1.0].
        """
        if s_values is None:
            s_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        lines = [
            f"OdeSolution: {self._label}",
            f"  Terms: {len(self.coeffs)}   s_max ≈ {self._s_max:.2f} nats",
            f"  {'s':>6}  {'|y|²':>10}  {'Re(y)':>10}  "
            f"{'phase':>10}  {'dθ/ds':>10}  {'J':>10}",
            "  " + "-" * 62,
        ]
        for s in s_values:
            lines.append(
                f"  {s:6.3f}  "
                f"{self.modulus_sq(s):10.6f}  "
                f"{self.real_part(s):10.6f}  "
                f"{self.phase(s):10.6f}  "
                f"{self.phase_rate(s):10.6f}  "
                f"{self.phase_current(s):10.6f}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Forcing helper
# ---------------------------------------------------------------------------

def _forcing_coeffs(
    forcing: _Forcing, terms: int
) -> list:
    """
    Normalise forcing to a list of EGF coefficients of length ``terms``.

    Accepts:
      - None            → all-zero forcing
      - CnrsH stream    → use its coefficients, zero-pad if needed
      - list/tuple      → use directly, zero-pad if needed
      - callable f(s)   → sample Taylor coefficients numerically
                          (only for smooth f; use sparingly)
    """
    if forcing is None:
        return [0] * terms

    if isinstance(forcing, CnrsH):
        c = list(forcing.coeffs)
        return (c + [0] * terms)[:terms]

    if callable(forcing):
        raise TypeError(
            "Callable forcing is not supported. "
            "Pass EGF coefficients as a list or CnrsH stream. "
            "sin(s): [0, 1, 0, -1, 0, 1, ...]  "
            "cos(s): [1, 0, -1, 0, 1, 0, ...]"
        )

    # Sequence
    c = list(forcing)
    return (c + [0] * terms)[:terms]


# ---------------------------------------------------------------------------
# Solvers
# ---------------------------------------------------------------------------

def cnrs_solve_linear(
    lam: _Scalar,
    y0: _Scalar = 1.0,
    terms: int = DEFAULT_TERMS,
) -> OdeSolution:
    """
    Solve y' = λy, y(0) = y0 via CNRS-H coefficient recurrence.

    The EGF coefficient recurrence is:

        c[0] = y0
        c[n+1] = λ · c[n]   for n = 0, 1, 2, ...

    This gives c[n] = y0 · λⁿ, corresponding to y(s) = y0 · exp(λs).
    Exact to floating-point precision within the natural domain.

    Parameters
    ----------
    lam : complex   Eigenvalue λ = α + iω.
    y0 : complex    Initial condition y(0).
    terms : int     Number of EGF coefficients (default 25).

    Returns
    -------
    OdeSolution
    """
    lam = complex(lam)
    y0 = complex(y0)
    c = [complex(0)] * terms
    c[0] = y0
    for n in range(terms - 1):
        c[n + 1] = lam * c[n]
    stream = CnrsH.from_list(c)
    s_max = _s_max(terms, abs(lam))
    return OdeSolution(stream, s_max, label=f"y'=({lam})y, y(0)={y0}")


def cnrs_solve_driven(
    lam: _Scalar,
    y0: _Scalar = 1.0,
    forcing: _Forcing = None,
    terms: int = DEFAULT_TERMS,
) -> OdeSolution:
    """
    Solve y' = λy + f(s), y(0) = y0 via CNRS-H coefficient recurrence.

    The EGF coefficient recurrence is:

        c[0] = y0
        c[n+1] = λ · c[n] + f[n]

    where f[n] are the EGF coefficients of the forcing function f(s).

    Parameters
    ----------
    lam : complex    Eigenvalue λ.
    y0 : complex     Initial condition y(0).
    forcing : CnrsH, list, callable, or None
        Forcing function f(s) as a CnrsH stream, list of EGF coefficients,
        or a callable f(s) → complex.  None means zero forcing (reduces
        to cnrs_solve_linear).
    terms : int      Number of EGF coefficients (default 25).

    Returns
    -------
    OdeSolution
    """
    lam = complex(lam)
    y0 = complex(y0)
    f = _forcing_coeffs(forcing, terms)
    c = [complex(0)] * terms
    c[0] = y0
    for n in range(terms - 1):
        c[n + 1] = lam * c[n] + complex(f[n])
    stream = CnrsH.from_list(c)
    s_max = _s_max(terms, abs(lam))
    label = f"y'=({lam})y+f(s), y(0)={y0}"
    return OdeSolution(stream, s_max, label=label)


def cnrs_solve_second_order(
    gamma: float,
    omega: float,
    y0: _Scalar = 1.0,
    dy0: _Scalar = 0.0,
    terms: int = DEFAULT_TERMS,
) -> OdeSolution:
    """
    Solve y'' + 2γy' + ω²y = 0, y(0) = y0, y'(0) = dy0.

    The EGF coefficient recurrence is:

        c[0] = y0
        c[1] = dy0
        c[n+2] = −2γ · c[n+1] − ω² · c[n]

    This covers:
      - γ = 0          → pure oscillator (cos/sin)
      - 0 < γ < ω      → underdamped oscillator (damped sinusoid)
      - γ = ω          → critically damped
      - γ > ω          → overdamped (two real exponentials)
      - γ < 0          → growing oscillator

    The general solution is:

        y(s) = A · exp(λ₁s) + B · exp(λ₂s)

    where λ₁,₂ = −γ ± i√(ω²−γ²) and A, B are determined by initial
    conditions.  The CNRS-H stream evaluates this exactly.

    Parameters
    ----------
    gamma : float   Damping coefficient γ (half the linear damping term).
    omega : float   Natural frequency ω.
    y0 : complex    Initial displacement y(0).
    dy0 : complex   Initial velocity y'(0).
    terms : int     Number of EGF coefficients (default 25).

    Returns
    -------
    OdeSolution
    """
    y0 = complex(y0)
    dy0 = complex(dy0)
    omega2 = omega ** 2
    c = [complex(0)] * terms
    c[0] = y0
    if terms > 1:
        c[1] = dy0
    for n in range(terms - 2):
        c[n + 2] = -2 * gamma * c[n + 1] - omega2 * c[n]
    stream = CnrsH.from_list(c)
    # Use |lambda| = sqrt(gamma^2 + omega^2) as magnitude estimate
    lam_mag = math.sqrt(gamma ** 2 + omega ** 2)
    s_max = _s_max(terms, lam_mag)
    label = f"y''+2({gamma})y'+({omega}²)y=0, y(0)={y0}, y'(0)={dy0}"
    return OdeSolution(stream, s_max, label=label)
