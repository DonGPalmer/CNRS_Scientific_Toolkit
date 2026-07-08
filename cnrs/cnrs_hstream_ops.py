"""
cnrs_hstream_ops.py
-------------------
Arithmetic operations on finite CNRS-H streams.

For now, we define addition and multiplication by:

  HStream -> CNRS-A string -> CNRS-A arithmetic -> HStream

This keeps semantics exact while we only work with finite prefixes.
"""

from __future__ import annotations
from .cnrs_hstream import HStream
from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs
from .cnrs_repr import normalize_cnrs


def hstream_add(a: HStream, b: HStream) -> HStream:
    """
    Add two finite H-streams via CNRS-A addition.
    """
    sa = a.to_str()
    sb = b.to_str()
    sc = normalize_cnrs(add_cnrs(sa, sb))
    return HStream.from_str(sc)


def hstream_mul(a: HStream, b: HStream) -> HStream:
    """
    Multiply two finite H-streams via CNRS-A multiplication.
    """
    sa = a.to_str()
    sb = b.to_str()
    sc = normalize_cnrs(mul_cnrs(sa, sb))
    return HStream.from_str(sc)
