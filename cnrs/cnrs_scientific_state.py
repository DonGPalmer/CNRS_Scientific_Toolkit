"""
cnrs.cnrs_scientific_state
==========================

CNRS-native scientific state object.

``CnrsScientificState`` is an integration object: it keeps a CNRS-H local jet
as the primary computational representation, while carrying the scientific
metadata needed for CNRS workflows -- source expression, expansion variable,
scale units, branch/path history, local domain, and optional observation maps.

The class is not intended to replace the lower-level CNRS-H calculus objects.
It gives scientific users a single explicit object that says what has been
represented, where it is local, what branch/path metadata it carries, and how
it is observed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from . import symbolic as sy
from .cnrs_h_jet import CnrsHJet, jet_from_symbolic
from .cnrs_h_taylor_model import CnrsHTaylorModel, taylor_model_from_jet, taylor_model_from_symbolic
from .cnrs_h_continuation import continued_jet_from_symbolic
from .cnrs_h_path import BranchPoint


class CnrsScientificStateError(ValueError):
    """Raised for invalid CNRS scientific-state operations."""


@dataclass(frozen=True)
class CnrsScientificState:
    """A CNRS-native local scientific object.

    Parameters
    ----------
    jet:
        Primary CNRS-H local jet representation.
    source_expr:
        Optional symbolic source expression.  When present, branch continuation
        can rebuild coefficients from the continued symbolic expression.
    var:
        Coordinate name.  Usually ``"s"`` for scale-coordinate workflows.
    scale_unit:
        Physical coordinate unit label.  Defaults to ``"nat"``.
    claim_status:
        Lightweight claim-status metadata, e.g. ``"finite_local_representation"``.
    provenance:
        Human-readable creation or workflow note.
    metadata:
        Additional user/workflow metadata.
    """

    jet: CnrsHJet
    source_expr: sy.Expr | None = None
    var: str = "s"
    scale_unit: str = "nat"
    claim_status: str = "finite_local_representation"
    provenance: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.jet, CnrsHJet):
            raise CnrsScientificStateError("jet must be a CnrsHJet")
        object.__setattr__(self, "var", self.var or self.jet.var)
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @classmethod
    def from_symbolic(
        cls,
        expr: Any,
        var: str | sy.Var = "s",
        *,
        center: complex | float | int = 0,
        order: int = 12,
        env: Mapping[str, Any] | None = None,
        scale_unit: str = "nat",
        claim_status: str = "finite_local_representation",
        provenance: str = "symbolic_to_cnrs_h_jet",
        metadata: Mapping[str, Any] | None = None,
    ) -> "CnrsScientificState":
        """Build a scientific state from a symbolic expression via CNRS-H jet coefficients."""
        e = sy.sympify(expr)
        jet = jet_from_symbolic(e, var, center=center, order=order, env=env, description=str(e))
        vname = var.name if isinstance(var, sy.Var) else str(var)
        return cls(
            jet,
            source_expr=e,
            var=vname,
            scale_unit=scale_unit,
            claim_status=claim_status,
            provenance=provenance,
            metadata=metadata or {},
        )

    @classmethod
    def from_jet(
        cls,
        jet: CnrsHJet,
        *,
        source_expr: Any | None = None,
        scale_unit: str = "nat",
        claim_status: str = "finite_local_representation",
        provenance: str = "cnrs_h_jet",
        metadata: Mapping[str, Any] | None = None,
    ) -> "CnrsScientificState":
        """Wrap an existing CNRS-H jet as a scientific state."""
        return cls(
            jet,
            source_expr=None if source_expr is None else sy.sympify(source_expr),
            var=jet.var,
            scale_unit=scale_unit,
            claim_status=claim_status,
            provenance=provenance,
            metadata=metadata or {},
        )

    @property
    def center(self) -> complex:
        return self.jet.center

    @property
    def order(self) -> int:
        return self.jet.order

    @property
    def branch_state(self):
        return self.jet.branch_state

    @property
    def domain(self):
        return self.jet.domain

    @property
    def path_history(self) -> tuple[str, ...]:
        return self.jet.path_history

    def evaluate(self, point: complex | float | int) -> complex:
        """Evaluate the finite CNRS-H local representation at ``point``."""
        return self.jet.evaluate(point)

    __call__ = evaluate

    def valid_for(self, point: complex | float | int, *, strict: bool = True) -> bool | None:
        return self.jet.valid_for(point, strict=strict)

    def observe(self, point_or_values: Any, map_name: str = "complex", **kwargs):
        """Evaluate/observe this state.

        If ``map_name`` is ``"complex"`` or ``"state"``, return the complex
        value(s) without reduction.  Otherwise apply one of the standard
        observation maps from ``cnrs.science.observation``.
        """
        key = map_name.lower().replace("-", "_")
        if hasattr(point_or_values, "__iter__") and not isinstance(point_or_values, (str, bytes, complex)):
            values = [self.evaluate(x) for x in point_or_values]
        else:
            values = self.evaluate(point_or_values)
        if key in {"complex", "state", "z", "raw"}:
            return values
        from .science.observation import observe as _observe
        return _observe(values, key, **kwargs)

    def observation_table(self, points: Any):
        values = [self.evaluate(x) for x in points]
        from .science.observation import observation_table as _observation_table
        return _observation_table(values, coord=points)

    def diff(self, *, order: int | None = None) -> "CnrsScientificState":
        expr = None if self.source_expr is None else sy.diff(self.source_expr, self.var).simplify()
        return CnrsScientificState(
            self.jet.diff(order=order),
            source_expr=expr,
            var=self.var,
            scale_unit=self.scale_unit,
            claim_status=self.claim_status,
            provenance=f"D({self.provenance or self.jet.description})",
            metadata={**self.metadata, "operation": "diff"},
        )

    differentiate = diff
    D = diff

    def integrate(self, constant: complex = 0, *, order: int | None = None) -> "CnrsScientificState":
        expr = None
        try:
            if self.source_expr is not None:
                expr = sy.integrate(self.source_expr, self.var).simplify()
        except Exception:
            expr = None
        return CnrsScientificState(
            self.jet.integrate(constant, order=order),
            source_expr=expr,
            var=self.var,
            scale_unit=self.scale_unit,
            claim_status=self.claim_status,
            provenance=f"Int({self.provenance or self.jet.description})",
            metadata={**self.metadata, "operation": "integrate"},
        )

    def continue_along(
        self,
        path,
        *,
        branch_points: list[BranchPoint] | tuple[BranchPoint, ...] | None = None,
        rebuild_coefficients: bool = True,
    ) -> "CnrsScientificState":
        """Continue the state along a path.

        When ``source_expr`` is available and ``rebuild_coefficients`` is true,
        use the v0.6.3 coefficient-active continuation path.  Otherwise preserve
        coefficients and update only branch/path metadata through the jet layer.
        """
        bps = tuple(branch_points or (BranchPoint(0j, kind="log", label="0"),))
        if rebuild_coefficients and self.source_expr is not None:
            result = continued_jet_from_symbolic(
                self.source_expr,
                self.var,
                center=self.center,
                order=self.order,
                path=path,
                branch_points=bps,
            )
            new_expr = result.continued_expr
            new_jet = result.continued_jet
            prov = f"continued({self.provenance or self.source_expr})"
            meta = {**self.metadata, "continuation": result.summary()}
        else:
            new_expr = self.source_expr
            new_jet = self.jet.continue_along(path, branch_points=bps)
            prov = f"continued_metadata({self.provenance or self.jet.description})"
            meta = {**self.metadata, "continuation": "metadata_only"}
        return CnrsScientificState(
            new_jet,
            source_expr=new_expr,
            var=self.var,
            scale_unit=self.scale_unit,
            claim_status=self.claim_status,
            provenance=prov,
            metadata=meta,
        )

    def to_taylor_model(
        self,
        *,
        sample_point: complex | float | int | None = None,
        remainder_bound: float | None = None,
    ) -> CnrsHTaylorModel:
        """Return a Taylor-model wrapper around the state's local jet."""
        return taylor_model_from_jet(
            self.jet,
            sample_point=sample_point,
            remainder_bound=remainder_bound,
            provenance=self.provenance or self.jet.description,
        )

    def summary(self) -> str:
        domain = "unknown" if self.domain is None else f"radius={self.domain.radius!r}, confidence={self.domain.confidence}, note={self.domain.note}"
        return (
            f"CnrsScientificState(var={self.var!r}, unit={self.scale_unit!r}, "
            f"center={self.center:g}, order={self.order}, "
            f"branch={self.branch_state}, domain={domain}, "
            f"status={self.claim_status!r})"
        )


def scientific_state_from_symbolic(*args, **kwargs) -> CnrsScientificState:
    """Convenience alias for ``CnrsScientificState.from_symbolic``."""
    return CnrsScientificState.from_symbolic(*args, **kwargs)


__all__ = [
    "CnrsScientificState",
    "CnrsScientificStateError",
    "scientific_state_from_symbolic",
]
