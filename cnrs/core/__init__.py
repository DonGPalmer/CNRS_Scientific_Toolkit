"""CNRS-native core objects and arithmetic.

This package is the primary CNRS representation layer.  It re-exports the
stable digit/base/value/branch objects from the historical flat module layout
while v0.6.0 introduces an explicit native architecture.
"""

from .base import Z0, DIGITS
from .digits import (
    gaussian_to_cnrs_digits,
    gaussian_to_cnrs_str,
    cnrs_to_gaussian,
    normalize_cnrs,
)
from .value import CVal, CnrsValue
from .branch import BranchState, DEFAULT_BRANCH_STATE
from .arithmetic import (
    add_cnrs,
    mul_cnrs,
    div_cnrs,
    cnrs_add,
    cnrs_sub,
    cnrs_mul,
    cnrs_neg,
    cnrs_eq,
)

__all__ = [
    "Z0", "DIGITS",
    "gaussian_to_cnrs_digits", "gaussian_to_cnrs_str", "cnrs_to_gaussian", "normalize_cnrs",
    "CVal", "CnrsValue",
    "BranchState", "DEFAULT_BRANCH_STATE",
    "add_cnrs", "mul_cnrs", "div_cnrs", "cnrs_add", "cnrs_sub", "cnrs_mul", "cnrs_neg", "cnrs_eq",
]
