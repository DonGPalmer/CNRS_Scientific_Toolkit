"""
cnrs_multiscale.py
==================
Component 7 of the CNRS Scientific Toolkit.

Multi-scale Scale Space computational layer: runs CNRS-H EGF streams across the
s-ladder (scale as a coordinate), passes outputs as boundary conditions at the
next scale level, and provides scale-aware observable maps with exact
digit-shift s-derivatives.

Background
----------
Scale Space (SS) treats s as a fourth spatial/scale coordinate,
with time handled separately in later 5D extensions.  A physical field Ψ_s = f(s)·exp(iθ(s)) is
represented as a CNRS-H EGF stream; its behaviour across scales is governed
by the same coefficient-recurrence calculus that, in benchmarked
linear ODE examples, makes CNRS-H faster and more precise than scipy RK45
(see cnrs_ode.py benchmark results: 4–18× faster, error ~ 3.5×10⁻¹⁶
vs. 2.4×10⁻¹¹).

Architecture
------------
The central object is ScaleLadder: a sequence of OdeSolution objects, one per
rung of the scale ladder.  Each rung covers a scale interval [s_lo, s_hi]; the
boundary value at s_hi of rung k becomes the initial condition at s_lo of rung
k+1.  This implements the SS "cascade of scales" as a computable object.

Items (a) and (b) of the Component 7 scope are implemented here:

  (a) ScaleLadder: scale-indexed solution container
      - Constructs a sequence of OdeSolution rungs
      - Propagates boundary values between rungs exactly (coefficient arithmetic)
      - Evaluates at any s by locating the correct rung
      - Supports heterogeneous eigenvalues per rung (scale-dependent physics)

  (b) Scale-aware observable maps
      - All five OdeSolution maps extended to work across the full ladder
      - ScaleDerivative: d/ds of any observable computed via digit-shift
        (exact, not numerical) within each rung
      - ScaleGradientCorrection: the scale-gradient correction d_eff from
        Paper 18 Theorem 1, now as a ladder-aware callable

Items (c)–(e) (junction conditions, 5D field equations, Ψ₀ determination)
are scoped but not yet implemented; they depend on Thread 5 (GR specialist).
Placeholder classes are provided so callers can be written against the
eventual API.

Public API
----------
Construction:
    ScaleLadder.uniform(lam, y0, s_total, n_rungs, terms=25)
        Uniform rungs, constant eigenvalue.  The simplest case.

    ScaleLadder.from_profile(lam_profile, y0, s_edges, terms=25)
        Heterogeneous rungs: lam_profile(s) supplies the eigenvalue at each
        rung midpoint.  Models scale-dependent physics.

    ScaleLadder.from_solutions(solutions, s_edges)
        From a pre-built list of OdeSolution objects and their s boundaries.

Evaluation:
    ladder.evaluate(s)          complex Ψ(s) at any s in [0, s_total]
    ladder.rung_at(s)           (rung_index, local_s) for a global s
    ladder.n_rungs              number of rungs
    ladder.s_edges              boundary points [s0, s1, ..., sN]
    ladder.boundary_values      list of complex Ψ at each rung boundary

Scale-aware observable maps (all accept global s):
    ladder.modulus_sq(s)        |Ψ(s)|²
    ladder.real_part(s)         Re Ψ(s)
    ladder.imag_part(s)         Im Ψ(s)
    ladder.phase(s)             arg Ψ(s) in (−π, π]
    ladder.phase_rate(s)        d(arg Ψ)/ds = Im(Ψ'/Ψ) — instantaneous freq
    ladder.phase_current(s)     |Ψ|² · d(arg Ψ)/ds — configurational current
    ladder.scale_derivative(s)  dΨ/ds (exact digit-shift within rung)

Scale-gradient correction (Paper 18, Theorem 1):
    scale_gradient_correction(ladder, s, delta_s)
        d_eff at scale s with gradient step delta_s.
        Returns ScaleGradientResult with .d_ratio, .correction, .d_eff.

Profile utilities:
    ladder_profile(ladder, s_vals, observable='modulus_sq')
        Evaluate any observable across a list of s values.
        Returns (s_array, values_array) for plotting or fitting.

    ladder_to_scalelaws(ladder)
        Convert each rung to a ScaleLaw for use with cnrs_scale machinery.

Result objects:
    LadderEvalResult     .s, .rung, .local_s, .value, .observables
    ScaleGradientResult  .s, .delta_s, .d_ratio, .correction, .d_eff

Placeholder stubs (Thread 5 / items c–e):
    JunctionCondition   — C¹ amplitude matching at a scale boundary
    FieldEquationCheck  — 5D SS field equation residual monitor
    PsiZeroDeterminer   — Ψ₀ phase-scale and hidden-sector amplitude

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 44, 2026-06-07
"""

from __future__ import annotations

import cmath
import math
import warnings
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple, Union

import numpy as np

from .cnrs_h import CnrsH
from .cnrs_ode import OdeSolution, cnrs_solve_linear, cnrs_solve_driven, _s_max
from .cnrs_scale import ScaleLaw

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

_Scalar = Union[int, float, complex]
_LamProfile = Callable[[float], complex]   # lam as a function of s

DEFAULT_TERMS: int = 25


# ---------------------------------------------------------------------------
# Result objects
# ---------------------------------------------------------------------------

@dataclass
class LadderEvalResult:
    """Full evaluation record at a single global s."""
    s: float
    rung: int
    local_s: float
    value: complex
    modulus_sq: float
    phase: float
    phase_rate: float
    phase_current: float

    def __repr__(self) -> str:
        return (
            f"LadderEvalResult(s={self.s:.4f}, rung={self.rung}, "
            f"|Ψ|²={self.modulus_sq:.6f}, phase={self.phase:.6f})"
        )


@dataclass
class ScaleGradientResult:
    """
    Scale-gradient correction d_eff at a point on the ladder.

    Implements Paper 18, Theorem 1: d_eff(s) = d · (1 + correction),
    where the correction encodes the scale-gradient of the diffusion ratio.
    """
    s: float
    delta_s: float
    d_ratio: float       # |Ψ(s + δs)| / |Ψ(s)|  — amplitude ratio
    correction: float    # fractional gradient correction
    d_eff: float         # effective diffusion ratio at s

    def __repr__(self) -> str:
        return (
            f"ScaleGradientResult(s={self.s:.4f}, d_ratio={self.d_ratio:.6f}, "
            f"correction={self.correction:+.6f}, d_eff={self.d_eff:.6f})"
        )


# ---------------------------------------------------------------------------
# ScaleLadder
# ---------------------------------------------------------------------------

class ScaleLadder:
    """
    A sequence of CNRS-H OdeSolution rungs spanning a total scale range.

    Each rung covers [s_edges[k], s_edges[k+1]].  The boundary value of
    rung k at its upper edge is propagated as the initial condition of rung
    k+1, implementing the SS cascade of scales as a computable object.

    The local coordinate within rung k is:
        s_local = s_global − s_edges[k]

    OdeSolution.evaluate() always takes a local s; ScaleLadder.evaluate()
    handles the global→local conversion automatically.
    """

    def __init__(
        self,
        solutions: List[OdeSolution],
        s_edges: List[float],
        label: str = "ScaleLadder",
    ):
        if len(solutions) != len(s_edges) - 1:
            raise ValueError(
                f"Need len(s_edges) = len(solutions) + 1; "
                f"got {len(s_edges)} edges and {len(solutions)} solutions."
            )
        self._solutions = solutions
        self._s_edges = [float(e) for e in s_edges]
        self._label = label

    # ── Construction ─────────────────────────────────────────────────────────

    @classmethod
    def uniform(
        cls,
        lam: _Scalar,
        y0: _Scalar = 1.0,
        s_total: float = 1.0,
        n_rungs: int = 4,
        terms: int = DEFAULT_TERMS,
        label: str = "uniform_ladder",
    ) -> "ScaleLadder":
        """
        Uniform ScaleLadder: constant eigenvalue, equal-width rungs.

        Parameters
        ----------
        lam     : complex  Eigenvalue (same at every rung).
        y0      : complex  Initial condition at s=0.
        s_total : float    Total scale range (nats).
        n_rungs : int      Number of rungs.
        terms   : int      EGF terms per rung.
        label   : str      Human-readable name.

        Returns
        -------
        ScaleLadder
        """
        lam = complex(lam)
        y0 = complex(y0)
        ds = s_total / n_rungs
        s_edges = [k * ds for k in range(n_rungs + 1)]

        solutions = []
        y_current = y0
        for _ in range(n_rungs):
            sol = cnrs_solve_linear(lam, y_current, terms=terms)
            solutions.append(sol)
            # Propagate boundary value: evaluate at end of rung (local s = ds)
            y_current = sol.evaluate(ds)

        return cls(solutions, s_edges, label=label)

    @classmethod
    def from_profile(
        cls,
        lam_profile: _LamProfile,
        y0: _Scalar = 1.0,
        s_edges: Optional[Sequence[float]] = None,
        s_total: float = 1.0,
        n_rungs: int = 4,
        terms: int = DEFAULT_TERMS,
        label: str = "profile_ladder",
    ) -> "ScaleLadder":
        """
        ScaleLadder with scale-dependent eigenvalue.

        lam_profile(s) is called at the midpoint of each rung to determine
        the local eigenvalue.  This models physics where the effective
        coupling or decay rate changes with scale.

        Parameters
        ----------
        lam_profile : callable  s → complex eigenvalue.
        y0          : complex   Initial condition at s=0.
        s_edges     : list      Explicit rung boundaries (overrides s_total/n_rungs).
        s_total     : float     Total scale range if s_edges not supplied.
        n_rungs     : int       Number of rungs if s_edges not supplied.
        terms       : int       EGF terms per rung.
        label       : str       Human-readable name.

        Returns
        -------
        ScaleLadder
        """
        y0 = complex(y0)
        if s_edges is None:
            ds = s_total / n_rungs
            s_edges = [k * ds for k in range(n_rungs + 1)]
        else:
            s_edges = [float(e) for e in s_edges]

        solutions = []
        y_current = y0
        for k in range(len(s_edges) - 1):
            s_lo = s_edges[k]
            s_hi = s_edges[k + 1]
            ds = s_hi - s_lo
            s_mid = 0.5 * (s_lo + s_hi)
            lam = complex(lam_profile(s_mid))
            sol = cnrs_solve_linear(lam, y_current, terms=terms)
            solutions.append(sol)
            y_current = sol.evaluate(ds)

        return cls(solutions, s_edges, label=label)

    @classmethod
    def from_solutions(
        cls,
        solutions: List[OdeSolution],
        s_edges: Sequence[float],
        label: str = "custom_ladder",
    ) -> "ScaleLadder":
        """
        Build a ScaleLadder from pre-constructed OdeSolution objects.

        Useful when different rung types (linear, driven, second-order) are
        needed at different scales.

        Parameters
        ----------
        solutions : list of OdeSolution  One per rung.
        s_edges   : sequence of float    n_rungs + 1 boundary points.
        label     : str

        Returns
        -------
        ScaleLadder
        """
        return cls(list(solutions), list(s_edges), label=label)

    # ── Rung lookup ──────────────────────────────────────────────────────────

    def rung_at(self, s: float) -> Tuple[int, float]:
        """
        Return (rung_index, local_s) for a global coordinate s.

        For s at the upper edge of the last rung, returns the last rung.
        For s outside [s_edges[0], s_edges[-1]], raises ValueError.
        """
        s = float(s)
        s_lo = self._s_edges[0]
        s_hi = self._s_edges[-1]

        if s < s_lo - 1e-12:
            raise ValueError(
                f"s={s:.4f} is below the ladder start s_lo={s_lo:.4f}."
            )
        if s > s_hi + 1e-12:
            raise ValueError(
                f"s={s:.4f} is above the ladder end s_hi={s_hi:.4f}."
            )

        # Clamp to edges
        s = max(s_lo, min(s, s_hi))

        # Locate rung: rung k covers [s_edges[k], s_edges[k+1])
        for k in range(len(self._solutions) - 1):
            if s < self._s_edges[k + 1]:
                return k, s - self._s_edges[k]
        # Last rung (or s == s_hi exactly)
        k = len(self._solutions) - 1
        return k, s - self._s_edges[k]

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def n_rungs(self) -> int:
        """Number of rungs."""
        return len(self._solutions)

    @property
    def s_edges(self) -> List[float]:
        """Rung boundary points [s0, s1, ..., sN]."""
        return list(self._s_edges)

    @property
    def s_total(self) -> float:
        """Total scale range covered."""
        return self._s_edges[-1] - self._s_edges[0]

    @property
    def solutions(self) -> List[OdeSolution]:
        """The OdeSolution for each rung (read-only list)."""
        return list(self._solutions)

    @property
    def boundary_values(self) -> List[complex]:
        """
        Complex Ψ at each rung boundary [s_edges[0], ..., s_edges[-1]].

        The value at s_edges[0] is the initial condition;
        each subsequent value is the propagated boundary.
        """
        bvs = [self._solutions[0].evaluate(0.0)]
        for k, sol in enumerate(self._solutions):
            ds = self._s_edges[k + 1] - self._s_edges[k]
            bvs.append(sol.evaluate(ds))
        return bvs

    # ── Core evaluation ──────────────────────────────────────────────────────

    def evaluate(self, s: float) -> complex:
        """
        Complex Ψ(s) at global coordinate s.

        Locates the correct rung, converts to local s, and evaluates the
        rung's OdeSolution.
        """
        k, s_local = self.rung_at(s)
        return self._solutions[k].evaluate(s_local)

    def full_eval(self, s: float) -> LadderEvalResult:
        """
        Full evaluation record at global s: value + all observables.

        Returns LadderEvalResult with rung index, local s, and all five
        observable maps.
        """
        k, s_local = self.rung_at(s)
        sol = self._solutions[k]
        v = sol.evaluate(s_local)
        ms = abs(v) ** 2
        ph = cmath.phase(v)
        pr = sol.phase_rate(s_local)
        pc = ms * pr
        return LadderEvalResult(
            s=float(s),
            rung=k,
            local_s=s_local,
            value=v,
            modulus_sq=ms,
            phase=ph,
            phase_rate=pr,
            phase_current=pc,
        )

    # ── Scale-aware observable maps ──────────────────────────────────────────

    def modulus_sq(self, s: float) -> float:
        """|Ψ(s)|² at global coordinate s."""
        return abs(self.evaluate(s)) ** 2

    def real_part(self, s: float) -> float:
        """Re Ψ(s) at global coordinate s."""
        return self.evaluate(s).real

    def imag_part(self, s: float) -> float:
        """Im Ψ(s) at global coordinate s."""
        return self.evaluate(s).imag

    def phase(self, s: float) -> float:
        """arg Ψ(s) in (−π, π] at global coordinate s."""
        return cmath.phase(self.evaluate(s))

    def phase_rate(self, s: float) -> float:
        """
        d(arg Ψ)/ds = Im(Ψ'/Ψ) at global coordinate s.

        Computed via exact digit-shift derivative within the rung — no
        finite-difference approximation.
        """
        k, s_local = self.rung_at(s)
        return self._solutions[k].phase_rate(s_local)

    def phase_current(self, s: float) -> float:
        """
        Configurational current J(s) = |Ψ|² · d(arg Ψ)/ds.

        In the SS context: J_A = f² ∇_A θ where Ψ_s = f·exp(iθ).
        """
        return self.modulus_sq(s) * self.phase_rate(s)

    def scale_derivative(self, s: float) -> complex:
        """
        dΨ/ds at global coordinate s via exact digit-shift differentiation.

        Within each rung, d/ds is the CNRS-H coefficient shift (exact).
        At rung boundaries the one-sided derivative from the lower rung
        is returned.
        """
        k, s_local = self.rung_at(s)
        return self._solutions[k].derivative().evaluate(s_local)

    # ── Summary ──────────────────────────────────────────────────────────────

    def summary(self, n_points: int = 5) -> str:
        """
        Human-readable table of all observables at uniformly spaced s values.
        """
        s_vals = np.linspace(self._s_edges[0], self._s_edges[-1], n_points)
        bvs = self.boundary_values
        lines = [
            f"ScaleLadder: {self._label}",
            f"  Rungs: {self.n_rungs}   s ∈ [{self._s_edges[0]:.3f}, "
            f"{self._s_edges[-1]:.3f}] nats",
            f"  Boundary |Ψ|: "
            + "  ".join(f"{abs(v):.4f}" for v in bvs),
            "",
            f"  {'s':>6}  {'rung':>5}  {'|Ψ|²':>10}  {'Re Ψ':>10}  "
            f"{'phase':>10}  {'dθ/ds':>10}  {'J':>10}",
            "  " + "─" * 68,
        ]
        for sv in s_vals:
            r = self.full_eval(float(sv))
            lines.append(
                f"  {r.s:6.3f}  {r.rung:>5d}  "
                f"{r.modulus_sq:10.6f}  {r.value.real:10.6f}  "
                f"{r.phase:10.6f}  {r.phase_rate:10.6f}  "
                f"{r.phase_current:10.6f}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"ScaleLadder({self._label!r}, {self.n_rungs} rungs, "
            f"s∈[{self._s_edges[0]:.2f},{self._s_edges[-1]:.2f}])"
        )


# ---------------------------------------------------------------------------
# Scale-gradient correction  (Paper 18, Theorem 1)
# ---------------------------------------------------------------------------

def scale_gradient_correction(
    ladder: ScaleLadder,
    s: float,
    delta_s: float,
    d_base: float = 1.0,
) -> ScaleGradientResult:
    """
    Compute the scale-gradient correction d_eff at scale s.

    Paper 18, Theorem 1 shows that the effective diffusion ratio acquires a
    correction from the scale-gradient of the field amplitude:

        d_eff(s) ≈ d_base · |Ψ(s + δs)| / |Ψ(s)|

    where δs is a small scale increment.  In the CNRS-H setting this ratio
    is computed from exact EGF evaluations — no finite differences in the
    underlying calculus.

    Parameters
    ----------
    ladder  : ScaleLadder   The multi-scale field.
    s       : float         Scale coordinate (nats).
    delta_s : float         Scale step for gradient estimate (nats).
    d_base  : float         Base diffusion ratio (default 1.0).

    Returns
    -------
    ScaleGradientResult
        .d_ratio    — |Ψ(s + δs)| / |Ψ(s)|
        .correction — (d_ratio − 1)
        .d_eff      — d_base · d_ratio
    """
    psi_s = ladder.evaluate(s)
    psi_s2 = ladder.evaluate(min(s + delta_s, ladder.s_edges[-1]))

    amp_s = abs(psi_s)
    amp_s2 = abs(psi_s2)

    if amp_s < 1e-30:
        warnings.warn(
            f"scale_gradient_correction: |Ψ({s:.4f})| ≈ 0; "
            "d_ratio is ill-defined.  Returning d_ratio=1.",
            stacklevel=2,
        )
        d_ratio = 1.0
    else:
        d_ratio = amp_s2 / amp_s

    correction = d_ratio - 1.0
    d_eff = d_base * d_ratio

    return ScaleGradientResult(
        s=float(s),
        delta_s=float(delta_s),
        d_ratio=d_ratio,
        correction=correction,
        d_eff=d_eff,
    )


# ---------------------------------------------------------------------------
# Profile utilities
# ---------------------------------------------------------------------------

def ladder_profile(
    ladder: ScaleLadder,
    s_vals: Sequence[float],
    observable: str = "modulus_sq",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Evaluate a named observable across a list of s values.

    Parameters
    ----------
    ladder     : ScaleLadder
    s_vals     : sequence of float   Global s coordinates.
    observable : str
        One of: 'modulus_sq', 'real_part', 'imag_part', 'phase',
                'phase_rate', 'phase_current', 'scale_derivative_real',
                'scale_derivative_imag', 'modulus'.

    Returns
    -------
    (s_array, values_array)  — both numpy float arrays (or complex for derivative).
    """
    _obs_map = {
        "modulus_sq":           ladder.modulus_sq,
        "modulus":              lambda s: abs(ladder.evaluate(s)),
        "real_part":            ladder.real_part,
        "imag_part":            ladder.imag_part,
        "phase":                ladder.phase,
        "phase_rate":           ladder.phase_rate,
        "phase_current":        ladder.phase_current,
        "scale_derivative_real": lambda s: ladder.scale_derivative(s).real,
        "scale_derivative_imag": lambda s: ladder.scale_derivative(s).imag,
    }
    if observable not in _obs_map:
        raise ValueError(
            f"Unknown observable {observable!r}. "
            f"Choose from: {list(_obs_map)}"
        )
    fn = _obs_map[observable]
    s_arr = np.asarray(s_vals, dtype=float)
    vals = np.array([fn(float(sv)) for sv in s_arr])
    return s_arr, vals


def ladder_to_scalelaws(ladder: ScaleLadder) -> List[ScaleLaw]:
    """
    Convert each rung of a ScaleLadder to a ScaleLaw.

    Returns a list of ScaleLaw objects (one per rung), enabling use of
    the cnrs_scale fitting, allometric, and Turing-threshold machinery
    on individual scale rungs.
    """
    return [
        ScaleLaw.from_cnrsh(sol.cnrs_h, name=f"rung_{k}")
        for k, sol in enumerate(ladder.solutions)
    ]


# ---------------------------------------------------------------------------
# Placeholder stubs — Thread 5 / Items (c)–(e)
# (Scoped; not yet implemented; depend on GR specialist input.)
# ---------------------------------------------------------------------------

class JunctionCondition:
    """
    C¹ amplitude matching at a scale boundary.  [Thread 5 / item (c)]

    Implements the junction conditions derived in Paper 20 (leading-order,
    conditional on GR specialist review).  Will enforce continuity of both
    Ψ and dΨ/ds across the rung boundary at s = s_junction.

    Not yet implemented.  Raises NotImplementedError.
    """

    def __init__(self, s_junction: float):
        self.s_junction = s_junction

    def apply(self, lower_rung: OdeSolution, upper_rung: OdeSolution):
        raise NotImplementedError(
            "JunctionCondition is not yet implemented.  "
            "Awaiting Thread 5 (GR specialist review of Paper 20 junction conditions)."
        )


class FieldEquationCheck:
    """
    5D Scale Space field equation residual monitor.  [Thread 5 / item (d)]

    Will verify that a ScaleLadder satisfies the SS field equations
    (Paper 17) and the correction factor F = 1 + 2/L (Papers 9–11) to
    within a specified tolerance.

    Not yet implemented.  Raises NotImplementedError.
    """

    def check(self, ladder: ScaleLadder, L: float) -> float:
        raise NotImplementedError(
            "FieldEquationCheck is not yet implemented.  "
            "Awaiting Thread 5 (GR specialist review)."
        )


class PsiZeroDeterminer:
    """
    Ψ₀ phase-scale and hidden-sector amplitude determination.  [Thread 5 / item (e)]

    Implements the Ψ₀ computation of Paper 22 once the GR conditionality
    of the C¹ amplitude result is resolved.

    Not yet implemented.  Raises NotImplementedError.
    """

    def determine(self, ladder: ScaleLadder) -> complex:
        raise NotImplementedError(
            "PsiZeroDeterminer is not yet implemented.  "
            "Awaiting Thread 5 (GR specialist review of Paper 22)."
        )
