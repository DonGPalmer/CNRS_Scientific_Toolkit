"""
cnrs_regime.py
==============
Component 8 of the CNRS Scientific Toolkit.

Scale-sweep and regime-detection layer: a lightweight wrapper around
arbitrary scientific models that makes parameters explicit functions of
logarithmic scale, sweeps across scale intervals, and detects regime
transitions.

Design credit: AI1 proposed the core abstraction (ScaleParameter,
ScaleSweep, RegimeTransition, detect_transitions) in the June 2026
review of the multi-scale modelling direction.  This implementation
adapts that design to the toolkit naming convention and adds an explicit
bridge to Component 7 (ScaleLadder), so that CNRS-H exact physics can
serve as the model inside a ScaleSweep.

Architecture
------------
The intended workflow is:

    1. Define one or more scale-dependent parameters (ScaleParameter).
    2. Define a model function: model(s, params) → any output.
       OR supply a ScaleLadder directly (ScaleSweep.from_ladder).
    3. Run ScaleSweep.run() to evaluate the model across a scale grid.
    4. Supply a classifier: output → bool to identify regime state.
    5. Inspect RegimeTransition objects and active_intervals().

The dependency chain with Component 7:

    cnrs_multiscale.ScaleLadder   (exact CNRS-H physics)
              ↓
    cnrs_regime.ScaleSweep        (scale-sweep + regime classification)
              ↓
    RegimeTransition / active_intervals  (transition detection)

ScaleSweep.from_ladder() takes a ScaleLadder and a classifier that
operates on LadderEvalResult objects, giving the full chain from CNRS-H
physics to regime detection without any intermediate model function.

Scale coordinate convention
----------------------------
    s = log(L / L_ref)    (natural logarithm; nats)

Utilities logarithmic_scale() and length_from_scale() convert between
physical length L and scale coordinate s.

Public API
----------
ScaleParameter:
    ScaleParameter(base, coefficients, name=None, enforce_positive=False)
        p(s) = base * (1 + c1*s + c2*s² + ...)
    p(s)            scalar evaluation
    p.values(scales) list of evaluations

RegimeTransition:
    .s_left, .s_right   boundary scale coordinates
    .state_left, .state_right  boolean states either side
    .midpoint           (s_left + s_right) / 2

ScaleSweepResult:
    .scales             list of scale grid points
    .outputs            list of raw model outputs
    .regime             optional list of bool (one per scale point)
    .transitions        optional list of RegimeTransition
    .active_intervals() list of (s_lo, s_hi) where regime is True

ScaleSweep:
    ScaleSweep(model, parameters, s_min, s_max, n, classifier=None)
        General constructor: model is any callable (s, params) → output.

    ScaleSweep.from_ladder(ladder, classifier, s_min=None, s_max=None, n=50)
        Bridge constructor: model is a ScaleLadder; classifier operates
        on LadderEvalResult objects.

    sweep.run()         → ScaleSweepResult
    sweep.scale_grid()  → list of float

Utilities:
    detect_transitions(scales, states)   → list of RegimeTransition
    logarithmic_scale(length, reference_length)  → float (nats)
    length_from_scale(s, reference_length)       → float

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 44, 2026-06-07
Design:  AI1 (June 2026 multi-scale review)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# Component 7 import — optional to allow cnrs_regime to be imported
# independently of cnrs_multiscale in unit tests.
try:
    from .cnrs_multiscale import ScaleLadder, LadderEvalResult
    _MULTISCALE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _MULTISCALE_AVAILABLE = False

Number = float


# ---------------------------------------------------------------------------
# ScaleParameter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ScaleParameter:
    """
    A model parameter represented as a polynomial function of logarithmic scale.

    The scale coordinate is:
        s = log(L / L_ref)   (natural logarithm; nats)

    The parameter evaluates as:
        p(s) = base * (1 + c1*s + c2*s² + c3*s³ + ...)

    where coefficients = [c1, c2, c3, ...].  An empty coefficient list
    gives a constant parameter p(s) = base.

    Parameters
    ----------
    base             : float   Value at s = 0.
    coefficients     : sequence of float   Polynomial coefficients [c1, c2, ...].
    name             : str, optional        Human-readable label.
    enforce_positive : bool    If True, raise ValueError when p(s) ≤ 0.

    Examples
    --------
    >>> D = ScaleParameter(base=100.0, coefficients=[-0.3], name='D_v')
    >>> D(0.0)
    100.0
    >>> D(1.0)
    70.0
    >>> D = ScaleParameter(base=1.0, coefficients=[0.0])  # constant
    >>> D(5.0)
    1.0
    """

    base: Number
    coefficients: Sequence[Number]
    name: Optional[str] = None
    enforce_positive: bool = False

    def __call__(self, s: Number) -> Number:
        """Evaluate parameter at scale coordinate s."""
        multiplier = 1.0
        for power, coeff in enumerate(self.coefficients, start=1):
            multiplier += coeff * (s ** power)
        value = self.base * multiplier
        if self.enforce_positive and value <= 0:
            raise ValueError(
                f"ScaleParameter {self.name or '<unnamed>'} became non-positive "
                f"at s={s:.4f}: value={value:.6f}"
            )
        return value

    def values(self, scales: Iterable[Number]) -> List[Number]:
        """Evaluate at each scale in an iterable."""
        return [self(s) for s in scales]

    def __repr__(self) -> str:
        name = self.name or "<unnamed>"
        return (
            f"ScaleParameter({name!r}, base={self.base}, "
            f"coefficients={list(self.coefficients)})"
        )


# ---------------------------------------------------------------------------
# RegimeTransition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegimeTransition:
    """
    A detected transition between two neighbouring scale samples.

    A transition is recorded when a boolean regime indicator changes
    (False → True or True → False) between adjacent scale grid points.

    Attributes
    ----------
    s_left       : float   Scale at the left sample (before transition).
    s_right      : float   Scale at the right sample (after transition).
    state_left   : bool    Regime state at s_left.
    state_right  : bool    Regime state at s_right.
    """

    s_left: Number
    s_right: Number
    state_left: bool
    state_right: bool

    @property
    def midpoint(self) -> Number:
        """Midpoint estimate of the transition scale."""
        return 0.5 * (self.s_left + self.s_right)

    def __repr__(self) -> str:
        return (
            f"RegimeTransition(s≈{self.midpoint:.4f}, "
            f"{self.state_left}→{self.state_right})"
        )


# ---------------------------------------------------------------------------
# ScaleSweepResult
# ---------------------------------------------------------------------------

@dataclass
class ScaleSweepResult:
    """
    Result of a ScaleSweep.run() call.

    Attributes
    ----------
    scales      : list of float   Scale grid points.
    outputs     : list            Raw model outputs (one per scale point).
    regime      : list of bool, optional   Classifier output per scale point.
    transitions : list of RegimeTransition, optional   Detected transitions.
    """

    scales: List[Number]
    outputs: List[Any]
    regime: Optional[List[bool]] = None
    transitions: Optional[List[RegimeTransition]] = None

    def active_intervals(self) -> List[Tuple[Number, Number]]:
        """
        Return scale intervals where the regime flag is True.

        Useful for identifying stability windows, patterning windows,
        resonance windows, or other scale-dependent active regions.

        Returns
        -------
        list of (s_lo, s_hi) tuples.  Empty list if regime is None.
        """
        if self.regime is None:
            return []

        intervals: List[Tuple[Number, Number]] = []
        start: Optional[Number] = None

        for s, active in zip(self.scales, self.regime):
            if active and start is None:
                start = s
            elif not active and start is not None:
                intervals.append((start, s))
                start = None

        if start is not None:
            intervals.append((start, self.scales[-1]))

        return intervals

    def __repr__(self) -> str:
        n_active = sum(self.regime) if self.regime else 0
        n_trans = len(self.transitions) if self.transitions else 0
        return (
            f"ScaleSweepResult({len(self.scales)} points, "
            f"{n_active} active, {n_trans} transitions)"
        )


# ---------------------------------------------------------------------------
# ScaleSweep
# ---------------------------------------------------------------------------

class ScaleSweep:
    """
    Run a model over a range of logarithmic scales.

    General constructor
    -------------------
    The model callable must accept (s, parameters) where:
        s          : float               Current scale coordinate (nats).
        parameters : dict[str, float]    Evaluated parameter values at s.

    The model may return any object.  A separate classifier converts
    each output into a boolean regime indicator.

    Bridge constructor (from_ladder)
    ---------------------------------
    ScaleSweep.from_ladder(ladder, classifier, ...) wraps a ScaleLadder
    (Component 7) so that CNRS-H exact physics serves as the model.
    The classifier receives a LadderEvalResult; no ScaleParameter objects
    are needed (the ladder already encodes scale dependence exactly).
    """

    def __init__(
        self,
        model: Callable[[Number, Dict[str, Number]], Any],
        parameters: Dict[str, ScaleParameter],
        s_min: Number,
        s_max: Number,
        n: int,
        classifier: Optional[Callable[[Any], bool]] = None,
        label: str = "ScaleSweep",
    ) -> None:
        if n < 2:
            raise ValueError("ScaleSweep requires n >= 2.")
        if s_max <= s_min:
            raise ValueError("ScaleSweep requires s_max > s_min.")

        self.model = model
        self.parameters = parameters
        self.s_min = float(s_min)
        self.s_max = float(s_max)
        self.n = n
        self.classifier = classifier
        self.label = label

    # ── Bridge constructor ────────────────────────────────────────────────────

    @classmethod
    def from_ladder(
        cls,
        ladder: "ScaleLadder",
        classifier: Callable[["LadderEvalResult"], bool],
        s_min: Optional[Number] = None,
        s_max: Optional[Number] = None,
        n: int = 50,
        label: str = "ladder_sweep",
    ) -> "ScaleSweep":
        """
        Build a ScaleSweep whose model is a ScaleLadder (Component 7).

        The model evaluates the full LadderEvalResult at each scale point;
        the classifier operates on LadderEvalResult objects directly.

        Parameters
        ----------
        ladder     : ScaleLadder   The CNRS-H multi-scale field.
        classifier : callable      LadderEvalResult → bool.
        s_min      : float, optional  Defaults to ladder.s_edges[0].
        s_max      : float, optional  Defaults to ladder.s_edges[-1].
        n          : int           Number of scale grid points.
        label      : str           Human-readable name.

        Returns
        -------
        ScaleSweep
        """
        if not _MULTISCALE_AVAILABLE:  # pragma: no cover
            raise ImportError("cnrs_multiscale is required for ScaleSweep.from_ladder.")

        s_lo = float(s_min) if s_min is not None else ladder.s_edges[0]
        s_hi = float(s_max) if s_max is not None else ladder.s_edges[-1]

        # Model wraps the ladder: returns LadderEvalResult
        def _ladder_model(s, params):  # params unused (ladder encodes dependence)
            return ladder.full_eval(s)

        sweep = cls(
            model=_ladder_model,
            parameters={},       # no ScaleParameter objects needed
            s_min=s_lo,
            s_max=s_hi,
            n=n,
            classifier=classifier,
            label=label,
        )
        return sweep

    # ── Scale grid ────────────────────────────────────────────────────────────

    def scale_grid(self) -> List[Number]:
        """Uniformly spaced scale grid from s_min to s_max (n points)."""
        step = (self.s_max - self.s_min) / (self.n - 1)
        return [self.s_min + i * step for i in range(self.n)]

    def evaluated_parameters(self, s: Number) -> Dict[str, Number]:
        """Evaluate all ScaleParameters at scale s."""
        return {name: param(s) for name, param in self.parameters.items()}

    # ── Run ──────────────────────────────────────────────────────────────────

    def run(self) -> ScaleSweepResult:
        """
        Evaluate the model across the scale grid.

        Returns
        -------
        ScaleSweepResult
        """
        scales = self.scale_grid()
        outputs: List[Any] = []

        for s in scales:
            params = self.evaluated_parameters(s)
            outputs.append(self.model(s, params))

        regime: Optional[List[bool]] = None
        transitions: Optional[List[RegimeTransition]] = None

        if self.classifier is not None:
            regime = [bool(self.classifier(output)) for output in outputs]
            transitions = detect_transitions(scales, regime)

        return ScaleSweepResult(
            scales=scales,
            outputs=outputs,
            regime=regime,
            transitions=transitions,
        )

    def __repr__(self) -> str:
        return (
            f"ScaleSweep({self.label!r}, n={self.n}, "
            f"s∈[{self.s_min:.2f},{self.s_max:.2f}])"
        )


# ---------------------------------------------------------------------------
# detect_transitions
# ---------------------------------------------------------------------------

def detect_transitions(
    scales: Sequence[Number],
    states: Sequence[bool],
) -> List[RegimeTransition]:
    """
    Detect boolean regime changes across a scale sequence.

    Parameters
    ----------
    scales : sequence of float   Scale grid points.
    states : sequence of bool    Regime flag at each grid point.

    Returns
    -------
    list of RegimeTransition, one per state change.

    Raises
    ------
    ValueError if scales and states have different lengths.
    """
    if len(scales) != len(states):
        raise ValueError(
            f"scales and states must have the same length; "
            f"got {len(scales)} and {len(states)}."
        )

    transitions: List[RegimeTransition] = []
    for i in range(1, len(scales)):
        if bool(states[i]) != bool(states[i - 1]):
            transitions.append(
                RegimeTransition(
                    s_left=scales[i - 1],
                    s_right=scales[i],
                    state_left=bool(states[i - 1]),
                    state_right=bool(states[i]),
                )
            )
    return transitions


# ---------------------------------------------------------------------------
# Coordinate utilities
# ---------------------------------------------------------------------------

def logarithmic_scale(length: Number, reference_length: Number) -> Number:
    """
    Compute logarithmic scale coordinate s = log(L / L_ref).

    Parameters
    ----------
    length           : float   Physical length L (must be > 0).
    reference_length : float   Reference length L_ref (must be > 0).

    Returns
    -------
    float   Scale coordinate in nats.
    """
    if length <= 0:
        raise ValueError(f"length must be positive; got {length}.")
    if reference_length <= 0:
        raise ValueError(f"reference_length must be positive; got {reference_length}.")
    return math.log(length / reference_length)


def length_from_scale(s: Number, reference_length: Number) -> Number:
    """
    Convert scale coordinate back to physical length: L = L_ref * exp(s).

    Parameters
    ----------
    s                : float   Scale coordinate (nats).
    reference_length : float   Reference length L_ref (must be > 0).

    Returns
    -------
    float   Physical length L.
    """
    if reference_length <= 0:
        raise ValueError(f"reference_length must be positive; got {reference_length}.")
    return reference_length * math.exp(s)
