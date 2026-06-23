"""
cnrs.formal_state
=================

Small formal CNRS* state object corresponding to the theoretical architecture.

This module is deliberately lightweight.  It gives the toolkit a code-level
object matching the paper-level tuple

    S = (a, k, h, x0, N, Omega)

where ``a`` is a CNRS-A value, ``k`` is branch/winding state metadata, ``h`` is
a CNRS-H-native coefficient jet, ``x0`` is the expansion centre, ``N`` is the
truncation order, and ``Omega`` records local-domain metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .cnrs_value import CVal
from .cnrs_h_native import CnrsHNative


@dataclass(frozen=True)
class CnrsFormalState:
    """Formal CNRS* state for theorem-aligned toolkit workflows."""

    value: CVal
    coefficients: CnrsHNative
    branch_state: Any = 0
    center: complex | float | int = 0
    order: int | None = None
    domain: Any = None
    status: str = "finite_local_cnrs_star_state"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.value, CVal):
            raise TypeError("value must be a CVal")
        if not isinstance(self.coefficients, CnrsHNative):
            raise TypeError("coefficients must be a CnrsHNative")
        if self.order is None:
            object.__setattr__(self, "order", max(0, self.coefficients.length - 1))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @classmethod
    def from_gaussian_coefficients(
        cls,
        value: complex | int,
        coeffs,
        *,
        branch_state: Any = 0,
        center: complex | float | int = 0,
        domain: Any = None,
        status: str = "finite_local_cnrs_star_state",
        metadata: Mapping[str, Any] | None = None,
    ) -> "CnrsFormalState":
        return cls(
            value=CVal.from_gaussian(complex(value)),
            coefficients=CnrsHNative.from_gaussian_list(coeffs),
            branch_state=branch_state,
            center=center,
            domain=domain,
            status=status,
            metadata=metadata or {},
        )

    @property
    def well_formed(self) -> bool:
        """Return True when the state carries the expected native components."""
        return isinstance(self.value, CVal) and isinstance(self.coefficients, CnrsHNative)

    def _operation_metadata(self, operation: str) -> dict[str, Any]:
        history = list(self.metadata.get("history", ()))
        history.append(operation)
        return {**self.metadata, "operation": operation, "history": tuple(history)}

    def with_coefficients(self, coefficients: CnrsHNative, *, operation: str) -> "CnrsFormalState":
        """Return a copy with replaced coefficients and preserved state metadata."""
        return CnrsFormalState(
            value=self.value,
            coefficients=coefficients,
            branch_state=self.branch_state,
            center=self.center,
            domain=self.domain,
            status=self.status,
            metadata=self._operation_metadata(operation),
        )

    def differentiate(self) -> "CnrsFormalState":
        return self.with_coefficients(self.coefficients.differentiate(), operation="differentiate")

    D = differentiate

    def integrate(self, constant: complex | int | CVal = 0) -> "CnrsFormalState":
        return self.with_coefficients(self.coefficients.integrate(constant), operation="integrate")

    def _merge_branch_state(self, other: "CnrsFormalState") -> Any:
        if self.branch_state == other.branch_state:
            return self.branch_state
        return (self.branch_state, other.branch_state)

    def _binary_state(self, other: "CnrsFormalState", *, operation: str, value: CVal, coefficients: CnrsHNative) -> "CnrsFormalState":
        if not isinstance(other, CnrsFormalState):
            return NotImplemented
        domain = self.domain if self.domain == other.domain else (self.domain, other.domain)
        center = self.center if self.center == other.center else (self.center, other.center)
        metadata = self._operation_metadata(operation)
        metadata["rhs_status"] = other.status
        return CnrsFormalState(
            value=value,
            coefficients=coefficients,
            branch_state=self._merge_branch_state(other),
            center=center,
            domain=domain,
            status=self.status,
            metadata=metadata,
        )

    def __add__(self, other: "CnrsFormalState") -> "CnrsFormalState":
        """CNRS* state addition: CVal addition plus CNRS-H coefficient addition."""
        if not isinstance(other, CnrsFormalState):
            return NotImplemented
        return self._binary_state(
            other,
            operation="add",
            value=self.value + other.value,
            coefficients=self.coefficients + other.coefficients,
        )

    def __mul__(self, other: "CnrsFormalState") -> "CnrsFormalState":
        """CNRS* state multiplication: CVal multiplication plus CNRS-H EGF product."""
        if not isinstance(other, CnrsFormalState):
            return NotImplemented
        return self._binary_state(
            other,
            operation="multiply",
            value=self.value * other.value,
            coefficients=self.coefficients * other.coefficients,
        )

    def preservation_report(self) -> dict[str, Any]:
        """Return status metadata for theorem-alignment tests and docs."""
        return {
            "well_formed": self.well_formed,
            "value_type": type(self.value).__name__,
            "coefficient_type": type(self.coefficients).__name__,
            "order": self.order,
            "status": self.status,
            "branch_state": self.branch_state,
        }

    def summary(self) -> str:
        return (
            f"CnrsFormalState(value={self.value!r}, branch={self.branch_state!r}, "
            f"center={self.center!r}, order={self.order}, domain={self.domain!r}, "
            f"status={self.status!r})"
        )


__all__ = ["CnrsFormalState"]
