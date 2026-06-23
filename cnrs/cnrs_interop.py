"""
cnrs_interop.py
===============
NumPy / SciPy interoperability bridge for the CNRS Scientific Toolkit.

Provides clean, two-way conversion between CNRS types and standard
scientific-Python objects, plus benchmark utilities that compare CNRS-H
coefficient-recurrence ODE solutions against scipy.integrate.solve_ivp.

The three-workflow pattern from the rest of the toolkit applies here too:
  A. early real reduction  — convert to numpy immediately, use scipy
  B. late complex reduction — keep CNRS-H stream, convert only at observation
  C. CNRS complex-state    — maintain CNRS representation throughout

This module makes workflow B/C interoperable with workflow A without forcing
a choice: you can pass a CNRS result to any scipy/numpy function, or import
a scipy result into a CnrsH stream for exact digit-shift differentiation.

Public API
----------
Type conversion:
    cnrsh_to_numpy(h, s_vals)          CnrsH stream → np.ndarray (complex128)
    numpy_to_cnrsh(y_vals, s_vals, degree) np.ndarray → CnrsH (EGF fit)
    ode_solution_to_numpy(sol, s_vals)  OdeSolution → np.ndarray
    cnrs_complex_to_numpy(czs)          list[CnrsComplex] → np.ndarray

SciPy ODE bridge:
    cnrs_to_scipy_ivp(sol, s_vals)      OdeSolution → scipy Bunch (compatible)
    scipy_ivp_to_cnrsh(ivp_result, degree) scipy Bunch → CnrsH (EGF fit)
    solve_and_compare(lam, y0, s_vals, terms)  → ComparisonResult

Benchmark utilities:
    benchmark_linear(lam, y0, s_vals, terms, n_repeat) → BenchmarkResult
    benchmark_second_order(gamma, omega, y0, dy0, s_vals, terms) → BenchmarkResult

Observation-map array extractors (vectorised over s_vals):
    modulus_array(sol, s_vals)          → np.ndarray of |f(s)|
    modulus_sq_array(sol, s_vals)       → np.ndarray of |f(s)|²
    real_array(sol, s_vals)             → np.ndarray of Re f(s)
    imag_array(sol, s_vals)             → np.ndarray of Im f(s)
    phase_array(sol, s_vals)            → np.ndarray of arg f(s)
    phase_rate_array(sol, s_vals)       → np.ndarray of Im(f'/f)

Result objects:
    ComparisonResult   .s_vals, .cnrs_vals, .scipy_vals, .abs_err, .rel_err,
                       .max_abs_err, .max_rel_err, .cnrs_time_ms, .scipy_time_ms
    BenchmarkResult    .label, .n_points, .n_repeat, .cnrs_ms, .scipy_ms,
                       .max_rel_err, .speedup_factor, .summary()

Optional pandas export:
    to_dataframe(sol, s_vals, cols)     → pd.DataFrame  (requires pandas)

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 43, 2026-06-06
"""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Union

import numpy as np

import sys

from .cnrs_h import CnrsH
from .cnrs_ode import OdeSolution, cnrs_solve_linear, cnrs_solve_second_order
from .cnrs_scale import fit_egf, ScaleLaw


# ---------------------------------------------------------------------------
# Type conversions: CNRS → numpy
# ---------------------------------------------------------------------------

def cnrsh_to_numpy(h: CnrsH, s_vals: Sequence[float]) -> np.ndarray:
    """
    Evaluate a CnrsH EGF stream at each s in s_vals.

    Returns np.ndarray of complex128, shape (len(s_vals),).

    Parameters
    ----------
    h      : CnrsH stream
    s_vals : 1-D sequence of real evaluation points

    Notes
    -----
    This is Workflow B late-reduction: the EGF stream is maintained exactly
    until this call, then converted to numpy for further processing.
    """
    s_arr = np.asarray(s_vals, dtype=float)
    return np.array([h.evaluate(complex(s)) for s in s_arr], dtype=complex)


def numpy_to_cnrsh(y_vals: np.ndarray, s_vals: Sequence[float],
                   degree: int = 12) -> CnrsH:
    """
    Fit a CnrsH EGF stream to numpy data y_vals evaluated at s_vals.

    Uses polynomial EGF least-squares fit (via cnrs_scale.fit_egf).
    The returned stream can be differentiated, integrated, and evaluated
    exactly within its reliable domain.

    Parameters
    ----------
    y_vals : complex or real numpy array, shape (n,)
    s_vals : 1-D sequence of real points, shape (n,)
    degree : EGF polynomial degree (default 12; increase for smoother data)

    Returns
    -------
    CnrsH stream — the EGF coefficient stream fitted to the data.
    """
    law = fit_egf(s_vals, y_vals.astype(complex), degree=degree)
    # Return a plain CnrsH stream for backward compatibility.
    # law._mode holds a CnrsHMode; extract the fast-path backend.
    mode = law._mode
    if mode.native:
        return mode.backend.to_cnrs_h()
    return mode.backend


def ode_solution_to_numpy(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """
    Evaluate an OdeSolution at each s in s_vals.

    Returns np.ndarray of complex128, shape (len(s_vals),).
    """
    s_arr = np.asarray(s_vals, dtype=float)
    return np.array([sol.evaluate(float(s)) for s in s_arr], dtype=complex)


def cnrs_complex_to_numpy(czs) -> np.ndarray:
    """
    Convert a list of CnrsComplex objects to np.ndarray of complex128.

    Delegates to cnrs_complex.to_numpy() but with a graceful fallback
    if the CnrsComplex type is not available.
    """
    try:
        from .cnrs_complex import to_numpy
        return to_numpy(czs)
    except ImportError:
        return np.array([complex(z) for z in czs], dtype=complex)


# ---------------------------------------------------------------------------
# Observation-map array extractors (vectorised)
# ---------------------------------------------------------------------------

def modulus_array(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """|f(s)| at each s — numpy array, float64."""
    return np.abs(ode_solution_to_numpy(sol, s_vals))


def modulus_sq_array(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """|f(s)|² at each s — numpy array, float64."""
    v = ode_solution_to_numpy(sol, s_vals)
    return (v * np.conj(v)).real


def real_array(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """Re f(s) at each s — numpy array, float64."""
    return ode_solution_to_numpy(sol, s_vals).real


def imag_array(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """Im f(s) at each s — numpy array, float64."""
    return ode_solution_to_numpy(sol, s_vals).imag


def phase_array(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """arg f(s) in (-pi, pi] at each s — numpy array, float64."""
    return np.angle(ode_solution_to_numpy(sol, s_vals))


def phase_rate_array(sol: OdeSolution, s_vals: Sequence[float]) -> np.ndarray:
    """
    Im(f'(s)/f(s)) at each s — numpy array, float64.

    The instantaneous angular frequency in s. For f = exp(lam*s),
    this equals Im(lam) exactly.
    """
    dsol = sol.derivative()
    vals = ode_solution_to_numpy(sol, s_vals)
    dvals = ode_solution_to_numpy(dsol, s_vals)
    with np.errstate(divide='ignore', invalid='ignore'):
        ld = np.where(np.abs(vals) > 1e-15, dvals / vals,
                      complex(float('nan')))
    return np.imag(ld)


# ---------------------------------------------------------------------------
# SciPy ODE bridge
# ---------------------------------------------------------------------------

def cnrs_to_scipy_ivp(sol: OdeSolution,
                      s_vals: Sequence[float]) -> object:
    """
    Convert a CNRS OdeSolution to a scipy-compatible result Bunch.

    Returns an object with attributes matching scipy.integrate.solve_ivp:
        .t   — s_vals as float64 array
        .y   — shape (2, n): [Re(f(s)), Im(f(s))]
        .success — True
        .message — description

    This allows CNRS results to be passed to any scipy post-processing
    function that expects a solve_ivp output.
    """
    from types import SimpleNamespace
    s_arr = np.asarray(s_vals, dtype=float)
    vals = ode_solution_to_numpy(sol, s_arr)
    return SimpleNamespace(
        t=s_arr,
        y=np.vstack([vals.real, vals.imag]),
        success=True,
        message=f"CNRS-H EGF solution: {getattr(sol, '_label', '')!r}",
        sol=None,
        t_events=None,
        y_events=None,
        nfev=0,
        njev=0,
        nlu=0,
        status=0,
    )


def scipy_ivp_to_cnrsh(ivp_result, degree: int = 12) -> CnrsH:
    """
    Fit a CnrsH stream to the output of scipy.integrate.solve_ivp.

    Extracts the solution from ivp_result.y (first row = Re, second = Im,
    or just first row if real) and ivp_result.t, then fits a polynomial EGF.

    Returns CnrsH stream that can be differentiated, integrated, and
    evaluated exactly within the EGF domain.

    Parameters
    ----------
    ivp_result : scipy solve_ivp output (or compatible SimpleNamespace)
    degree     : EGF polynomial degree for fitting
    """
    t = ivp_result.t
    y = ivp_result.y
    if y.shape[0] >= 2:
        vals = y[0] + 1j * y[1]
    else:
        vals = y[0].astype(complex)
    return numpy_to_cnrsh(vals, t, degree=degree)


# ---------------------------------------------------------------------------
# Solve and compare
# ---------------------------------------------------------------------------

@dataclass
class ComparisonResult:
    """
    Side-by-side comparison of CNRS-H and scipy.integrate.solve_ivp.

    Attributes
    ----------
    s_vals         : evaluation points
    cnrs_vals      : CNRS-H evaluated values (complex)
    scipy_vals     : scipy solution values (complex)
    exact_vals     : exact analytical values (complex), if provided
    abs_err        : |cnrs - scipy| at each point
    rel_err        : |cnrs - scipy| / (|scipy| + eps) at each point
    max_abs_err    : max |cnrs - scipy|
    max_rel_err    : max relative error
    cnrs_time_ms   : CNRS-H solve time in ms
    scipy_time_ms  : scipy solve time in ms
    label          : description of the problem
    """
    s_vals:       np.ndarray
    cnrs_vals:    np.ndarray
    scipy_vals:   np.ndarray
    exact_vals:   Optional[np.ndarray]
    abs_err:      np.ndarray
    rel_err:      np.ndarray
    max_abs_err:  float
    max_rel_err:  float
    cnrs_time_ms: float
    scipy_time_ms: float
    label:        str = ""

    def summary(self) -> str:
        lines = [
            f"ComparisonResult: {self.label}",
            f"  Points:          {len(self.s_vals)}",
            f"  Max |CNRS-scipy|: {self.max_abs_err:.3e}",
            f"  Max rel error:    {self.max_rel_err:.3e}",
            f"  CNRS time:        {self.cnrs_time_ms:.2f} ms",
            f"  scipy time:       {self.scipy_time_ms:.2f} ms",
            f"  Speed ratio:      {self.scipy_time_ms/max(self.cnrs_time_ms,1e-9):.2f}x "
            f"({'CNRS faster' if self.cnrs_time_ms < self.scipy_time_ms else 'scipy faster'})",
        ]
        if self.exact_vals is not None:
            cnrs_exact = np.max(np.abs(self.cnrs_vals - self.exact_vals))
            scipy_exact = np.max(np.abs(self.scipy_vals - self.exact_vals))
            lines += [
                f"  CNRS vs exact:    {cnrs_exact:.3e}",
                f"  scipy vs exact:   {scipy_exact:.3e}",
            ]
        return '\n'.join(lines)


def solve_and_compare(
    lam: complex,
    y0: complex,
    s_vals: Sequence[float],
    terms: int = 30,
    label: str = "",
) -> ComparisonResult:
    """
    Solve y' = lam*y, y(0)=y0 with both CNRS-H and scipy, compare results.

    CNRS-H: exact coefficient recurrence (cnrs_solve_linear).
    scipy:  solve_ivp with RK45, dense_output=False.

    Both are evaluated at s_vals. Exact solution: y0 * exp(lam * s).

    Parameters
    ----------
    lam    : eigenvalue
    y0     : initial condition
    s_vals : evaluation points (must start at or near 0)
    terms  : CNRS-H EGF terms
    label  : description for ComparisonResult

    Returns
    -------
    ComparisonResult
    """
    from scipy.integrate import solve_ivp

    s_arr = np.asarray(s_vals, dtype=float)
    s_end = float(s_arr[-1])

    # CNRS-H solve
    t0 = time.perf_counter()
    sol = cnrs_solve_linear(lam=lam, y0=y0, terms=terms)
    cnrs_vals = ode_solution_to_numpy(sol, s_arr)
    cnrs_ms = (time.perf_counter() - t0) * 1000

    # scipy solve (real system: [Re(y), Im(y)])
    def rhs(t, z):
        y_c = z[0] + 1j * z[1]
        dy = lam * y_c
        return [dy.real, dy.imag]

    t0 = time.perf_counter()
    ivp = solve_ivp(rhs, [0.0, s_end], [y0.real, y0.imag],
                    t_eval=s_arr, method='RK45', rtol=1e-10, atol=1e-12)
    scipy_vals = ivp.y[0] + 1j * ivp.y[1]
    scipy_ms = (time.perf_counter() - t0) * 1000

    # Exact
    exact_vals = y0 * np.exp(lam * s_arr)

    abs_err = np.abs(cnrs_vals - scipy_vals)
    rel_err = abs_err / (np.abs(scipy_vals) + 1e-300)

    return ComparisonResult(
        s_vals=s_arr,
        cnrs_vals=cnrs_vals,
        scipy_vals=scipy_vals,
        exact_vals=exact_vals,
        abs_err=abs_err,
        rel_err=rel_err,
        max_abs_err=float(np.max(abs_err)),
        max_rel_err=float(np.max(rel_err)),
        cnrs_time_ms=cnrs_ms,
        scipy_time_ms=scipy_ms,
        label=label or f"y'={lam}*y, y0={y0}",
    )


# ---------------------------------------------------------------------------
# Benchmark utilities
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    """
    Timing and accuracy benchmark: CNRS-H vs scipy.integrate.solve_ivp.

    Attributes
    ----------
    label          : problem description
    n_points       : number of evaluation points
    n_repeat       : number of timing repetitions
    cnrs_ms        : mean CNRS-H time per solve (ms)
    scipy_ms       : mean scipy time per solve (ms)
    max_rel_err    : max relative error |CNRS-scipy| / |scipy|
    speedup_factor : scipy_ms / cnrs_ms  (>1 means CNRS is faster)
    """
    label:         str
    n_points:      int
    n_repeat:      int
    cnrs_ms:       float
    scipy_ms:      float
    max_rel_err:   float
    speedup_factor: float

    def summary(self) -> str:
        faster = "CNRS-H" if self.speedup_factor > 1 else "scipy"
        ratio = max(self.speedup_factor, 1/max(self.speedup_factor, 1e-9))
        return (
            f"Benchmark: {self.label}\n"
            f"  Points: {self.n_points}, Repeats: {self.n_repeat}\n"
            f"  CNRS-H: {self.cnrs_ms:.3f} ms/solve\n"
            f"  scipy:  {self.scipy_ms:.3f} ms/solve\n"
            f"  {faster} is {ratio:.1f}x faster\n"
            f"  Max rel error (CNRS vs scipy): {self.max_rel_err:.2e}"
        )


def benchmark_linear(
    lam: complex = complex(-0.3, 2.0),
    y0: complex = complex(1.0, 0.0),
    s_vals: Optional[Sequence[float]] = None,
    terms: int = 30,
    n_repeat: int = 20,
    label: str = "",
) -> BenchmarkResult:
    """
    Benchmark CNRS-H vs scipy for y' = lam*y.

    Runs n_repeat solves of each, reports mean timing and accuracy.

    Parameters
    ----------
    lam      : eigenvalue (default -0.3 + 2i, a damped oscillator)
    y0       : initial condition
    s_vals   : evaluation points (default: 100 points in [0, 1])
    terms    : CNRS-H EGF terms
    n_repeat : timing repetitions
    label    : description

    Returns
    -------
    BenchmarkResult
    """
    from scipy.integrate import solve_ivp

    if s_vals is None:
        s_vals = np.linspace(0.0, 1.0, 100)
    s_arr = np.asarray(s_vals, dtype=float)
    s_end = float(s_arr[-1])

    def scipy_rhs(t, z):
        yc = z[0] + 1j * z[1]
        dy = lam * yc
        return [dy.real, dy.imag]

    # Warm up
    cnrs_solve_linear(lam=lam, y0=y0, terms=terms)
    solve_ivp(scipy_rhs, [0.0, s_end], [y0.real, y0.imag],
              t_eval=s_arr, method='RK45', rtol=1e-10, atol=1e-12)

    # Time CNRS
    cnrs_times = []
    cnrs_vals = None
    for _ in range(n_repeat):
        t0 = time.perf_counter()
        sol = cnrs_solve_linear(lam=lam, y0=y0, terms=terms)
        v = ode_solution_to_numpy(sol, s_arr)
        cnrs_times.append((time.perf_counter() - t0) * 1000)
        cnrs_vals = v

    # Time scipy
    scipy_times = []
    scipy_vals = None
    for _ in range(n_repeat):
        t0 = time.perf_counter()
        ivp = solve_ivp(scipy_rhs, [0.0, s_end], [y0.real, y0.imag],
                        t_eval=s_arr, method='RK45', rtol=1e-10, atol=1e-12)
        v = ivp.y[0] + 1j * ivp.y[1]
        scipy_times.append((time.perf_counter() - t0) * 1000)
        scipy_vals = v

    cnrs_ms = float(np.mean(cnrs_times))
    scipy_ms = float(np.mean(scipy_times))
    max_rel_err = float(np.max(
        np.abs(cnrs_vals - scipy_vals) / (np.abs(scipy_vals) + 1e-300)))
    speedup = scipy_ms / max(cnrs_ms, 1e-9)

    return BenchmarkResult(
        label=label or f"y'=({lam})*y",
        n_points=len(s_arr),
        n_repeat=n_repeat,
        cnrs_ms=cnrs_ms,
        scipy_ms=scipy_ms,
        max_rel_err=max_rel_err,
        speedup_factor=speedup,
    )


def benchmark_second_order(
    gamma: float = 0.1,
    omega: float = 1.0,
    y0: complex = complex(1.0, 0.0),
    dy0: complex = complex(0.0, 0.0),
    s_vals: Optional[Sequence[float]] = None,
    terms: int = 30,
    n_repeat: int = 20,
    label: str = "",
) -> BenchmarkResult:
    """
    Benchmark CNRS-H vs scipy for y'' + 2*gamma*y' + omega²*y = 0.

    Parameters
    ----------
    gamma    : damping coefficient
    omega    : natural frequency
    y0, dy0  : initial conditions
    s_vals   : evaluation points (default: 100 points over one period)
    terms    : CNRS-H EGF terms
    n_repeat : timing repetitions

    Returns
    -------
    BenchmarkResult
    """
    from scipy.integrate import solve_ivp

    if s_vals is None:
        import math
        T = 2 * math.pi / omega
        s_vals = np.linspace(0.0, T, 100)
    s_arr = np.asarray(s_vals, dtype=float)
    s_end = float(s_arr[-1])
    omega_sq = omega ** 2

    def scipy_rhs(t, z):
        # z = [Re(y), Re(y'), Im(y), Im(y')]
        yr, ypr, yi, ypi = z
        yprr = -2*gamma*ypr - omega_sq*yr
        ypri = -2*gamma*ypi - omega_sq*yi
        return [ypr, yprr, ypi, ypri]

    z0 = [y0.real, dy0.real, y0.imag, dy0.imag]

    # Warm up
    cnrs_solve_second_order(gamma=gamma, omega=omega, y0=y0, dy0=dy0, terms=terms)
    solve_ivp(scipy_rhs, [0.0, s_end], z0, t_eval=s_arr,
              method='RK45', rtol=1e-10, atol=1e-12)

    cnrs_times = []
    cnrs_vals = None
    for _ in range(n_repeat):
        t0 = time.perf_counter()
        sol = cnrs_solve_second_order(gamma=gamma, omega=omega,
                                      y0=y0, dy0=dy0, terms=terms)
        v = ode_solution_to_numpy(sol, s_arr)
        cnrs_times.append((time.perf_counter() - t0) * 1000)
        cnrs_vals = v

    scipy_times = []
    scipy_vals = None
    for _ in range(n_repeat):
        t0 = time.perf_counter()
        ivp = solve_ivp(scipy_rhs, [0.0, s_end], z0, t_eval=s_arr,
                        method='RK45', rtol=1e-10, atol=1e-12)
        v = ivp.y[0] + 1j * ivp.y[2]
        scipy_times.append((time.perf_counter() - t0) * 1000)
        scipy_vals = v

    cnrs_ms = float(np.mean(cnrs_times))
    scipy_ms = float(np.mean(scipy_times))
    max_rel_err = float(np.max(
        np.abs(cnrs_vals - scipy_vals) / (np.abs(scipy_vals) + 1e-300)))
    speedup = scipy_ms / max(cnrs_ms, 1e-9)

    return BenchmarkResult(
        label=label or f"y''+{2*gamma}y'+{omega_sq}y=0",
        n_points=len(s_arr),
        n_repeat=n_repeat,
        cnrs_ms=cnrs_ms,
        scipy_ms=scipy_ms,
        max_rel_err=max_rel_err,
        speedup_factor=speedup,
    )


# ---------------------------------------------------------------------------
# Optional pandas export
# ---------------------------------------------------------------------------

def to_dataframe(sol: OdeSolution, s_vals: Sequence[float],
                 cols: Optional[List[str]] = None):
    """
    Export OdeSolution observable maps to a pandas DataFrame.

    Requires pandas. Returns None with a warning if pandas is not available.

    Parameters
    ----------
    sol    : OdeSolution to export
    s_vals : evaluation points
    cols   : column names to include (default: all)
              options: 's', 'real', 'imag', 'modulus', 'modulus_sq',
                       'phase', 'phase_rate'

    Returns
    -------
    pd.DataFrame or None
    """
    try:
        import pandas as pd
    except ImportError:
        warnings.warn("pandas not available; to_dataframe() returns None.")
        return None

    s_arr = np.asarray(s_vals, dtype=float)
    all_cols = {
        's':          s_arr,
        'real':       real_array(sol, s_arr),
        'imag':       imag_array(sol, s_arr),
        'modulus':    modulus_array(sol, s_arr),
        'modulus_sq': modulus_sq_array(sol, s_arr),
        'phase':      phase_array(sol, s_arr),
        'phase_rate': phase_rate_array(sol, s_arr),
    }
    if cols is None:
        cols = list(all_cols.keys())
    return pd.DataFrame({c: all_cols[c] for c in cols if c in all_cols})
