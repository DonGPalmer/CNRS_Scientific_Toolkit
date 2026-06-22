"""
Chain-rule demonstration for CNRS autodiff.

Run from the repository root:

    python examples/science_workflows/chain_rule_scale_law.py

This example shows three first-order derivative calculations:

1. A basic nested function: exp(s^2)
2. A Scale Space style exponential law: A exp(k s)
3. A nested scale transformation: sin(exp(s/L))
"""

from pathlib import Path
import sys
import math
import cmath

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.autodiff import CnrsDual, exp, sin, derivative, value_and_derivative


def show(label, value, deriv, expected=None):
    print(f"\n{label}")
    print(f"  value      = {complex(value)}")
    print(f"  derivative = {complex(deriv)}")
    if expected is not None:
        print(f"  expected   = {expected}")
        print(f"  abs error  = {abs(complex(deriv) - expected):.3e}")


def main():
    # 1. Basic chain rule: d/ds exp(s^2) = 2s exp(s^2)
    s0 = 2.0
    value, deriv = value_and_derivative(lambda s: exp(s * s), s0, L=18)
    show("1) d/ds exp(s^2) at s=2", value, deriv, expected=2 * s0 * math.exp(s0 * s0))

    # 2. Scale-law derivative: y(s)=A exp(k s), y'=k A exp(k s)
    A = 2.0
    k = 0.3
    s0 = 4.0
    value, deriv = value_and_derivative(lambda s: A * exp(k * s), s0, L=18)
    expected_value = A * math.exp(k * s0)
    show("2) scale law y=A exp(k s) at s=4", value, deriv, expected=k * expected_value)

    # 3. Nested scale transformation: y(s)=sin(exp(s/L))
    Lscale = 5.0
    s0 = 1.2
    value, deriv = value_and_derivative(lambda s: sin(exp(s / Lscale)), s0, L=18)
    expected = cmath.cos(cmath.exp(s0 / Lscale)) * (1 / Lscale) * cmath.exp(s0 / Lscale)
    show("3) nested y=sin(exp(s/L)) at s=1.2, L=5", value, deriv, expected=expected)

    print("\nCNRS autodiff chain-rule demo complete.")


if __name__ == "__main__":
    main()
