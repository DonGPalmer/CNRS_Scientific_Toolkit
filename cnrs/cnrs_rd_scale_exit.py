"""
Reaction-diffusion scale-exit utilities.

This module provides a small, reusable analysis layer for two-species
reaction-diffusion systems whose diffusion coefficients vary with logarithmic
scale.

The intent is not to replace full PDE solvers.  Instead, the module answers a
narrow multi-scale question:

    At which scales is the homogeneous state linearly Turing-unstable?

For a two-species system linearized at a homogeneous steady state,

    d/dt [u, v]^T = J [u, v]^T + diag(D_u(s), D_v(s)) nabla^2 [u, v]^T,

where s = log(L/L0), the mode with q = k^2 has Jacobian

    J_q = J - q diag(D_u, D_v).

If the homogeneous kinetics are stable, a diffusion-driven instability is
possible when the determinant of J_q becomes negative for some q > 0.  This
module evaluates that condition across scale and detects scale entry/exit
points.

The utilities are deliberately lightweight so they can wrap existing biological
models, CellML/BioModels reductions, or CNRS-H ScaleLaw objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple

import math

try:  # optional at runtime, but available in the toolkit test environment
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

Number = float
ScaleFunction = Callable[[Number], Number]


@dataclass(frozen=True)
class RDLinearKinetics:
    """Two-species reaction kinetics linearized at a homogeneous state.

    The matrix convention is::

        J = [[f_u, f_v],
             [g_u, g_v]]

    where f and g are the reaction terms for the two species.
    """

    f_u: Number
    f_v: Number
    g_u: Number
    g_v: Number
    name: str = "linear_kinetics"

    @property
    def trace(self) -> Number:
        return self.f_u + self.g_v

    @property
    def determinant(self) -> Number:
        return self.f_u * self.g_v - self.f_v * self.g_u

    def homogeneous_stable(self) -> bool:
        """Return True if the no-diffusion homogeneous state is stable."""
        return self.trace < 0.0 and self.determinant > 0.0

    @classmethod
    def from_matrix(cls, matrix: Sequence[Sequence[Number]], name: str = "linear_kinetics") -> "RDLinearKinetics":
        """Construct from a 2x2 nested sequence or numpy array."""
        return cls(
            f_u=float(matrix[0][0]),
            f_v=float(matrix[0][1]),
            g_u=float(matrix[1][0]),
            g_v=float(matrix[1][1]),
            name=name,
        )


@dataclass(frozen=True)
class ExponentialDiffusionLaw:
    """Simple positive diffusion law D(s) = D0 * exp(lambda_s * s)."""

    d0: Number
    lambda_s: Number
    name: str = "D"

    def __call__(self, s: Number) -> Number:
        if self.d0 <= 0:
            raise ValueError(f"{self.name}: d0 must be positive")
        return self.d0 * math.exp(self.lambda_s * s)


@dataclass(frozen=True)
class TuringPoint:
    """Turing diagnostic values at one scale sample."""

    s: Number
    d_u: Number
    d_v: Number
    ratio: Number
    active: bool
    q_star: Optional[Number]
    margin: Number


@dataclass(frozen=True)
class ScaleTransition:
    """Transition between inactive and active Turing regimes."""

    s_left: Number
    s_right: Number
    active_left: bool
    active_right: bool
    s_mid: Number

    @property
    def kind(self) -> str:
        if not self.active_left and self.active_right:
            return "entry"
        if self.active_left and not self.active_right:
            return "exit"
        return "change"


@dataclass(frozen=True)
class ScaleExitResult:
    """Result of a reaction-diffusion scale-exit scan."""

    points: List[TuringPoint]
    transitions: List[ScaleTransition]

    @property
    def scales(self) -> List[Number]:
        return [p.s for p in self.points]

    @property
    def active(self) -> List[bool]:
        return [p.active for p in self.points]

    @property
    def ratios(self) -> List[Number]:
        return [p.ratio for p in self.points]

    def active_intervals(self) -> List[Tuple[Number, Number]]:
        """Return approximate scale intervals over which Turing instability is active."""
        if not self.points:
            return []

        intervals: List[Tuple[Number, Number]] = []
        start: Optional[Number] = None

        for point in self.points:
            if point.active and start is None:
                start = point.s
            elif not point.active and start is not None:
                intervals.append((start, point.s))
                start = None

        if start is not None:
            intervals.append((start, self.points[-1].s))

        return intervals

    def first_exit(self) -> Optional[Number]:
        """Return the first active -> inactive transition midpoint, if present."""
        for transition in self.transitions:
            if transition.kind == "exit":
                return transition.s_mid
        return None

    def first_entry(self) -> Optional[Number]:
        """Return the first inactive -> active transition midpoint, if present."""
        for transition in self.transitions:
            if transition.kind == "entry":
                return transition.s_mid
        return None


@dataclass(frozen=True)
class TuringThresholds:
    """Diffusion-ratio thresholds for a two-species Turing instability."""

    d_low: Optional[Number]
    d_high: Optional[Number]
    stable_kinetics: bool


def _as_float(value) -> float:
    """Convert float, numpy scalar, or complex-with-small-imaginary to float."""
    if isinstance(value, complex):
        if abs(value.imag) > 1e-9:
            raise ValueError(f"Expected real value, got {value}")
        return float(value.real)
    return float(value)


def turing_thresholds(kinetics: RDLinearKinetics) -> TuringThresholds:
    """Return diffusion-ratio roots for the two-species Turing condition.

    The calculation assumes D_u is normalized to 1 and d = D_v/D_u.
    For stable homogeneous kinetics, Turing instability requires::

        f_u*d + g_v > 0
        (f_u*d + g_v)^2 - 4*d*det(J) > 0

    The roots reported here are the roots of the discriminant polynomial.
    The active region must still be tested with :func:`turing_active` because
    the sign condition f_u*d + g_v > 0 also matters.
    """
    if not kinetics.homogeneous_stable():
        return TuringThresholds(None, None, False)

    det_j = kinetics.determinant
    a = kinetics.f_u ** 2
    b = 2.0 * kinetics.f_u * kinetics.g_v - 4.0 * det_j
    c = kinetics.g_v ** 2

    if abs(a) < 1e-15:
        return TuringThresholds(None, None, True)

    disc = b * b - 4.0 * a * c
    if disc < 0:
        return TuringThresholds(None, None, True)

    root_disc = math.sqrt(disc)
    r1 = (-b - root_disc) / (2.0 * a)
    r2 = (-b + root_disc) / (2.0 * a)
    return TuringThresholds(min(r1, r2), max(r1, r2), True)


def turing_diagnostic(kinetics: RDLinearKinetics, d_u: Number, d_v: Number, s: Number = 0.0) -> TuringPoint:
    """Evaluate the Turing condition for one scale sample."""
    d_u = _as_float(d_u)
    d_v = _as_float(d_v)
    if d_u <= 0.0 or d_v <= 0.0:
        raise ValueError("Diffusion coefficients must be positive")

    ratio = d_v / d_u
    det_j = kinetics.determinant

    # For general D_u and D_v, determinant polynomial in q = k^2 is:
    # D_u D_v q^2 - (f_u D_v + g_v D_u) q + det(J).
    linear = kinetics.f_u * d_v + kinetics.g_v * d_u
    margin = linear * linear - 4.0 * d_u * d_v * det_j
    q_star = linear / (2.0 * d_u * d_v) if d_u * d_v > 0 else None

    active = bool(
        kinetics.homogeneous_stable()
        and q_star is not None
        and q_star > 0.0
        and margin > 0.0
    )

    return TuringPoint(
        s=_as_float(s),
        d_u=d_u,
        d_v=d_v,
        ratio=ratio,
        active=active,
        q_star=q_star if q_star is not None and q_star > 0.0 else None,
        margin=margin,
    )


def scan_scale_exit(
    kinetics: RDLinearKinetics,
    d_u: ScaleFunction,
    d_v: ScaleFunction,
    s_min: Number,
    s_max: Number,
    n: int = 201,
    refine: bool = True,
    bisection_steps: int = 48,
) -> ScaleExitResult:
    """Scan a scale interval and detect Turing entry/exit transitions.

    Parameters
    ----------
    kinetics:
        Linearized two-species kinetics at the homogeneous state.
    d_u, d_v:
        Positive diffusion laws as functions of logarithmic scale s.
    s_min, s_max:
        Scale interval in nats.
    n:
        Number of samples. Must be at least 2.
    refine:
        If True, refine detected transitions by bisection.
    bisection_steps:
        Number of bisection iterations for transition refinement.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    if s_max <= s_min:
        raise ValueError("s_max must be greater than s_min")

    step = (s_max - s_min) / (n - 1)
    scales = [s_min + i * step for i in range(n)]
    points = [turing_diagnostic(kinetics, d_u(s), d_v(s), s=s) for s in scales]

    transitions: List[ScaleTransition] = []

    def active_at(x: Number) -> bool:
        return turing_diagnostic(kinetics, d_u(x), d_v(x), s=x).active

    for left, right in zip(points[:-1], points[1:]):
        if left.active == right.active:
            continue

        s_l, s_r = left.s, right.s
        if refine:
            a, b = s_l, s_r
            a_state = left.active
            for _ in range(bisection_steps):
                m = 0.5 * (a + b)
                m_state = active_at(m)
                if m_state == a_state:
                    a = m
                else:
                    b = m
            s_mid = 0.5 * (a + b)
        else:
            s_mid = 0.5 * (s_l + s_r)

        transitions.append(
            ScaleTransition(
                s_left=s_l,
                s_right=s_r,
                active_left=left.active,
                active_right=right.active,
                s_mid=s_mid,
            )
        )

    return ScaleExitResult(points=points, transitions=transitions)


def exponential_gm_scale_exit(
    kinetics: RDLinearKinetics,
    d_u0: Number,
    d_v0: Number,
    lambda_u: Number,
    lambda_v: Number,
    s_min: Number = 0.0,
    s_max: Number = 4.0,
    n: int = 201,
) -> ScaleExitResult:
    """Convenience wrapper for exponential diffusion laws."""
    du = ExponentialDiffusionLaw(d_u0, lambda_u, name="D_u")
    dv = ExponentialDiffusionLaw(d_v0, lambda_v, name="D_v")
    return scan_scale_exit(kinetics, du, dv, s_min=s_min, s_max=s_max, n=n)


def gm_default_kinetics():
    """Return the default Gierer-Meinhardt kinetics used in cnrs_bio.

    This is imported lazily to avoid a hard dependency cycle at module import.
    """
    from .cnrs_bio import GmParams, gm_jacobian

    params = GmParams()
    return RDLinearKinetics.from_matrix(gm_jacobian(params), name="GM_default")


# ---------------------------------------------------------------------------
# ScaleLadder and ScaleLaw bridges
# ---------------------------------------------------------------------------

def ladder_diffusion_law(ladder: "ScaleLadder", observable: str = "modulus") -> ScaleFunction:
    """
    Convert a ScaleLadder (Component 7) into a ScaleFunction for use with
    scan_scale_exit.

    The ScaleLadder represents a CNRS-H EGF field Ψ(s) across the scale
    ladder.  Its amplitude |Ψ(s)| is a real positive function of s that can
    serve as a scale-dependent diffusion coefficient.

    Parameters
    ----------
    ladder     : ScaleLadder   CNRS-H multi-scale field.
    observable : str
        How to extract a real positive value from the ladder at each s.
        - 'modulus'    : |Ψ(s)| = sqrt(|Ψ|²)  [default; always positive]
        - 'modulus_sq' : |Ψ(s)|²               [also always positive]
        - 'real_part'  : Re(Ψ(s))              [caller must ensure > 0]

    Returns
    -------
    ScaleFunction   callable s → float, suitable for scan_scale_exit.

    Physical interpretation
    -----------------------
    If Ψ_s = f(s)·exp(iθ(s)) is the CNRS-H field representing a diffusion
    mode, then |Ψ(s)| = f(s) is the amplitude of that mode at scale s.
    Paper 18, Theorem 1 shows that the effective diffusion ratio acquires a
    scale-gradient correction proportional to f'(s)/f(s), computed exactly
    via the digit-shift derivative.

    The CNRS-H computation is more precise than the scalar exponential
    approximation: for a true exponential law D(s) = D₀·exp(λs) the two
    agree exactly; for any non-exponential profile (multi-scale coupling,
    oscillatory components, etc.) only the ladder gives the correct value.
    """
    _valid = ("modulus", "modulus_sq", "real_part")
    if observable not in _valid:
        raise ValueError(f"observable must be one of {_valid}; got {observable!r}")

    if observable == "modulus":
        def fn(s: float) -> float:
            import math as _math
            return _math.sqrt(ladder.modulus_sq(s))
    elif observable == "modulus_sq":
        def fn(s: float) -> float:
            return ladder.modulus_sq(s)
    else:
        def fn(s: float) -> float:
            v = ladder.real_part(s)
            if v <= 0:
                raise ValueError(
                    f"ladder_diffusion_law: Re(Ψ({s:.4f})) = {v:.6f} ≤ 0; "
                    "use observable='modulus' for a guaranteed positive value."
                )
            return v

    return fn


def scalelaw_diffusion_law(law: "ScaleLaw") -> ScaleFunction:
    """
    Convert a ScaleLaw (Component 3 / cnrs_scale) into a ScaleFunction for
    use with scan_scale_exit.

    This bridges the existing cnrs_bio diffusion profiles (da_profile,
    dh_profile) directly into the RD scale-exit scanner without wrapping
    them in a full ScaleLadder.

    Parameters
    ----------
    law : ScaleLaw   CNRS-H backed scale law.

    Returns
    -------
    ScaleFunction   callable s → float (|law(s)| as a positive float).

    Example
    -------
    >>> from cnrs.cnrs_bio import da_profile, dh_profile, gm_default_kinetics
    >>> from cnrs.cnrs_rd_scale_exit import scalelaw_diffusion_law, scan_scale_exit
    >>> du = scalelaw_diffusion_law(da_profile())
    >>> dv = scalelaw_diffusion_law(dh_profile())
    >>> result = scan_scale_exit(gm_default_kinetics(), du, dv, 0.0, 2.0)
    """
    import math as _math

    def fn(s: float) -> float:
        v = law.evaluate(complex(s))
        mag = _math.sqrt(v.real ** 2 + v.imag ** 2)
        if mag <= 0:
            raise ValueError(
                f"scalelaw_diffusion_law: |law({s:.4f})| = 0; "
                "diffusion coefficients must be positive."
            )
        return mag

    return fn


def scan_scale_exit_ladder(
    kinetics: "RDLinearKinetics",
    ladder_u: "ScaleLadder",
    ladder_v: "ScaleLadder",
    s_min: float = None,
    s_max: float = None,
    n: int = 201,
    observable: str = "modulus",
    refine: bool = True,
    bisection_steps: int = 48,
) -> "ScaleExitResult":
    """
    Scan for Turing entry/exit transitions using ScaleLadder fields for
    the diffusion coefficients.

    This is the full CNRS-H path: diffusion profiles are represented as
    exact EGF streams propagated across the scale ladder rather than as
    scalar exponential approximations.

    Parameters
    ----------
    kinetics   : RDLinearKinetics   Linearized two-species kinetics.
    ladder_u   : ScaleLadder        CNRS-H field for D_u(s).
    ladder_v   : ScaleLadder        CNRS-H field for D_v(s).
    s_min      : float, optional    Defaults to max of ladder lower bounds.
    s_max      : float, optional    Defaults to min of ladder upper bounds.
    n          : int                Number of scale samples.
    observable : str                How to extract D from each ladder;
                                    see ladder_diffusion_law.
    refine     : bool               Bisection refinement of transitions.
    bisection_steps : int           Bisection iterations.

    Returns
    -------
    ScaleExitResult

    Notes
    -----
    The two ladders need not have the same rung structure; they are
    evaluated independently at each scale point.  The only requirement
    is that [s_min, s_max] lies within both ladders' domains.
    """
    # Determine s range from ladders if not supplied
    s_lo = max(ladder_u.s_edges[0], ladder_v.s_edges[0])
    s_hi = min(ladder_u.s_edges[-1], ladder_v.s_edges[-1])

    if s_min is not None:
        s_lo = max(s_lo, float(s_min))
    if s_max is not None:
        s_hi = min(s_hi, float(s_max))

    if s_hi <= s_lo:
        raise ValueError(
            f"No overlapping scale range: ladder_u covers "
            f"[{ladder_u.s_edges[0]:.3f},{ladder_u.s_edges[-1]:.3f}], "
            f"ladder_v covers [{ladder_v.s_edges[0]:.3f},{ladder_v.s_edges[-1]:.3f}]."
        )

    du_fn = ladder_diffusion_law(ladder_u, observable=observable)
    dv_fn = ladder_diffusion_law(ladder_v, observable=observable)

    return scan_scale_exit(
        kinetics, du_fn, dv_fn,
        s_min=s_lo, s_max=s_hi,
        n=n, refine=refine, bisection_steps=bisection_steps,
    )
