"""
cnrs_layer3_ops.py
------------------
Operator algebra on Layer-3 analytic objects.

This module extends the operator calculus from cnrs_operator.py
to act directly on L3Value objects, not just HStreams.

Layer-3 operators can:
  - transform the HStream component
  - update the Layer-2 branch index
  - update the continuation rule
  - compose with other operators

This is the operator-analytic layer required for Problem 2 and Problem 4.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

from .cnrs_layer3 import L3Value
from .cnrs_operator import Operator
from .cnrs_hstream_ops import hstream_add
from .cnrs_hstream import HStream


@dataclass(frozen=True)
class L3Operator:
    """
    A Layer-3 operator.

    Components:
      - f_stream: transformation on the HStream
      - f_branch: transformation on the branch index k
      - name: optional label for debugging / display
    """
    f_stream: Callable[[HStream], HStream]
    f_branch: Callable[[int], int] = lambda k: k
    name: Optional[str] = None

    # -----------------------------
    # Application to L3Value
    # -----------------------------

    def __call__(self, v: L3Value) -> L3Value:
        """
        Apply the operator to a Layer-3 value.
        """
        new_stream = self.f_stream(v.stream)
        new_k = self.f_branch(v.l2.k)

        # Rebuild the Layer-2 component with updated branch index
        new_l2 = v.l2.shift_branch(new_k - v.l2.k)

        return L3Value(
            l2=new_l2,
            stream=new_stream,
            cont=v.cont,
            op=self
        )

    # -----------------------------
    # Operator algebra
    # -----------------------------

    def __matmul__(self, other: "L3Operator") -> "L3Operator":
        """
        Composition: (A @ B)(x) = A(B(x))
        """
        return L3Operator(
            f_stream=lambda s: self.f_stream(other.f_stream(s)),
            f_branch=lambda k: self.f_branch(other.f_branch(k)),
            name=f"({self.name}@{other.name})" if self.name and other.name else None
        )

    def __add__(self, other: "L3Operator") -> "L3Operator":
        """
        Pointwise operator addition on streams.
        Branch index is preserved.
        """
        return L3Operator(
            f_stream=lambda s: hstream_add(self.f_stream(s), other.f_stream(s)),
            f_branch=lambda k: k,
            name=f"({self.name}+{other.name})" if self.name and other.name else None
        )


# ---------------------------------------------------------------------------
# Predefined Layer-3 operators
# ---------------------------------------------------------------------------

# Identity operator
Id3 = L3Operator(
    f_stream=lambda s: s,
    f_branch=lambda k: k,
    name="Id3"
)

# Forward shift (multiply by Z0)
Shift3 = L3Operator(
    f_stream=lambda s: s.shift_left(1),
    f_branch=lambda k: k,
    name="Shift3"
)

# Backward shift (divide by Z0)
ShiftInv3 = L3Operator(
    f_stream=lambda s: s.shift_right(1),
    f_branch=lambda k: k,
    name="ShiftInv3"
)

# Branch increment operator
BranchUp = L3Operator(
    f_stream=lambda s: s,
    f_branch=lambda k: k + 1,
    name="BranchUp"
)

# Branch decrement operator
BranchDown = L3Operator(
    f_stream=lambda s: s,
    f_branch=lambda k: k - 1,
    name="BranchDown"
)
