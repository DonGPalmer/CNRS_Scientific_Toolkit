"""
tests/test_cnrs_h.py
--------------------
Pytest wrapper for CNRS-H calculus layer (8 algebraic properties).

  P1  Exact differentiation   P5  Linearity
  P2  Exact integration       P6  nth derivative
  P3  Fundamental Theorem     P7  EGF multiplication
  P4  Leibniz rule            P8  Scale input
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cnrs.cnrs_h_verify import (
    test_constructors,
    test_p1_differentiation,
    test_p2_integration,
    test_p3_ftc,
    test_p4_leibniz,
    test_p5_linearity,
    test_p6_nth_derivative,
    test_p7_egf_multiplication,
    test_p8_scale_input,
)

def test_h_constructors():       test_constructors()
def test_h_p1_differentiation(): test_p1_differentiation()
def test_h_p2_integration():     test_p2_integration()
def test_h_p3_ftc():             test_p3_ftc()
def test_h_p4_leibniz():         test_p4_leibniz()
def test_h_p5_linearity():       test_p5_linearity()
def test_h_p6_nth_derivative():  test_p6_nth_derivative()
def test_h_p7_egf_mul():         test_p7_egf_multiplication()
def test_h_p8_scale_input():     test_p8_scale_input()
