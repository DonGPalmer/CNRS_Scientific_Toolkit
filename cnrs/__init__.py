"""
cnrs — Complex Numeric Representational System
===============================================

A Python implementation of the CNRS arithmetic and calculus framework.

Base:   z0 = -2 + i  (a Gaussian integer, N(z0) = 5)
Digits: D = {0, 1, 2, 3, 4}

The package is organised in three layers:

  Layer 1 — CNRS-A: arithmetic layer
    Finite digit-string representation of Gaussian integers.
    Addition via a 14-state finite-state transducer.
    Multiplication via Cauchy convolution + carry normalisation.
    Division, subtraction, and high-level operator wrappers.

  Layer 2 — CNRS-H: calculus layer
    EGF (exponential generating function) digit-string representation.
    Differentiation and integration are exact digit-shift operations.
    Operator calculus: shift operators, discrete derivative/integral.

  Layer 3 — Analytic continuation (partial)
    Full Gaussian rational representation in three cases:
      - Finite Z[i][1/z0] values (terminating expansion).
      - Pure z0-adic periodic rationals (denominator coprime to 5).
      - Laurent-periodic z0-adic rationals (denominator divisible by 5).
    Evaluate via CnrsRational.z0_adic_value() (fast float),
    CnrsRational.z0_adic_value_fractions() (fully exact: returns (Fraction, Fraction)),
    or CnrsRational.z0_adic_value_exact() (exact internally, returns complex).
    Long-period expansions require sufficiently large max_frac; exceeding it
    raises RuntimeError.
    CNRS floating-point arithmetic (CNRS-float, experimental).
    Branch-index (Layer-2) and global analytic (Layer-3/4) objects (prototype).

  Scientific toolkit (v0.3.0+)
    CnrsComplex: unified complex interface matching Python's built-in complex.
    Wraps CnrsFloat with arithmetic, measurement, and array utilities.

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
"""

# ── Layer 1: CNRS-A arithmetic ────────────────────────────────────────────────

from .cnrs_repr import (
    Z0, DIGITS,
    gaussian_to_cnrs_digits,
    gaussian_to_cnrs_str,
    cnrs_to_gaussian,
    normalize_cnrs,
)

from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs
from .cnrs_div import div_by_base_power, div_by_base, div_cnrs
from .cnrs_ops import cnrs_add, cnrs_sub, cnrs_mul, cnrs_neg, cnrs_eq
from .cnrs_value import CVal

# ── Layer 2: CNRS-H calculus ──────────────────────────────────────────────────

from .cnrs_h import CnrsH
from .cnrs_hstream import HStream
from .cnrs_operator import Operator

# ── Analytic continuation ─────────────────────────────────────────────────────

from .cnrs_expansion import InfiniteExpansion
from .cnrs_rational import CnrsRational, gaussian_rational_to_cnrs
from .cnrs_float import CnrsFloat

# ── Layer-2 / Layer-3 / Layer-4 objects ──────────────────────────────────────

from .cnrs_layer2 import Layer2
from .cnrs_layer2_value import L2Val
from .cnrs_layer3 import L3Value
from .cnrs_layer4 import L4Value, L4State

# ── Scientific toolkit ────────────────────────────────────────────────────────

from .cnrs_complex import CnrsComplex, encode_array, decode_array, to_numpy
from .cnrs_ode import cnrs_solve_linear, cnrs_solve_driven, cnrs_solve_second_order, OdeSolution

__all__ = [
    # Constants
    "Z0", "DIGITS",
    # Representation
    "gaussian_to_cnrs_digits", "gaussian_to_cnrs_str",
    "cnrs_to_gaussian", "normalize_cnrs",
    # Arithmetic
    "add_cnrs", "mul_cnrs", "div_by_base_power", "div_by_base", "div_cnrs",
    "cnrs_add", "cnrs_sub", "cnrs_mul", "cnrs_neg", "cnrs_eq",
    "CVal",
    # Calculus
    "CnrsH", "HStream", "Operator",
    # Analytic
    "InfiniteExpansion", "CnrsRational", "gaussian_rational_to_cnrs", "CnrsFloat",
    # Layered objects
    "Layer2", "L2Val", "L3Value", "L4Value", "L4State",
    # Scientific toolkit
    "CnrsComplex", "encode_array", "decode_array", "to_numpy",
    "cnrs_solve_linear", "cnrs_solve_driven", "cnrs_solve_second_order",
    "OdeSolution",
]
