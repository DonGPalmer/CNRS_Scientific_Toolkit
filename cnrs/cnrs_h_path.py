"""
cnrs.cnrs_h_path
================

Piecewise-linear continuation paths and winding-number scaffolding for
CNRS-H branch-aware local jets.

This module is deliberately conservative.  It does not implement full analytic
continuation or Riemann-surface lifting.  It gives the toolkit explicit path
objects, winding-number calculations around isolated branch points, and simple
branch-state update rules for local logarithm/square-root bookkeeping.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Iterable, Sequence

from .symbolic import BranchState, DEFAULT_BRANCH_STATE

TAU = 2.0 * math.pi


class ContinuationPathError(ValueError):
    """Raised for invalid continuation-path operations."""


def _as_complex(z: complex | float | int) -> complex:
    return complex(z)


def _canonical_int(x: float, *, tol: float = 1e-9) -> int:
    nearest = round(x)
    if abs(x - nearest) <= tol:
        return int(nearest)
    return int(nearest)


@dataclass(frozen=True)
class PathSegment:
    """A straight segment of a continuation path in the complex plane."""

    start: complex
    end: complex

    def __post_init__(self) -> None:
        object.__setattr__(self, "start", _as_complex(self.start))
        object.__setattr__(self, "end", _as_complex(self.end))

    @property
    def delta(self) -> complex:
        return self.end - self.start

    @property
    def length(self) -> float:
        return abs(self.delta)

    def point_at(self, t: float) -> complex:
        if not 0.0 <= t <= 1.0:
            raise ValueError("segment parameter t must lie in [0, 1]")
        return self.start + t * self.delta

    def distance_to(self, point: complex | float | int) -> float:
        """Return the Euclidean distance from ``point`` to this segment."""
        p = _as_complex(point)
        if self.length == 0:
            return abs(p - self.start)
        v = self.delta
        t = ((p - self.start).real * v.real + (p - self.start).imag * v.imag) / (abs(v) ** 2)
        t = max(0.0, min(1.0, t))
        return abs(p - self.point_at(t))

    def crosses(self, point: complex | float | int, *, tol: float = 1e-12) -> bool:
        return self.distance_to(point) <= tol


@dataclass(frozen=True)
class BranchPoint:
    """An isolated branch point used by local path/winding diagnostics."""

    location: complex = 0j
    kind: str = "log"
    label: str = "0"

    def __post_init__(self) -> None:
        object.__setattr__(self, "location", _as_complex(self.location))


@dataclass(frozen=True)
class WindingEvent:
    """A path-induced branch-state event around a branch point."""

    branch_point: BranchPoint
    winding: int

    @property
    def kind(self) -> str:
        return self.branch_point.kind

    def summary(self) -> str:
        return f"{self.kind}@{self.branch_point.location:g}: winding={self.winding}"


@dataclass(frozen=True)
class ContinuationPath:
    """Piecewise-linear path in the complex plane.

    Parameters
    ----------
    points:
        Two or more complex points.  Consecutive points define straight
        path segments.  The path may be open or closed.
    label:
        Optional human-readable name stored in jet path histories.
    """

    points: tuple[complex, ...]
    label: str = ""

    def __init__(self, points: Iterable[complex | float | int], label: str = "") -> None:
        pts = tuple(_as_complex(z) for z in points)
        if len(pts) < 2:
            raise ContinuationPathError("a continuation path needs at least two points")
        object.__setattr__(self, "points", pts)
        object.__setattr__(self, "label", label)

    @property
    def start(self) -> complex:
        return self.points[0]

    @property
    def end(self) -> complex:
        return self.points[-1]

    @property
    def is_closed(self) -> bool:
        return abs(self.start - self.end) <= 1e-12

    @property
    def segments(self) -> tuple[PathSegment, ...]:
        return tuple(PathSegment(a, b) for a, b in zip(self.points[:-1], self.points[1:]))

    @property
    def length(self) -> float:
        return sum(seg.length for seg in self.segments)

    def crosses(self, point: complex | float | int, *, tol: float = 1e-12) -> bool:
        return any(seg.crosses(point, tol=tol) for seg in self.segments)

    def reversed(self) -> "ContinuationPath":
        label = f"reverse({self.label})" if self.label else "reverse"
        return ContinuationPath(reversed(self.points), label=label)

    def winding_number(self, point: complex | float | int = 0j, *, require_closed: bool = True) -> int:
        return winding_number(self, point, require_closed=require_closed)

    def summary(self) -> str:
        name = self.label or "path"
        return f"{name}: {len(self.points)} points, closed={self.is_closed}, length={self.length:g}"


def circle_path(
    *,
    center: complex | float | int = 0j,
    radius: float = 1.0,
    turns: int = 1,
    samples_per_turn: int = 64,
    start_angle: float = 0.0,
    label: str = "circle",
) -> ContinuationPath:
    """Return a sampled circular continuation path."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    if samples_per_turn < 4:
        raise ValueError("samples_per_turn must be at least 4")
    c = _as_complex(center)
    n = abs(turns) * samples_per_turn
    sign = 1 if turns >= 0 else -1
    pts = []
    for j in range(n + 1):
        theta = start_angle + sign * TAU * abs(turns) * j / n
        pts.append(c + radius * complex(math.cos(theta), math.sin(theta)))
    return ContinuationPath(pts, label=label)


def winding_number(path: ContinuationPath, point: complex | float | int = 0j, *, require_closed: bool = True) -> int:
    """Compute the integer winding number of a path about ``point``.

    The implementation sums unwrapped argument changes of ``z-point`` along
    consecutive line segments.  It is intended for piecewise-linear diagnostic
    paths that do not pass through the branch point.
    """
    p = _as_complex(point)
    if require_closed and not path.is_closed:
        raise ContinuationPathError("winding number is only integer-valued for closed paths")
    if path.crosses(p):
        raise ContinuationPathError("path crosses the branch point; winding is undefined")
    total = 0.0
    for a, b in zip(path.points[:-1], path.points[1:]):
        za = a - p
        zb = b - p
        if abs(za) <= 1e-15 or abs(zb) <= 1e-15:
            raise ContinuationPathError("path endpoint lies on the branch point")
        da = cmath.phase(zb) - cmath.phase(za)
        while da <= -math.pi:
            da += TAU
        while da > math.pi:
            da -= TAU
        total += da
    return _canonical_int(total / TAU)


def winding_events(path: ContinuationPath, branch_points: Sequence[BranchPoint] | None = None) -> tuple[WindingEvent, ...]:
    """Return nonzero winding events around the supplied branch points."""
    bps = tuple(branch_points or (BranchPoint(0j, kind="log", label="0"),))
    events: list[WindingEvent] = []
    for bp in bps:
        w = winding_number(path, bp.location)
        if w:
            events.append(WindingEvent(bp, w))
    return tuple(events)


def update_branch_state_along_path(
    state: BranchState | None,
    path: ContinuationPath,
    branch_points: Sequence[BranchPoint] | None = None,
) -> BranchState:
    """Update local branch-state labels from path winding events.

    Current conservative rules:
    - log branch increments by winding around a log branch point;
    - sqrt branch changes parity after each winding around a sqrt branch point;
    - power branch increments by winding around a pow branch point;
    - total winding accumulates all nonzero events.
    """
    s = state or DEFAULT_BRANCH_STATE
    log_branch = s.log_branch
    sqrt_branch = s.sqrt_branch
    pow_branch = s.pow_branch
    total_winding = s.winding
    for event in winding_events(path, branch_points):
        kind = event.kind.lower()
        w = event.winding
        total_winding += w
        if kind in {"log", "logarithm"}:
            log_branch += w
        elif kind in {"sqrt", "square-root", "square_root"}:
            sqrt_branch = (sqrt_branch + w) % 2
        elif kind in {"pow", "power"}:
            pow_branch += w
        elif kind == "all":
            log_branch += w
            sqrt_branch = (sqrt_branch + w) % 2
            pow_branch += w
        else:
            # Unknown branch-point kinds still contribute to path history.
            pass
    return BranchState(log_branch, sqrt_branch, pow_branch, total_winding)


def continue_log(z: complex | float | int, path: ContinuationPath, state: BranchState | None = None) -> complex:
    """Evaluate a log value after conservative path-induced branch update."""
    new_state = update_branch_state_along_path(state, path, [BranchPoint(0j, kind="log", label="0")])
    return cmath.log(_as_complex(z)) + (TAU * new_state.log_branch) * 1j


def continue_sqrt(z: complex | float | int, path: ContinuationPath, state: BranchState | None = None) -> complex:
    """Evaluate a square-root value after conservative path-induced branch update."""
    new_state = update_branch_state_along_path(state, path, [BranchPoint(0j, kind="sqrt", label="0")])
    value = cmath.sqrt(_as_complex(z))
    return -value if new_state.sqrt_branch % 2 else value


def path_history_note(path: ContinuationPath, events: Sequence[WindingEvent] | None = None) -> str:
    """Compact human-readable note for embedding in CNRS-H jets."""
    ev = tuple(events or ())
    if not ev:
        return f"continued along {path.label or 'path'}; no nonzero winding events"
    return f"continued along {path.label or 'path'}; " + "; ".join(e.summary() for e in ev)


__all__ = [
    "ContinuationPathError",
    "PathSegment",
    "BranchPoint",
    "WindingEvent",
    "ContinuationPath",
    "circle_path",
    "winding_number",
    "winding_events",
    "update_branch_state_along_path",
    "continue_log",
    "continue_sqrt",
    "path_history_note",
]
