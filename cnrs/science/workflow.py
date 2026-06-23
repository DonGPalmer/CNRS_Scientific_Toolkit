"""
cnrs.science.workflow
=====================

Theory-aligned scientific workflow helpers for CNRS v0.9.

These utilities keep a complex/CNRS state intact until an explicit observation
map is selected.  They are intentionally modest: the point is not to make a
new scientific claim, but to make complex-state preservation measurable in
small workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
import numpy as np

from .observation import observation_table, compare_observation_maps


@dataclass(frozen=True)
class ObservationPreservationReport:
    """Report comparing state-preserving and projected workflows."""

    name: str
    points: tuple[float, ...]
    complex_values: tuple[complex, ...]
    observations: Mapping[str, Any]
    metrics: Mapping[str, float]
    interpretation: str

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "n_points": len(self.points),
            "metrics": dict(self.metrics),
            "interpretation": self.interpretation,
        }


def _as_complex_array(values: Any) -> np.ndarray:
    return np.asarray(values, dtype=complex)


def sample_state(state: Any, points: Iterable[float]) -> tuple[complex, ...]:
    """Evaluate a CNRS scientific state, CnrsHNative/CnrsH object, or callable."""
    pts = tuple(float(p) for p in points)
    vals = []
    for p in pts:
        if hasattr(state, "evaluate"):
            vals.append(complex(state.evaluate(p)))
        else:
            vals.append(complex(state(p)))
    return tuple(vals)


def preservation_metrics(values: Any, *, coord: Any = None) -> dict[str, float]:
    """Return simple diagnostics for what projections keep or discard."""
    z = _as_complex_array(values)
    if coord is None:
        coord_arr = np.arange(len(z), dtype=float)
    else:
        coord_arr = np.asarray(coord, dtype=float)

    real_only = np.real(z).astype(complex)
    modulus_only = np.abs(z).astype(complex)
    abs2_only = (np.abs(z) ** 2).astype(complex)

    den = np.linalg.norm(z)
    den = den if den else 1.0
    phase = np.unwrap(np.angle(z)) if len(z) else np.asarray([])
    phase_span = float(np.max(phase) - np.min(phase)) if len(phase) else 0.0
    phase_rate = np.gradient(phase, coord_arr) if len(phase) > 1 else np.asarray([0.0])

    return {
        "real_projection_rel_error": float(np.linalg.norm(z - real_only) / den),
        "modulus_projection_rel_error": float(np.linalg.norm(z - modulus_only) / den),
        "abs2_projection_rel_error": float(np.linalg.norm(z - abs2_only) / den),
        "phase_span": phase_span,
        "mean_phase_rate": float(np.mean(phase_rate)) if len(phase_rate) else 0.0,
        "modulus_variation": float(np.max(np.abs(z)) - np.min(np.abs(z))) if len(z) else 0.0,
        "intensity_variation": float(np.max(np.abs(z) ** 2) - np.min(np.abs(z) ** 2)) if len(z) else 0.0,
    }


def build_preservation_report(
    state: Any,
    points: Iterable[float],
    *,
    name: str = "cnrs_preservation_workflow",
) -> ObservationPreservationReport:
    """Sample a state and return standard observation/projection diagnostics."""
    pts = tuple(float(p) for p in points)
    vals = sample_state(state, pts)
    obs = observation_table(vals, coord=pts)
    metrics = preservation_metrics(vals, coord=pts)
    return ObservationPreservationReport(
        name=name,
        points=pts,
        complex_values=vals,
        observations=obs,
        metrics=metrics,
        interpretation=(
            "The complex state is sampled first and observation maps are applied late; "
            "projection errors quantify what real/modulus/intensity reductions discard."
        ),
    )


def compare_state_pair(
    state_a: Any,
    state_b: Any,
    points: Iterable[float],
) -> dict[str, float]:
    """Compare two state-preserving workflows across observation maps."""
    pts = tuple(float(p) for p in points)
    a = sample_state(state_a, pts)
    b = sample_state(state_b, pts)
    return compare_observation_maps(a, b, coord=pts)


__all__ = [
    "ObservationPreservationReport",
    "sample_state",
    "preservation_metrics",
    "build_preservation_report",
    "compare_state_pair",
]
