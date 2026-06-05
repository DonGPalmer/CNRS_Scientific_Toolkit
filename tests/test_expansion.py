"""
tests/test_expansion.py
-----------------------
Pytest wrapper for InfiniteExpansion and CnrsRational verification suites.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cnrs.cnrs_expansion_verify import (
    test_e1_gaussian_integers,
    test_e2_convergence,
    test_e3_period_detection,
    test_e4_residual_correctness,
    test_e5_zero,
)
from cnrs.cnrs_rational_verify import (
    test_r1_gaussian_integers,
    test_r2_finite_fractions,
    test_r3_round_trip,
    test_r4_string_consistency,
    test_r5_arithmetic,
    test_r6_display,
    test_r7_boundary_cases,
)

def test_expansion_e1(): test_e1_gaussian_integers()
def test_expansion_e2(): test_e2_convergence()
def test_expansion_e3(): test_e3_period_detection()
def test_expansion_e4(): test_e4_residual_correctness()
def test_expansion_e5(): test_e5_zero()

def test_rational_r1(): test_r1_gaussian_integers()
def test_rational_r2(): test_r2_finite_fractions()
def test_rational_r3(): test_r3_round_trip()
def test_rational_r4(): test_r4_string_consistency()
def test_rational_r5(): test_r5_arithmetic()
def test_rational_r6(): test_r6_display()
def test_rational_r7(): test_r7_boundary_cases()
