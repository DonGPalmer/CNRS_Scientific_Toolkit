"""
Observation maps for complex-state-preserving CNRS workflows.

The central idea is to keep the complex state until an explicit observation
map is chosen: real, imaginary, modulus, modulus-squared, phase, or a
phase-current proxy.
"""
from __future__ import annotations

import numpy as np
from typing import Any, Callable


def _as_array(z: Any):
    return np.asarray(z, dtype=complex)


def real(z: Any):
    return np.real(_as_array(z))


def imag(z: Any):
    return np.imag(_as_array(z))


def abs_value(z: Any):
    return np.abs(_as_array(z))


def abs2(z: Any):
    arr = _as_array(z)
    return np.abs(arr) ** 2


def phase(z: Any, unwrap: bool = True):
    ph = np.angle(_as_array(z))
    return np.unwrap(ph) if unwrap else ph


def phase_current(z: Any, coord: Any = None, unwrap: bool = True):
    """
    Phase-current proxy J = |z|^2 d(arg z)/dx.

    If coord is None, unit grid spacing is used.
    """
    arr = _as_array(z)
    ph = phase(arr, unwrap=unwrap)
    if coord is None:
        grad = np.gradient(ph)
    else:
        grad = np.gradient(ph, np.asarray(coord, dtype=float))
    return (np.abs(arr) ** 2) * grad


def observe(z: Any, map_name: str, **kwargs):
    """Apply a named observation map."""
    key = map_name.lower().replace("-", "_")
    if key in {"re", "real"}:
        return real(z)
    if key in {"im", "imag", "imaginary"}:
        return imag(z)
    if key in {"abs", "mod", "modulus"}:
        return abs_value(z)
    if key in {"abs2", "mod2", "modulus_squared", "power", "intensity"}:
        return abs2(z)
    if key in {"phase", "arg", "argument"}:
        return phase(z, **kwargs)
    if key in {"phase_current", "current", "j"}:
        return phase_current(z, **kwargs)
    raise ValueError(f"Unknown observation map: {map_name!r}")


def observation_table(z: Any, coord: Any = None) -> dict[str, Any]:
    """Return the standard observation-map family for a complex state."""
    return {
        "real": real(z),
        "imag": imag(z),
        "abs": abs_value(z),
        "abs2": abs2(z),
        "phase": phase(z),
        "phase_current": phase_current(z, coord=coord),
    }


def compare_observation_maps(z1: Any, z2: Any, coord: Any = None) -> dict[str, float]:
    """Relative L2 differences across standard observation maps."""
    out = {}
    for name in ["real", "imag", "abs", "abs2", "phase", "phase_current"]:
        a = observe(z1, name, coord=coord) if name == "phase_current" else observe(z1, name)
        b = observe(z2, name, coord=coord) if name == "phase_current" else observe(z2, name)
        denom = np.linalg.norm(a)
        out[name] = float(np.linalg.norm(a - b) / (denom if denom else 1.0))
    return out
