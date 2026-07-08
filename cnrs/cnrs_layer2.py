"""
cnrs_layer2.py
--------------
Layer-2 representation: (CNRS-A digit string, integer branch index).

This is a minimal but coherent Layer-2 abstraction:

  - A Layer2 value is (z_str, k) where:
        z_str : CNRS-A digit string (Layer-1 value)
        k     : integer branch index (Layer-2 sheet)

  - Arithmetic is defined as:
        add: (z1, k1) + (z2, k2) = (z1+z2, 0)      [branch reset]
        sub: (z1, k1) - (z2, k2) = (z1-z2, 0)      [branch reset, via a+(-b)]
        mul: (z1, k1) * (z2, k2) = (z1*z2, k1+k2)  [branch accumulation]

    This matches the proved result in CNRS_problem2_capstone_v8.tex,
    Proposition "Properties of (X~, +)" part (iv): addition resets the
    branch index to k=0 regardless of k1, k2. Multiplication's branch
    accumulation (k1+k2) is separately established (log-sheet winding
    numbers add under multiplication) and is unaffected by this fix.

FIXED (this update, Thread 19 downstream check): earlier versions of
this module used k1+k2 for addition (and k1-k2 for subtraction), which
did not match the proved capstone result. This was a real correctness
bug against the formal record, not a notation choice. Downstream
callers checked: cnrs_layer2_value.py (L2Val, has its own independent
__add__/__sub__ delegating to or duplicating this logic -- also fixed),
cnrs_layer3.py (does not call Layer2.__add__/__sub__; shift_branch()
does an explicit k+dk shift, unaffected), cnrs_continuation.py (imports
Layer2 but does not use it), cnrs_verify.py (test_layer2() asserted the
old k1+k2 rule for addition -- fixed to assert branch reset),
test_tc_equations.py (test_tc_ch18_layer2_addition_branch asserted the
old rule and mis-cited TC Ch.18 as its source when the actual source is
the P2 Capstone -- fixed and re-cited).

UNIFIED-STRING LAYOUT (Thread 19): this module's internal representation
remains the (z_str, k) pair -- changing the internal representation to a
true single string is a larger refactor than this update attempts. What
this update adds is read/write support for the external unified-string
text format defined in CNRS_branch_index_incorporation_v3.tex,
Version 3 layout:

    ...d2 d1 d0 | km...k1 k0 . e1 e2...

i.e. the integer part of z, the branch marker '|', the k-segment
(bounded between '|' and '.'), then the complex point '.' and the
fractional part of z. A transitional broken-bar marker '||' is used
when k is written in ordinary decimal rather than expanded in base
-2+i (which is the only form this implementation currently produces
for k, since k is stored as a plain Python int) -- see
to_unified_string() / from_unified_string() below.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from .cnrs_ops import cnrs_add, cnrs_mul
from .cnrs_repr import cnrs_to_gaussian, gaussian_to_cnrs_str, normalize_cnrs


@dataclass(frozen=True)
class Layer2:
    """
    Layer-2 value: (CNRS-A digit string, integer branch index).
    """
    z: str   # CNRS-A digit string (Layer-1)
    k: int   # branch index (Layer-2)

    # -----------------------------
    # Basic constructors
    # -----------------------------

    @staticmethod
    def from_gaussian(value: complex, k: int = 0) -> "Layer2":
        """
        Construct a Layer2 value from a Gaussian integer and branch index.
        """
        z_str = normalize_cnrs(gaussian_to_cnrs_str(value))
        return Layer2(z_str, int(k))

    def to_gaussian(self) -> complex:
        """
        Forget the branch index and return the Layer-1 Gaussian value.
        """
        return cnrs_to_gaussian(self.z)

    # -----------------------------
    # Arithmetic
    # -----------------------------

    def __add__(self, other: "Layer2") -> "Layer2":
        """
        Layer-2 addition.

        Convention (fixed to match the proved result): branch reset.
            (z1, k1) + (z2, k2) = (z1 + z2, 0)

        This matches CNRS_problem2_capstone_v8.tex, Definition "Canonical
        addition in X~" and Proposition "Properties of (X~, +)" part (iv)
        ("branch reset"): the sum of two extended elements always lands on
        the principal sheet k=0, regardless of k1 and k2. Earlier versions
        of this module used k1+k2 for addition, which does not match the
        proved result; this was a real correctness bug, not a notation
        choice, and is corrected here (Thread 19 downstream check).
        """
        z_sum = cnrs_add(self.z, other.z)
        return Layer2(z_sum, 0)

    def __sub__(self, other: "Layer2") -> "Layer2":
        """
        Layer-2 subtraction via addition and negation.

        Convention (fixed for consistency with the corrected __add__):
        subtraction is defined as a + (-b), and negation does not touch
        the branch index (it is a unary operation on the value alone).
        Applying the proved branch-reset addition rule to a + (-b) gives
        k=0 for the result, by direct substitution -- this is not an
        independent assumption beyond the capstone's addition definition.
        The capstone itself does not separately state a subtraction rule;
        if Don wants a different convention (e.g. subtraction preserves
        k1-k2, treating it as distinct from a+(-b)), that needs its own
        proved definition first.
        """
        z_diff = cnrs_add(self.z, gaussian_to_cnrs_str(-cnrs_to_gaussian(other.z)))
        return Layer2(normalize_cnrs(z_diff), 0)

    def __mul__(self, other: "Layer2") -> "Layer2":
        """
        Layer-2 multiplication.

        Current convention:
            (z1, k1) * (z2, k2) = (z1 * z2, k1 + k2)

        This matches a simple log-sheet intuition:
            log(c1) ~ log|c1| + i(arg c1 + 2π k1)
            log(c2) ~ log|c2| + i(arg c2 + 2π k2)
            log(c1 c2) ~ log(c1) + log(c2)  ⇒ branch indices add.
        """
        z_prod = cnrs_mul(self.z, other.z)
        k_prod = self.k + other.k
        return Layer2(z_prod, k_prod)

    # -----------------------------
    # Pretty printing
    # -----------------------------

    def __str__(self) -> str:
        return f"{self.z} @ {self.k}"

    def __repr__(self) -> str:
        return f"Layer2(z={self.z!r}, k={self.k})"

    # -----------------------------
    # Unified-string format (Thread 19, Version 3 layout)
    # -----------------------------

    def to_unified_string(self, expand_k: bool = False) -> str:
        """
        Render this Layer2 value as a unified branch-marker string,
        per CNRS_branch_index_incorporation_v3.tex:

            ...d2 d1 d0 | km...k1 k0 . e1 e2...

        By default (expand_k=False) the k-segment is written in ordinary
        decimal and the transitional broken-bar marker '||' is used, since
        this implementation stores k as a plain int and has not yet
        committed to a canonical base-(-2+i) expansion convention for
        negative k (the (F) property guarantees existence, but the
        existing sign convention has not been cross-checked against this
        module's own gaussian_to_cnrs_str for negative integers).

        If expand_k=True, k is expanded in base -2+i via
        gaussian_to_cnrs_str (since k in Z is a Gaussian integer) and the
        single-bar marker '|' is used. This path is offered for forward
        compatibility with the long-term target form but has not been
        independently verified against the branch-index paper's worked
        examples (c=3+4i, k=1 and k=-5) -- do not treat expand_k=True
        output as canonical without that check.
        """
        if "." in self.z:
            int_part, frac_part = self.z.split(".")
        else:
            int_part, frac_part = self.z, ""

        if expand_k:
            k_str = gaussian_to_cnrs_str(complex(self.k, 0))
            marker = "|"
        else:
            k_str = str(self.k)
            marker = "||"

        if frac_part:
            return f"{int_part}{marker}{k_str}.{frac_part}"
        else:
            return f"{int_part}{marker}{k_str}"

    @staticmethod
    def from_unified_string(s: str) -> "Layer2":
        """
        Parse a unified branch-marker string back into a Layer2 value.

        Accepts both the single-bar '|' form (k expanded in base -2+i)
        and the transitional broken-bar '||' form (k in decimal). The
        marker actually present in the string determines how the
        k-segment is interpreted -- this is the point of having two
        distinct marker symbols rather than one (see Remark on the
        transitional broken-bar marker, branch-index-incorporation v3).

        Raises ValueError if no recognized marker is present, or if the
        string does not contain exactly one marker.
        """
        if "||" in s:
            marker = "||"
            expand_k = False
        elif "|" in s:
            marker = "|"
            expand_k = True
        else:
            raise ValueError(
                f"No branch marker ('|' or '||') found in unified string: {s!r}"
            )

        if s.count(marker) != 1:
            raise ValueError(
                f"Expected exactly one '{marker}' marker in unified string: {s!r}"
            )

        int_part, rest = s.split(marker, 1)

        if "." in rest:
            k_part, frac_part = rest.split(".", 1)
        else:
            k_part, frac_part = rest, ""

        if expand_k:
            k_val = cnrs_to_gaussian(k_part)
            if abs(k_val.imag) > 1e-9:
                raise ValueError(
                    f"k-segment {k_part!r} did not decode to a real integer "
                    f"(got {k_val!r}); the unified string is malformed."
                )
            k = int(round(k_val.real))
        else:
            k = int(k_part)

        z_str = f"{int_part}.{frac_part}" if frac_part else int_part
        z_str = normalize_cnrs(z_str)

        return Layer2(z_str, k)


# Convenience constructors / helpers

def make_layer2(z_str: str, k: int = 0) -> Layer2:
    """
    Build a Layer2 value directly from a CNRS-A string and branch index.
    """
    return Layer2(normalize_cnrs(z_str), int(k))


def layer2_from_complex(c: complex, k: int = 0) -> Layer2:
    """
    Build a Layer2 value from a complex/Gaussian value and branch index.
    """
    return Layer2.from_gaussian(c, k)
