"""
cnrs_bio.py
===========
Biological scale dynamics toolkit for the CNRS scientific toolkit.

Implements the Gierer-Meinhardt (GM) activator-inhibitor model in the
CNRS-H multi-scale framework, as developed in Paper 18.  Provides:

  - Exact scale-dependent diffusion profiles D_a(s), D_h(s) as ScaleLaws
  - The CNRS-H diffusion-ratio field d(s) = D_h(s)/D_a(s)
  - Classical and scale-dependent Turing conditions
  - d_hi / d_lo discriminant calculation from GM parameters
  - s_exit detection: the scale at which Turing instability becomes extinct
  - k=0 (leading-order) GM coefficient evolution via CNRS-H
  - Effective diffusion ratio d_eff(s) with first-order scale-gradient correction
  - Three-workflow comparison (early / late / CNRS) for the Turing threshold

Architecture
------------
The CNRS-H multi-scale approach (Paper 18, §3) represents all
scale-dependent fields f(s) as EGF coefficient streams:

    f(s) = Σ f_k s^k/k!    →   [f_0, f_1, f_2, ...]

Differentiation d/ds is the exact digit-shift (drop f_0, shift left).
Multiplication of two fields uses Cauchy convolution of their coefficient
streams.  This allows the nonlinear GM system to be evolved at all scale
levels simultaneously, without linearising the scale dependence.

The key result (Paper 18, Theorem 1):
  The effective diffusion ratio seen at scale s_0 is:

      d_eff(s_0) = (D_h(s_0) + ε D_h'(s_0) h_1/h_0)
                 / (D_a(s_0) + ε D_a'(s_0) a_1/a_0)

  where a_1/a_0 and h_1/h_0 are the normalised scale gradients of the
  activator and inhibitor.  Turing instability is active iff d_eff > d_hi.

Parameters (Paper 18 demonstration, §4)
-----------------------------------------
  D_a(s) = 0.010 * exp(-s/3)       [activator diffusion, slow decay]
  D_h(s) = 1.000 * exp(-2s)        [inhibitor diffusion, fast decay]
  d(s)   = D_h/D_a = 100 * exp(-5s/3)

  Nondimensional GM: c = 0.5, gamma = 50
  Discriminant roots: d_lo = 0.2154, d_hi = 41.785
  s_exit ≈ 0.52 nats  (ℓ ≈ 17 μm, inter-cellular scale)

Public API
----------
Diffusion profiles:
    da_profile(terms=32)   →  ScaleLaw for D_a(s) = 0.010 * exp(-s/3)
    dh_profile(terms=32)   →  ScaleLaw for D_h(s) = 1.000 * exp(-2s)
    d_ratio(terms=32)      →  ScaleLaw for d(s) = D_h(s)/D_a(s)

Turing analysis:
    GmParams(c, gamma)     dataclass of GM nondimensional parameters
    gm_jacobian(p)         →  2×2 Jacobian at homogeneous steady state
    turing_discriminant(p) →  (d_lo, d_hi) discriminant roots
    turing_active(d, p)    →  bool  (d > d_hi)
    s_exit(p, terms, n_points)  →  float, the Turing extinction scale

Scale-gradient correction:
    d_eff(s, a1_over_a0, h1_over_h0, p, terms)
        →  float, effective diffusion ratio with scale-gradient correction

Multi-scale GM coefficient evolution (k=0):
    gm_k0_rhs(a0, h0, p)   →  (da0_dt, dh0_dt) right-hand sides at k=0
    gm_steady_state(p)     →  (a_star, h_star) homogeneous steady state

Three-workflow comparison:
    compare_turing_workflows(p, s_vals)  →  TuringWorkflowResult

Result objects:
    TuringProfile    .s_vals, .d_vals, .d_eff_vals, .active, .s_exit
    TuringWorkflowResult  .early, .late, .cnrs, .s_exit_early, .s_exit_cnrs

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Paper:   Palmer (2026), Paper 18 — Multi-Scale Turing Pattern Formation
Session: 43, 2026-06-06
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

import numpy as np

from .cnrs_h import CnrsH
from .cnrs_scale import ScaleLaw, turing_threshold


# ---------------------------------------------------------------------------
# Default Paper 18 demonstration parameters
# ---------------------------------------------------------------------------

#: Activator diffusion amplitude at s=0
DA0_DEFAULT: float = 0.010
#: Activator diffusion decay rate (1/L_a = 1/3 nat^-1)
LA_DEFAULT: float = -1.0 / 3.0

#: Inhibitor diffusion amplitude at s=0
DH0_DEFAULT: float = 1.000
#: Inhibitor diffusion decay rate (1/L_h = 2 nat^-1)
LH_DEFAULT: float = -2.0

#: Nondimensional GM parameters (Paper 18, §4)
C_DEFAULT: float = 0.5
GAMMA_DEFAULT: float = 50.0

#: Turing discriminant roots for default parameters
D_LO_DEFAULT: float = 0.2154
D_HI_DEFAULT: float = 41.785

#: Turing extinction scale (nats) for default parameters
S_EXIT_DEFAULT: float = 0.52


# ---------------------------------------------------------------------------
# GM parameter dataclass
# ---------------------------------------------------------------------------

@dataclass
class GmParams:
    """
    Nondimensional Gierer-Meinhardt parameters.

    The nondimensional GM system (Murray 2003, Chapter 2):
        du/dt = gamma*(u^2/v - u + c) + nabla^2 u
        dv/dt = gamma*(u^2 - v)       + d * nabla^2 v

    where u = activator, v = inhibitor, gamma > 0, c > 0, d > 1.

    The homogeneous steady state is:
        u* = 1 + c,  v* = (1 + c)^2

    Turing instability requires d > d_hi, where d_hi is the larger
    discriminant root of the Turing polynomial.

    Attributes
    ----------
    c     : basal activator production  (default 0.5)
    gamma : overall reaction rate       (default 50.0)
    da0   : activator diffusion at s=0  (default 0.010)
    lam_a : activator diffusion exponent (default -1/3)
    dh0   : inhibitor diffusion at s=0  (default 1.000)
    lam_h : inhibitor diffusion exponent (default -2.0)
    """
    c:     float = C_DEFAULT
    gamma: float = GAMMA_DEFAULT
    da0:   float = DA0_DEFAULT
    lam_a: float = LA_DEFAULT
    dh0:   float = DH0_DEFAULT
    lam_h: float = LH_DEFAULT

    def d_ratio_at_zero(self) -> float:
        """d(0) = D_h(0)/D_a(0)."""
        return self.dh0 / self.da0

    def d_exponent(self) -> float:
        """Exponent in d(s) = d(0)*exp((lam_h - lam_a)*s)."""
        return self.lam_h - self.lam_a


# ---------------------------------------------------------------------------
# Diffusion profiles
# ---------------------------------------------------------------------------

def da_profile(p: Optional[GmParams] = None, terms: int = 32) -> ScaleLaw:
    """
    ScaleLaw for D_a(s) = da0 * exp(lam_a * s).

    Default: 0.010 * exp(-s/3)  (Paper 18 demonstration).
    """
    if p is None:
        p = GmParams()
    return ScaleLaw.exponential(lam=complex(p.lam_a, 0.0),
                                scale=complex(p.da0, 0.0),
                                terms=terms,
                                name=f"D_a(s)={p.da0}*exp({p.lam_a:.4f}s)")


def dh_profile(p: Optional[GmParams] = None, terms: int = 32) -> ScaleLaw:
    """
    ScaleLaw for D_h(s) = dh0 * exp(lam_h * s).

    Default: 1.000 * exp(-2s)  (Paper 18 demonstration).
    """
    if p is None:
        p = GmParams()
    return ScaleLaw.exponential(lam=complex(p.lam_h, 0.0),
                                scale=complex(p.dh0, 0.0),
                                terms=terms,
                                name=f"D_h(s)={p.dh0}*exp({p.lam_h:.4f}s)")


def d_ratio(p: Optional[GmParams] = None, terms: int = 32) -> ScaleLaw:
    """
    ScaleLaw for d(s) = D_h(s)/D_a(s) = (dh0/da0)*exp((lam_h - lam_a)*s).

    Default: 100.0 * exp(-5s/3)  (Paper 18 demonstration).
    """
    if p is None:
        p = GmParams()
    d0 = p.dh0 / p.da0
    lam_d = p.lam_h - p.lam_a
    return ScaleLaw.exponential(lam=complex(lam_d, 0.0),
                                scale=complex(d0, 0.0),
                                terms=terms,
                                name=f"d(s)={d0:.3f}*exp({lam_d:.4f}s)")


# ---------------------------------------------------------------------------
# Turing analysis
# ---------------------------------------------------------------------------

def gm_steady_state(p: Optional[GmParams] = None) -> Tuple[float, float]:
    """
    Homogeneous steady state (u*, v*) of the nondimensional GM system.

        u* = 1 + c
        v* = (1 + c)^2

    Returns (u_star, v_star).
    """
    if p is None:
        p = GmParams()
    u_star = 1.0 + p.c
    v_star = u_star ** 2
    return u_star, v_star


def gm_jacobian(p: Optional[GmParams] = None) -> np.ndarray:
    """
    2×2 Jacobian of the GM kinetics at the homogeneous steady state,
    scaled by gamma.

    J = gamma * [[2u*/v* - 1,  -(u*/v*)^2],
                 [2u*,          -1        ]]

    For the default nondimensionalisation with u* = 1+c, v* = (1+c)^2:
        J = gamma * [[1/(1+c) - 1,  -1/(1+c)^2],
                     [2(1+c),        -1         ]]

    Returns a 2×2 numpy array.
    """
    if p is None:
        p = GmParams()
    u, v = gm_steady_state(p)
    g = p.gamma
    j00 = g * (2 * u / v - 1)
    j01 = g * (-(u / v) ** 2)
    j10 = g * 2 * u
    j11 = g * (-1.0)
    return np.array([[j00, j01], [j10, j11]])


def turing_discriminant(p: Optional[GmParams] = None) -> Tuple[float, float]:
    """
    Discriminant roots (d_lo, d_hi) of the Turing instability polynomial.

    The Turing condition requires d = D_h/D_a > d_hi, where d_hi is the
    larger root of:

        det(J)  -  (j00 + d*j11)^2 / (4d)  =  0

    equivalently the quadratic in d:

        j00^2 * d^2  +  (2*j00*j11 - 4*det(J)) * d  +  j11^2  =  0

    Returns (d_lo, d_hi) with d_lo < d_hi.

    For the default parameters (c=0.5, gamma=50):
        d_lo ≈ 0.2154,  d_hi ≈ 41.785  (Paper 18, Table 1).
    """
    if p is None:
        p = GmParams()
    J = gm_jacobian(p)
    j00, j01, j10, j11 = J[0, 0], J[0, 1], J[1, 0], J[1, 1]
    det_J = j00 * j11 - j01 * j10

    # Quadratic: j11^2 * d^2 - (2*j11*j00 - 4*det_J)*d + j00^2 = 0
    A = j00 ** 2
    B = 2 * j00 * j11 - 4 * det_J
    C = j11 ** 2

    discriminant = B ** 2 - 4 * A * C
    if discriminant < 0:
        raise ValueError(
            "turing_discriminant: no real roots — parameters do not support "
            "Turing instability for any d.")

    sqrt_disc = math.sqrt(discriminant)
    d1 = (-B - sqrt_disc) / (2 * A)
    d2 = (-B + sqrt_disc) / (2 * A)
    d_lo, d_hi = (min(d1, d2), max(d1, d2))
    return d_lo, d_hi


def turing_active(d: float, p: Optional[GmParams] = None) -> bool:
    """
    True iff d > d_hi (Turing instability active at this scale).

    Also checks tr(J) < 0 and det(J) > 0 (stability of kinetics).
    """
    if p is None:
        p = GmParams()
    J = gm_jacobian(p)
    if np.trace(J) >= 0 or np.linalg.det(J) <= 0:
        raise ValueError(
            "turing_active: kinetics are not stable (tr(J)>=0 or det(J)<=0). "
            "Turing analysis requires stable homogeneous steady state.")
    _, d_hi = turing_discriminant(p)
    return d > d_hi


def find_s_exit(p: Optional[GmParams] = None, terms: int = 32,
                n_points: int = 500,
                s_lo: float = 0.0, s_hi: float = 5.0) -> Optional[float]:
    """
    Find s_exit: the scale at which Turing instability becomes extinct.

    Uses the d_ratio ScaleLaw and turing_threshold to locate the crossing
    d(s) = d_hi.  The log-derivative of d(s) is lam_d (constant), so we
    directly search for where d(s) crosses d_hi.

    Strategy: evaluate d at n_points uniformly in [s_lo, s_hi] and
    bisect the first crossing of d(s) = d_hi.

    Returns s_exit (float) or None if d(s) > d_hi throughout [s_lo, s_hi]
    (always active) or d(s) < d_hi throughout (never active).
    """
    if p is None:
        p = GmParams()

    _, d_hi = turing_discriminant(p)
    dr = d_ratio(p, terms=terms)

    s_vals = np.linspace(s_lo, s_hi, n_points)
    d_vals = np.array([dr.evaluate(complex(s)).real for s in s_vals])

    # Find crossing of d(s) = d_hi
    diff = d_vals - d_hi
    sign_changes = np.where(np.diff(np.sign(diff)))[0]

    if len(sign_changes) == 0:
        return None

    idx = int(sign_changes[0])
    a, b = float(s_vals[idx]), float(s_vals[idx + 1])

    # Bisect
    for _ in range(52):
        mid = 0.5 * (a + b)
        fm = dr.evaluate(complex(mid)).real - d_hi
        if abs(fm) < 1e-12:
            break
        fa = dr.evaluate(complex(a)).real - d_hi
        if fa * fm < 0:
            b = mid
        else:
            a = mid

    return 0.5 * (a + b)


# ---------------------------------------------------------------------------
# Scale-gradient correction (Paper 18, Theorem 1)
# ---------------------------------------------------------------------------

def d_eff(s: float,
          a1_over_a0: float,
          h1_over_h0: float,
          p: Optional[GmParams] = None,
          terms: int = 32) -> float:
    """
    Effective diffusion ratio at scale s, including first-order
    scale-gradient correction (Paper 18, Theorem 1):

        d_eff(s) = (D_h(s) + ε * D_h'(s) * h1/h0)
                 / (D_a(s) + ε * D_a'(s) * a1/a0)

    where ε = 1 (the scale coordinate), a1/a0 is the normalised
    scale gradient of the activator, h1/h0 for the inhibitor.

    With D_a(s) = da0*exp(lam_a*s) and D_h(s) = dh0*exp(lam_h*s):
        D_a'(s) = lam_a * D_a(s)
        D_h'(s) = lam_h * D_h(s)

    So:
        d_eff = D_h(s) * (1 + lam_h * h1/h0)
              / (D_a(s) * (1 + lam_a * a1/a0))

    Parameters
    ----------
    s           : scale coordinate (nats)
    a1_over_a0  : normalised activator scale gradient a_1/a_0
    h1_over_h0  : normalised inhibitor scale gradient h_1/h_0
    p           : GmParams (default: Paper 18 parameters)
    terms       : CNRS-H terms for diffusion profiles

    Returns
    -------
    d_eff : float, effective diffusion ratio at scale s
    """
    if p is None:
        p = GmParams()

    Da = da_profile(p, terms).evaluate(complex(s)).real
    Dh = dh_profile(p, terms).evaluate(complex(s)).real

    numerator   = Dh * (1.0 + p.lam_h * h1_over_h0)
    denominator = Da * (1.0 + p.lam_a * a1_over_a0)

    if abs(denominator) < 1e-300:
        return float("inf")
    return numerator / denominator


# ---------------------------------------------------------------------------
# k=0 GM coefficient evolution (leading order)
# ---------------------------------------------------------------------------

def gm_k0_rhs(a0: float, h0: float,
              p: Optional[GmParams] = None) -> Tuple[float, float]:
    """
    Right-hand side of the k=0 (leading-order, s=0) GM equations:

        da0/dt = gamma * (a0^2/h0 - a0 + c)
        dh0/dt = gamma * (a0^2 - h0)

    (Spatial diffusion drops out at k=0 for spatially homogeneous states.)

    Returns (da0_dt, dh0_dt).
    """
    if p is None:
        p = GmParams()
    da0_dt = p.gamma * (a0 ** 2 / h0 - a0 + p.c)
    dh0_dt = p.gamma * (a0 ** 2 - h0)
    return da0_dt, dh0_dt


def gm_steady_state_check(p: Optional[GmParams] = None,
                           tol: float = 1e-10) -> bool:
    """
    Verify that gm_k0_rhs(u*, v*) ≈ (0, 0) at the homogeneous steady state.
    """
    if p is None:
        p = GmParams()
    u, v = gm_steady_state(p)
    rhs_a, rhs_h = gm_k0_rhs(u, v, p)
    return abs(rhs_a) < tol and abs(rhs_h) < tol


# ---------------------------------------------------------------------------
# Turing profile across scales
# ---------------------------------------------------------------------------

@dataclass
class TuringProfile:
    """
    Scale-resolved Turing instability profile.

    Attributes
    ----------
    s_vals   : array of scale coordinates (nats)
    d_vals   : d(s) = D_h(s)/D_a(s) at each s
    d_hi     : Turing threshold
    d_lo     : lower discriminant root
    active   : bool array, True where d(s) > d_hi
    s_exit   : float or None, scale at which instability becomes extinct
    """
    s_vals: np.ndarray
    d_vals: np.ndarray
    d_hi:   float
    d_lo:   float
    active: np.ndarray
    s_exit: Optional[float]


def turing_profile(p: Optional[GmParams] = None,
                   s_vals: Optional[Sequence[float]] = None,
                   terms: int = 32) -> TuringProfile:
    """
    Compute the scale-resolved Turing instability profile.

    Evaluates d(s), d_hi, and active status at each s in s_vals.

    Parameters
    ----------
    p      : GmParams (default: Paper 18)
    s_vals : scale coordinates to evaluate (default: 0 to 4 nats, 200 points)
    terms  : CNRS-H terms for diffusion profiles

    Returns
    -------
    TuringProfile
    """
    if p is None:
        p = GmParams()
    if s_vals is None:
        s_vals = np.linspace(0.0, 4.0, 200)
    s_arr = np.asarray(s_vals, dtype=float)

    dr = d_ratio(p, terms=terms)
    d_arr = np.array([dr.evaluate(complex(s)).real for s in s_arr])

    d_lo_val, d_hi_val = turing_discriminant(p)
    active = d_arr > d_hi_val
    s_ex = find_s_exit(p, terms=terms)

    return TuringProfile(s_vals=s_arr, d_vals=d_arr,
                         d_hi=d_hi_val, d_lo=d_lo_val,
                         active=active, s_exit=s_ex)


# ---------------------------------------------------------------------------
# Three-workflow comparison
# ---------------------------------------------------------------------------

@dataclass
class TuringWorkflowResult:
    """
    Three-workflow comparison for the Turing threshold.

    Workflow A (early reduction): use d(s) = D_h(s)/D_a(s) directly,
        ignore scale-gradient correction. Detects s_exit from d(s) = d_hi.

    Workflow B (standard complex late reduction): same as A for the
        real-valued diffusion ratio — no complex structure at this level.

    Workflow C (CNRS scale-gradient): include first-order correction
        d_eff(s) = d(s)*(1 + lam_h*h1/h0)/(1 + lam_a*a1/a0).
        This can shift s_exit depending on the activator scale gradient.

    Attributes
    ----------
    s_vals          : scale array
    d_no_correction : d(s) without correction (workflows A/B)
    d_with_correction: d_eff(s) with scale-gradient correction (workflow C)
    s_exit_no_correction  : s_exit from d(s) = d_hi
    s_exit_with_correction: s_exit from d_eff(s) = d_hi
    d_hi            : Turing threshold
    a1_over_a0      : activator scale gradient used
    h1_over_h0      : inhibitor scale gradient used
    """
    s_vals: np.ndarray
    d_no_correction: np.ndarray
    d_with_correction: np.ndarray
    s_exit_no_correction: Optional[float]
    s_exit_with_correction: Optional[float]
    d_hi: float
    a1_over_a0: float
    h1_over_h0: float


def compare_turing_workflows(
    p: Optional[GmParams] = None,
    s_vals: Optional[Sequence[float]] = None,
    a1_over_a0: float = 0.0,
    h1_over_h0: float = 0.0,
    terms: int = 32,
) -> TuringWorkflowResult:
    """
    Compare Turing threshold detection across three workflows.

    Workflow A/B: d(s) = D_h(s)/D_a(s), no scale-gradient correction.
    Workflow C:   d_eff(s) with first-order scale-gradient correction.

    When a1_over_a0 = h1_over_h0 = 0, all workflows agree.
    Non-zero scale gradients (a1_over_a0 ≠ 0) shift d_eff and thus s_exit.

    Parameters
    ----------
    p           : GmParams (default: Paper 18)
    s_vals      : scale grid (default: 0 to 3 nats, 300 points)
    a1_over_a0  : normalised activator scale gradient
    h1_over_h0  : normalised inhibitor scale gradient
    terms       : CNRS-H terms

    Returns
    -------
    TuringWorkflowResult
    """
    if p is None:
        p = GmParams()
    if s_vals is None:
        s_vals = np.linspace(0.0, 3.0, 300)
    s_arr = np.asarray(s_vals, dtype=float)

    _, d_hi_val = turing_discriminant(p)

    # Workflow A/B: plain diffusion ratio
    dr = d_ratio(p, terms=terms)
    d_plain = np.array([dr.evaluate(complex(s)).real for s in s_arr])

    # Workflow C: with scale-gradient correction
    d_corr = np.array([d_eff(float(s), a1_over_a0, h1_over_h0, p, terms)
                       for s in s_arr])

    # s_exit without correction (bisect d_plain = d_hi)
    s_exit_plain = find_s_exit(p, terms=terms)

    # s_exit with correction (bisect d_corr = d_hi)
    diff_corr = d_corr - d_hi_val
    sign_changes = np.where(np.diff(np.sign(diff_corr)))[0]
    if len(sign_changes) == 0:
        s_exit_corr = None
    else:
        idx = int(sign_changes[0])
        a_bi, b_bi = float(s_arr[idx]), float(s_arr[idx + 1])
        for _ in range(52):
            mid = 0.5 * (a_bi + b_bi)
            fm = d_eff(mid, a1_over_a0, h1_over_h0, p, terms) - d_hi_val
            if abs(fm) < 1e-12:
                break
            fa = d_eff(a_bi, a1_over_a0, h1_over_h0, p, terms) - d_hi_val
            if fa * fm < 0:
                b_bi = mid
            else:
                a_bi = mid
        s_exit_corr = 0.5 * (a_bi + b_bi)

    return TuringWorkflowResult(
        s_vals=s_arr,
        d_no_correction=d_plain,
        d_with_correction=d_corr,
        s_exit_no_correction=s_exit_plain,
        s_exit_with_correction=s_exit_corr,
        d_hi=d_hi_val,
        a1_over_a0=a1_over_a0,
        h1_over_h0=h1_over_h0,
    )
