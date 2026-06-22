"""
cnrs.cnrs_formal_state
======================

Formal CNRS* state object for theory-aligned toolkit work.

A CNRS* state is intentionally lighter than ``CnrsScientificState``.  It is a
mathematical bookkeeping object that records the three core CNRS-native
components discussed in the main CNRS architecture paper:

    (a, k, h, center, order, domain)

where ``a`` is a CNRS-A value, ``k`` is explicit branch/path state, and ``h`` is
a CNRS-H coefficient object whose coefficients are stored as CNRS-A values.
The extra center/order/domain fields record finite local validity metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from .cnrs_value import CVal
from .cnrs_h_native import CnrsHNative, _ZERO_CVAL


class CnrsFormalStateError(ValueError):
    """Raised for invalid CNRS* formal state operations."""


@dataclass(frozen=True)
class BranchIndex:
    """Minimal explicit branch/path state.

    ``index`` records the integer branch/winding count used by branch-dependent
    functions.  ``kind`` is descriptive metadata, e.g. ``"log"`` or ``"sqrt"``.
    """

    index: int = 0
    kind: str = "generic"
    note: str = ""

    def shift(self, delta: int, *, note: str | None = None) -> "BranchIndex":
        return BranchIndex(self.index + int(delta), self.kind, self.note if note is None else note)


@dataclass(frozen=True)
class CnrsFormalState:
    """Theory-aligned CNRS* state.

    Parameters
    ----------
    value:
        CNRS-A value component.
    branch:
        Explicit branch/path component.
    jet:
        CNRS-H native coefficient component.
    center:
        Expansion center for local CNRS-H interpretation.
    order:
        Finite truncation order.  Defaults to ``jet.length - 1``.
    domain:
        Optional local validity/domain metadata.
    status:
        Theorem/status label.  Defaults to ``"finite_local_cnrs_state"``.
    """

    value: CVal
    branch: BranchIndex
    jet: CnrsHNative
    center: complex = 0j
    order: int | None = None
    domain: Any = None
    status: str = "finite_local_cnrs_state"

    def __post_init__(self) -> None:
        if not isinstance(self.value, CVal):
            raise CnrsFormalStateError("value must be a CVal")
        if not isinstance(self.branch, BranchIndex):
            raise CnrsFormalStateError("branch must be a BranchIndex")
        if not isinstance(self.jet, CnrsHNative):
            raise CnrsFormalStateError("jet must be a CnrsHNative")
        if self.order is None:
            object.__setattr__(self, "order", max(0, self.jet.length - 1))
        if self.order < 0:
            raise CnrsFormalStateError("order must be non-negative")

    @classmethod
    def from_gaussian_coeffs(
        cls,
        value: complex | int,
        coeffs,
        *,
        branch_index: int = 0,
        branch_kind: str = "generic",
        center: complex = 0j,
        order: int | None = None,
        domain: Any = None,
        status: str = "finite_local_cnrs_state",
    ) -> "CnrsFormalState":
        return cls(
            CVal.from_gaussian(complex(value)),
            BranchIndex(branch_index, branch_kind),
            CnrsHNative.from_gaussian_list(coeffs),
            center=center,
            order=order,
            domain=domain,
            status=status,
        )

    def differentiate(self) -> "CnrsFormalState":
        """Preserve value/branch metadata and differentiate the CNRS-H component."""
        return replace(self, jet=self.jet.differentiate(), order=max(0, self.jet.length - 2))

    D = differentiate

    def integrate(self, constant: complex | int | CVal = 0) -> "CnrsFormalState":
        """Preserve value/branch metadata and integrate the CNRS-H component."""
        return replace(self, jet=self.jet.integrate(constant), order=self.jet.length)

    def add_branch(self, delta: int, *, note: str | None = None) -> "CnrsFormalState":
        """Return a state with explicitly updated branch index."""
        return replace(self, branch=self.branch.shift(delta, note=note))

    def coefficient_strings(self) -> tuple[str, ...]:
        return tuple(c.s for c in self.jet.coeffs)

    def summary(self) -> str:
        return (
            f"CnrsFormalState(value={self.value.s!r}, branch={self.branch.index}, "
            f"kind={self.branch.kind!r}, center={self.center!r}, order={self.order}, "
            f"status={self.status!r})"
        )


__all__ = ["BranchIndex", "CnrsFormalState", "CnrsFormalStateError"]
