"""Generalized, node-specific branch objects for CNRS symbolic continuation.

This module extends the original aggregate ``BranchDelta`` mechanism without
removing it. A :class:`BranchObject` binds one symbolic ``branch_key`` to:

* a multivalued operation kind (``log``, ``sqrt``, or ``pow``),
* one or more branch-locus points,
* its current sheet coordinate, and
* the monodromy rule used to update that coordinate.

For logarithms and powers the default state group is integer translation. For
square roots the default is parity in Z/2Z. The design is deliberately finite
and local; it is not yet a general fundamental-groupoid or arbitrary
permutation-monodromy engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from . import symbolic as sy
from .cnrs_h_path import ContinuationPath, winding_number


class GeneralizedBranchError(ValueError):
    """Raised for invalid generalized branch definitions or applications."""


def _normal_kind(kind: str) -> str:
    k = str(kind).lower().replace("_", "-")
    aliases = {
        "logarithm": "log",
        "square-root": "sqrt",
        "power": "pow",
    }
    k = aliases.get(k, k)
    if k not in {"log", "sqrt", "pow"}:
        raise GeneralizedBranchError(f"unsupported generalized branch kind: {kind!r}")
    return k


@dataclass(frozen=True)
class BranchObject:
    """Branch state attached to one stable symbolic node key.

    Parameters
    ----------
    key:
        Stable identifier stored on a symbolic ``Log``, ``Sqrt``, or ``Pow``
        node as ``branch_key``.
    kind:
        ``log``, ``sqrt``, or ``pow``.
    loci:
        Isolated branch points whose windings act on this node.
    state:
        Current branch coordinate. ``sqrt`` is reduced modulo ``modulus``.
    modulus:
        Optional cyclic modulus. Defaults to 2 for ``sqrt`` and to no modulus
        for ``log`` and ``pow``.
    label:
        Optional descriptive label.
    """

    key: str
    kind: str
    loci: tuple[complex, ...]
    state: int = 0
    modulus: int | None = None
    label: str = ""

    def __init__(
        self,
        key: str,
        kind: str,
        loci: Iterable[complex | float | int],
        state: int = 0,
        modulus: int | None = None,
        label: str = "",
    ) -> None:
        key_text = str(key).strip()
        if not key_text:
            raise GeneralizedBranchError("branch object key must be nonempty")
        k = _normal_kind(kind)
        pts = tuple(complex(z) for z in loci)
        if not pts:
            raise GeneralizedBranchError("branch object must have at least one locus")
        mod = 2 if modulus is None and k == "sqrt" else modulus
        if mod is not None and mod <= 0:
            raise GeneralizedBranchError("branch modulus must be positive")
        st = int(state)
        if mod is not None:
            st %= mod
        object.__setattr__(self, "key", key_text)
        object.__setattr__(self, "kind", k)
        object.__setattr__(self, "loci", pts)
        object.__setattr__(self, "state", st)
        object.__setattr__(self, "modulus", mod)
        object.__setattr__(self, "label", str(label))

    def winding_delta(self, path: ContinuationPath) -> int:
        """Sum path windings around all loci associated with this object."""
        return sum(winding_number(path, point) for point in self.loci)

    def shifted(self, delta: int) -> "BranchObject":
        """Return a copy with state updated by ``delta``."""
        state = self.state + int(delta)
        if self.modulus is not None:
            state %= self.modulus
        return BranchObject(
            self.key,
            self.kind,
            self.loci,
            state=state,
            modulus=self.modulus,
            label=self.label,
        )

    def continued(self, path: ContinuationPath) -> "BranchObject":
        return self.shifted(self.winding_delta(path))

    def summary(self) -> str:
        loci = ",".join(f"{z:g}" for z in self.loci)
        group = f"Z/{self.modulus}Z" if self.modulus is not None else "Z"
        return f"{self.key}:{self.kind} loci=[{loci}] state={self.state} group={group}"


@dataclass(frozen=True)
class BranchTransition:
    """Before/after record for one node-specific branch continuation."""

    before: BranchObject
    after: BranchObject
    winding_delta: int

    @property
    def changed(self) -> bool:
        return self.before.state != self.after.state

    def summary(self) -> str:
        return (
            f"{self.before.key}: winding={self.winding_delta:+d}, "
            f"state {self.before.state}->{self.after.state}"
        )


@dataclass(frozen=True)
class BranchRegistry:
    """Immutable collection of node-specific branch objects."""

    objects: tuple[BranchObject, ...]

    def __init__(self, objects: Iterable[BranchObject]) -> None:
        objs = tuple(objects)
        keys = [obj.key for obj in objs]
        if len(set(keys)) != len(keys):
            raise GeneralizedBranchError("branch object keys must be unique")
        object.__setattr__(self, "objects", objs)

    def by_key(self) -> dict[str, BranchObject]:
        return {obj.key: obj for obj in self.objects}

    def continue_along(self, path: ContinuationPath) -> tuple["BranchRegistry", tuple[BranchTransition, ...]]:
        transitions = []
        updated = []
        for obj in self.objects:
            delta = obj.winding_delta(path)
            new_obj = obj.shifted(delta)
            updated.append(new_obj)
            transitions.append(BranchTransition(obj, new_obj, delta))
        return BranchRegistry(updated), tuple(transitions)

    def summary(self) -> str:
        return "; ".join(obj.summary() for obj in self.objects) or "empty branch registry"


def _node_branch_value(node: sy.Expr, obj: BranchObject) -> int:
    base = int(getattr(node, "branch", 0))
    state = obj.state
    if obj.kind == "sqrt":
        return (base + state) % (obj.modulus or 2)
    return base + state


def _apply_registry(node: sy.Expr, objects: Mapping[str, BranchObject], *, strict: bool) -> sy.Expr:
    if isinstance(node, (sy.Const, sy.Var)):
        return node

    if isinstance(node, sy.Log):
        arg = _apply_registry(node.arg, objects, strict=strict)
        key = node.branch_key
        if key is None:
            return sy.Log(arg, branch=node.branch, branch_state=node.branch_state)
        obj = objects.get(key)
        if obj is None:
            if strict:
                raise GeneralizedBranchError(f"no branch object registered for key {key!r}")
            return sy.Log(arg, branch=node.branch, branch_state=node.branch_state, branch_key=key)
        if obj.kind != "log":
            raise GeneralizedBranchError(f"branch key {key!r} is {obj.kind}, not log")
        return sy.Log(arg, branch=_node_branch_value(node, obj), branch_key=key)

    if isinstance(node, sy.Sqrt):
        arg = _apply_registry(node.arg, objects, strict=strict)
        key = node.branch_key
        if key is None:
            return sy.Sqrt(arg, branch=node.branch, branch_state=node.branch_state)
        obj = objects.get(key)
        if obj is None:
            if strict:
                raise GeneralizedBranchError(f"no branch object registered for key {key!r}")
            return sy.Sqrt(arg, branch=node.branch, branch_state=node.branch_state, branch_key=key)
        if obj.kind != "sqrt":
            raise GeneralizedBranchError(f"branch key {key!r} is {obj.kind}, not sqrt")
        return sy.Sqrt(arg, branch=_node_branch_value(node, obj), branch_key=key)

    if isinstance(node, sy.Pow):
        left = _apply_registry(node.left, objects, strict=strict)
        right = _apply_registry(node.right, objects, strict=strict)
        key = node.branch_key
        if key is None:
            return sy.Pow(left, right, branch=node.branch, branch_state=node.branch_state)
        obj = objects.get(key)
        if obj is None:
            if strict:
                raise GeneralizedBranchError(f"no branch object registered for key {key!r}")
            return sy.Pow(left, right, branch=node.branch, branch_state=node.branch_state, branch_key=key)
        if obj.kind != "pow":
            raise GeneralizedBranchError(f"branch key {key!r} is {obj.kind}, not pow")
        return sy.Pow(left, right, branch=_node_branch_value(node, obj), branch_key=key)

    if isinstance(node, sy.Exp):
        return sy.Exp(_apply_registry(node.arg, objects, strict=strict))
    if isinstance(node, sy.Sin):
        return sy.Sin(_apply_registry(node.arg, objects, strict=strict))
    if isinstance(node, sy.Cos):
        return sy.Cos(_apply_registry(node.arg, objects, strict=strict))
    if isinstance(node, sy.Tan):
        return sy.Tan(_apply_registry(node.arg, objects, strict=strict))
    if isinstance(node, sy.Neg):
        return sy.Neg(_apply_registry(node.arg, objects, strict=strict))
    if isinstance(node, sy.Add):
        return sy.Add(_apply_registry(node.left, objects, strict=strict), _apply_registry(node.right, objects, strict=strict))
    if isinstance(node, sy.Sub):
        return sy.Sub(_apply_registry(node.left, objects, strict=strict), _apply_registry(node.right, objects, strict=strict))
    if isinstance(node, sy.Mul):
        return sy.Mul(_apply_registry(node.left, objects, strict=strict), _apply_registry(node.right, objects, strict=strict))
    if isinstance(node, sy.Div):
        return sy.Div(_apply_registry(node.left, objects, strict=strict), _apply_registry(node.right, objects, strict=strict))
    if isinstance(node, sy.Integral):
        return sy.Integral(_apply_registry(node.integrand, objects, strict=strict), node.var)
    raise GeneralizedBranchError(f"unsupported symbolic node: {type(node).__name__}")


def apply_branch_registry(expr: Any, registry: BranchRegistry, *, strict: bool = True) -> sy.Expr:
    """Apply node-specific branch states to a symbolic expression."""
    return _apply_registry(sy.sympify(expr), registry.by_key(), strict=strict).simplify()


@dataclass(frozen=True)
class GeneralizedContinuationResult:
    original_expr: sy.Expr
    continued_expr: sy.Expr
    original_registry: BranchRegistry
    continued_registry: BranchRegistry
    transitions: tuple[BranchTransition, ...]
    path: ContinuationPath

    @property
    def changed_keys(self) -> tuple[str, ...]:
        return tuple(t.before.key for t in self.transitions if t.changed)

    def summary(self) -> str:
        changes = "; ".join(t.summary() for t in self.transitions) or "no branch objects"
        return f"continued along {self.path.label or 'path'}; {changes}"


def continue_symbolic_with_registry(
    expr: Any,
    path: ContinuationPath,
    registry: BranchRegistry,
    *,
    strict: bool = True,
) -> GeneralizedContinuationResult:
    """Continue a keyed symbolic expression using node-specific branch objects."""
    original = sy.sympify(expr)
    updated_registry, transitions = registry.continue_along(path)
    continued = apply_branch_registry(original, updated_registry, strict=strict)
    return GeneralizedContinuationResult(
        original,
        continued,
        registry,
        updated_registry,
        transitions,
        path,
    )


__all__ = [
    "GeneralizedBranchError",
    "BranchObject",
    "BranchTransition",
    "BranchRegistry",
    "GeneralizedContinuationResult",
    "apply_branch_registry",
    "continue_symbolic_with_registry",
]
