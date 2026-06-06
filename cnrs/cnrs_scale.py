"""
cnrs_scale.py
=============
ScaleLaw — a CNRS-H backed scale-law toolkit for the CNRS scientific toolkit.

Provides scale-law construction, fitting, differentiation, allometric analysis,
and Turing-threshold detection, all rooted in the CNRS-H EGF calculus.

The core insight (from Phase C / Session 42): in the CNRS-H EGF convention,
differentiation is an exact coefficient shift.  A scale law f(s) represented
as a CNRS-H stream therefore admits exact log-derivative, allometric-exponent
extraction, and threshold detection — all from coefficient arithmetic alone.

Architecture
------------
A ScaleLaw wraps a CnrsH stream (EGF coefficients) and presents:
  - evaluation at any s within the natural domain
  - exact coefficient-level derivative (digit shift)
  - log-derivative lambda(s) = f'(s)/f(s)  (allometric exponent proxy)
  - allometric exponent extraction via least-squares fit in log-scale
  - Turing threshold detection: find s where Re(lambda(s)) crosses a threshold

The three-workflow pattern applies here too:
  A. early real reduction  (use .modulus or .real_part directly)
  B. late complex reduction (use .evaluate then measure)
  C. CNRS complex-state preservation (keep stream; extract at end)

Natural domain
--------------
A CNRS-H stream with ``terms`` coefficients is accurate up to s ≈ s_max,
estimated as (terms! * tol)^{1/terms} / |lambda|, where lambda is the
leading eigenvalue.  At 25 terms with tol=1e-6 and |lambda|=1: s_max ≈ 5.9.
For Scale Space applications (s in nats, typical range [0, 1 nat]), 25 terms
is more than adequate.

Turing threshold
----------------
The Turing instability condition (Paper 18, §3) is active for s < s_exit,
where s_exit is detected as the point where Re(log_derivative(s)) crosses
a user-supplied threshold.  See turing_threshold().

Allometric fitting
------------------
A power law f(ℓ) ~ A * ℓ^b is linear in log-log coordinates:
    log f = log A + b * log ℓ = log A + b * s   (s = log(ℓ/ℓ_ref))

fit_allometric(s, y) fits b and A via least-squares on log(y) vs s,
and returns an AllometricResult with a ScaleLaw backed by an EGF stream
so the fit can be differentiated and extended analytically.

Public API
----------
Construction:
    ScaleLaw.exponential(lam, scale=1, terms=32)
        f(s) = scale * exp(lam * s)

    ScaleLaw.from_coeffs(coeffs, name=None)
        Directly from EGF coefficient list.

    ScaleLaw.from_cnrsh(h, name=None)
        From an existing CnrsH stream.

Evaluation:
    law(s)                  complex value at s  (scalar or numpy array)
    law.evaluate(s)         same, scalar only
    law.s_max               approximate upper bound of reliable domain
    law.derivative()        ScaleLaw for df/ds  (exact digit shift)
    law.integral(c)         ScaleLaw for antiderivative
    law.log_derivative(s)   f'(s)/f(s) as complex scalar

Observation maps (return float or float array):
    law.modulus(s)          |f(s)|
    law.modulus_sq(s)       |f(s)|^2
    law.real_part(s)        Re f(s)
    law.imag_part(s)        Im f(s)
    law.phase(s)            arg f(s) in (-pi, pi]
    law.phase_rate(s)       Im(f'(s)/f(s))  (instantaneous freq in s)

Fitting:
    fit_exponential(s, y, terms=32, name=None)  →  FitResult
    fit_egf(s, y, degree, name=None)            →  ScaleLaw
    fit_allometric(s, y, name=None)             →  AllometricResult

Threshold detection:
    turing_threshold(law, threshold, s_lo, s_hi, n_points=200)  →  TuringResult

Result objects:
    FitResult        .law, .lam, .scale, .residual
    AllometricResult .law, .exponent, .amplitude, .residual, .r_squared
    TuringResult     .s_exit, .threshold, .crossed, .lambda_lo, .lambda_hi

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 43, 2026-06-06
"""

from __future__ import annotations

import cmath
import math
import warnings
from dataclasses import dataclass
from typing import Optional, Sequence, Union

import numpy as np

from .cnrs_h import CnrsH


# ---------------------------------------------------------------------------
# Domain warning helper
# ---------------------------------------------------------------------------

def _s_max_estimate(terms: int, eigenvalue_mag: float, tol: float = 1e-6) -> float:
    """Estimate upper reliable domain for a CNRS-H stream."""
    if eigenvalue_mag < 1e-15:
        return float("inf")
    log_factorial = sum(math.log(k) for k in range(1, terms + 1))
    log_smax = (log_factorial + math.log(tol)) / terms
    return math.exp(log_smax) / eigenvalue_mag


def _domain_warn(s: float, s_max: float, name: str) -> None:
    if s_max < float("inf") and abs(s) > s_max:
        warnings.warn(
            f"ScaleLaw '{name}': s={s:.3f} is outside the reliable domain "
            f"[0, {s_max:.3f}].  Result may be inaccurate.",
            stacklevel=3,
        )


# ---------------------------------------------------------------------------
# Core ScaleLaw class
# ---------------------------------------------------------------------------

class ScaleLaw:
    """
    A CNRS-H backed scale law f(s).

    Wraps a CnrsH EGF stream and provides evaluation, differentiation,
    log-derivative, and observable maps.
    """

    def __init__(self, h: CnrsH, name: str = "scale_law",
                 _s_max: Optional[float] = None):
        self._h = h
        self.name = name
        coeffs = list(h.coeffs) if hasattr(h, "coeffs") else []
        if len(coeffs) >= 2 and abs(coeffs[0]) > 1e-15:
            lam_mag = abs(coeffs[1] / coeffs[0])
            self.s_max = (_s_max if _s_max is not None
                          else _s_max_estimate(len(coeffs), lam_mag))
        else:
            self.s_max = _s_max if _s_max is not None else float("inf")

    # ---- construction -------------------------------------------------------

    @classmethod
    def exponential(cls, lam: complex, scale: complex = 1.0,
                    terms: int = 32, name: Optional[str] = None) -> "ScaleLaw":
        """f(s) = scale * exp(lam * s)."""
        coeffs = [scale * (lam ** n) for n in range(terms)]
        h = CnrsH.from_list(coeffs)
        lam_mag = abs(lam)
        s_max = _s_max_estimate(terms, lam_mag) if lam_mag > 1e-15 else float("inf")
        label = name or f"{scale}*exp(({lam})*s)"
        return cls(h, name=label, _s_max=s_max)

    @classmethod
    def from_coeffs(cls, coeffs: Sequence[complex],
                    name: Optional[str] = None) -> "ScaleLaw":
        """From a list of EGF coefficients [c0, c1, c2, ...]."""
        h = CnrsH.from_list(list(coeffs))
        return cls(h, name=name or "scale_law")

    @classmethod
    def from_cnrsh(cls, h: CnrsH, name: Optional[str] = None) -> "ScaleLaw":
        """From an existing CnrsH stream."""
        return cls(h, name=name or "scale_law")

    # ---- evaluation ---------------------------------------------------------

    def evaluate(self, s: Union[float, complex]) -> complex:
        """Complex value f(s) at a single point."""
        s_real = float(s.real if hasattr(s, "real") else s)
        _domain_warn(s_real, self.s_max, self.name)
        return self._h.evaluate(complex(s))

    def __call__(self, s):
        """Evaluate at s (scalar or numpy array)."""
        if np.ndim(s) == 0:
            return self.evaluate(complex(s))
        return np.array([self.evaluate(complex(x))
                         for x in np.asarray(s).ravel()],
                        dtype=complex).reshape(np.shape(s))

    # ---- calculus -----------------------------------------------------------

    def derivative(self, name: Optional[str] = None) -> "ScaleLaw":
        """df/ds via exact CNRS-H digit shift."""
        dh = self._h.differentiate()
        return ScaleLaw(dh, name=name or f"D({self.name})", _s_max=self.s_max)

    def integral(self, constant: complex = 0.0,
                 name: Optional[str] = None) -> "ScaleLaw":
        """Antiderivative ∫f ds via CNRS-H digit prepend."""
        ih = self._h.integrate(constant)
        return ScaleLaw(ih, name=name or f"I({self.name})", _s_max=self.s_max)

    def log_derivative(self, s: Union[float, complex]) -> complex:
        """f'(s)/f(s) — allometric exponent proxy at s."""
        f_val = self.evaluate(s)
        df_val = self.derivative().evaluate(s)
        if abs(f_val) < 1e-15:
            return complex(float("nan"), float("nan"))
        return df_val / f_val

    # ---- observation maps ---------------------------------------------------

    def modulus(self, s) -> Union[float, np.ndarray]:
        """|f(s)|."""
        v = self(s)
        return np.abs(v) if np.ndim(v) > 0 else abs(v)

    def modulus_sq(self, s) -> Union[float, np.ndarray]:
        """|f(s)|²."""
        v = self(s)
        return (v * v.conjugate()).real if np.ndim(v) == 0 else (v * np.conj(v)).real

    def real_part(self, s) -> Union[float, np.ndarray]:
        """Re f(s)."""
        return self(s).real

    def imag_part(self, s) -> Union[float, np.ndarray]:
        """Im f(s)."""
        return self(s).imag

    def phase(self, s) -> Union[float, np.ndarray]:
        """arg f(s) in (-pi, pi]."""
        v = self(s)
        if np.ndim(v) == 0:
            return cmath.phase(v)
        return np.angle(v)

    def phase_rate(self, s) -> Union[float, np.ndarray]:
        """Im(f'(s)/f(s)) — instantaneous phase rate in s."""
        if np.ndim(s) == 0:
            return self.log_derivative(s).imag
        return np.array([self.log_derivative(complex(x)).imag
                         for x in np.asarray(s).ravel()],
                        dtype=float).reshape(np.shape(s))

    def __repr__(self) -> str:
        return f"ScaleLaw(name={self.name!r}, s_max={self.s_max:.2f})"


# ---------------------------------------------------------------------------
# Result objects
# ---------------------------------------------------------------------------

@dataclass
class FitResult:
    """Result of fit_exponential."""
    law: ScaleLaw
    lam: complex
    scale: complex
    residual: float


@dataclass
class AllometricResult:
    """Result of fit_allometric."""
    law: ScaleLaw
    exponent: float
    amplitude: float
    residual: float
    r_squared: float


@dataclass
class TuringResult:
    """Result of turing_threshold."""
    s_exit: Optional[float]
    threshold: float
    crossed: bool
    lambda_lo: float
    lambda_hi: float


# ---------------------------------------------------------------------------
# Fitting functions
# ---------------------------------------------------------------------------

def fit_exponential(s: Sequence[float], y: Sequence[complex],
                    terms: int = 32, name: str = "exp_fit") -> FitResult:
    """
    Fit y(s) ≈ scale * exp(lam * s) via least-squares.

    Step 1: linear fit of log|y| vs s → Re(lam) and log|scale|.
    Step 2: phase residual fit vs s → Im(lam).

    Works best when y is well approximated by a single exponential.
    For multi-exponential data use fit_egf.
    """
    s_arr = np.asarray(s, dtype=float)
    y_arr = np.asarray(y, dtype=complex)
    n = len(s_arr)

    log_abs_y = np.log(np.abs(y_arr) + 1e-300)
    A_mat = np.column_stack([np.ones(n), s_arr])
    coeffs_real, *_ = np.linalg.lstsq(A_mat, log_abs_y, rcond=None)
    log_A_real = float(coeffs_real[0])
    re_lam = float(coeffs_real[1])

    phase_y = np.unwrap(np.angle(y_arr))
    coeffs_phase, *_ = np.linalg.lstsq(A_mat, phase_y, rcond=None)
    phase_intercept = float(coeffs_phase[0])
    im_lam = float(coeffs_phase[1])

    lam = complex(re_lam, im_lam)
    A_mag = math.exp(log_A_real)
    scale = complex(A_mag * math.cos(phase_intercept),
                    A_mag * math.sin(phase_intercept))

    law = ScaleLaw.exponential(lam, scale=scale, terms=terms, name=name)
    y_pred = np.array([law.evaluate(complex(x)) for x in s_arr], dtype=complex)
    residual = float(np.sqrt(np.mean(np.abs(y_arr - y_pred) ** 2)))

    return FitResult(law=law, lam=lam, scale=scale, residual=residual)


def fit_egf(s: Sequence[float], y: Sequence[complex],
            degree: int, name: str = "egf_fit") -> ScaleLaw:
    """
    Fit y(s) ≈ Σ_{n=0}^{degree} a_n * s^n / n!  (polynomial EGF).

    Returns a ScaleLaw backed by the fitted EGF coefficients.
    Supports smooth but non-exponential scale laws.
    """
    s_arr = np.asarray(s, dtype=float)
    y_arr = np.asarray(y, dtype=complex)
    A = np.vstack([(s_arr ** n) / math.factorial(n)
                   for n in range(degree + 1)]).T
    coeffs, *_ = np.linalg.lstsq(A, y_arr, rcond=None)
    return ScaleLaw.from_coeffs(coeffs.tolist(), name=name)


def fit_allometric(s: Sequence[float], y: Sequence[float],
                   name: str = "allometric_fit") -> AllometricResult:
    """
    Fit a power law y ~ A * exp(b * s)  (allometric scaling).

    In nat coordinates s = log(ℓ/ℓ_ref):
        log y = log A + b * s

    Fits b (the allometric exponent) and A = exp(intercept) via
    least-squares on log(|y|) vs s.

    Returns AllometricResult with:
        .exponent  — b  (b≈0.75: Kleiber; b=1: isometric; b>1: superlinear)
        .amplitude — A  (pre-factor at s=0)
        .law       — ScaleLaw for the fitted exponential
        .residual  — RMS residual in log domain
        .r_squared — R^2 in log domain

    All y must be positive (power-law domain).
    """
    s_arr = np.asarray(s, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if np.any(y_arr <= 0):
        raise ValueError(
            "fit_allometric: all y values must be positive (power-law domain).")

    log_y = np.log(y_arr)
    n = len(s_arr)
    A_mat = np.column_stack([np.ones(n), s_arr])
    coeffs, *_ = np.linalg.lstsq(A_mat, log_y, rcond=None)
    intercept, exponent = float(coeffs[0]), float(coeffs[1])
    amplitude = math.exp(intercept)

    log_y_pred = intercept + exponent * s_arr
    rms_residual = float(np.sqrt(np.mean((log_y - log_y_pred) ** 2)))
    ss_res = float(np.sum((log_y - log_y_pred) ** 2))
    ss_tot = float(np.sum((log_y - np.mean(log_y)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 1.0

    law = ScaleLaw.exponential(lam=complex(exponent, 0.0),
                               scale=complex(amplitude, 0.0),
                               terms=32, name=name)

    return AllometricResult(law=law, exponent=exponent, amplitude=amplitude,
                            residual=rms_residual, r_squared=r_squared)


# ---------------------------------------------------------------------------
# Turing threshold detection
# ---------------------------------------------------------------------------

def turing_threshold(law: ScaleLaw, threshold: float,
                     s_lo: float, s_hi: float,
                     n_points: int = 200) -> TuringResult:
    """
    Find s_exit where Re(log_derivative(s)) crosses ``threshold``.

    The Turing instability (Paper 18) is active for s < s_exit.
    This function locates s_exit as the root of:
        Re(f'(s)/f(s)) - threshold = 0

    Uses uniform sampling followed by bisection for accuracy.
    Returns the first (smallest-s) crossing if multiple exist.

    Parameters
    ----------
    law       : ScaleLaw for the activator mode
    threshold : target value for Re(log_derivative)
    s_lo      : lower bound of search interval
    s_hi      : upper bound of search interval
    n_points  : sampling resolution for initial sign-change detection

    Returns
    -------
    TuringResult
        .s_exit    — crossing point (float) or None
        .crossed   — True if crossing found
        .threshold — the threshold searched for
        .lambda_lo — Re(log_derivative) at s_lo
        .lambda_hi — Re(log_derivative) at s_hi
    """
    s_vals = np.linspace(s_lo, s_hi, n_points)
    ld_vals = np.array([law.log_derivative(complex(x)).real for x in s_vals])

    lambda_lo = float(ld_vals[0])
    lambda_hi = float(ld_vals[-1])

    diff = ld_vals - threshold
    sign_changes = np.where(np.diff(np.sign(diff)))[0]

    if len(sign_changes) == 0:
        return TuringResult(s_exit=None, threshold=threshold,
                            crossed=False, lambda_lo=lambda_lo,
                            lambda_hi=lambda_hi)

    # Bisect around first sign change
    idx = int(sign_changes[0])
    a, b = float(s_vals[idx]), float(s_vals[idx + 1])
    fa = law.log_derivative(complex(a)).real - threshold
    fb = law.log_derivative(complex(b)).real - threshold

    for _ in range(52):
        mid = 0.5 * (a + b)
        fm = law.log_derivative(complex(mid)).real - threshold
        if abs(fm) < 1e-12:
            break
        if fa * fm < 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm

    return TuringResult(s_exit=0.5 * (a + b), threshold=threshold,
                        crossed=True, lambda_lo=lambda_lo, lambda_hi=lambda_hi)
