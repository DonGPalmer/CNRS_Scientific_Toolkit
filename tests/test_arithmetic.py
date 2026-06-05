"""
tests/test_arithmetic.py
------------------------
Pytest wrapper for CNRS-A arithmetic verification suite.

Covers representation, addition (14-state transducer),
multiplication (convolution + normalisation), and Layer-2 arithmetic.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cnrs.cnrs_verify import (
    test_representation_roundtrip,
    test_addition,
    test_multiplication,
    test_layer2,
)

def test_arith_representation(): test_representation_roundtrip()
def test_arith_addition():       test_addition()
def test_arith_multiplication(): test_multiplication()
def test_arith_layer2():         test_layer2()
