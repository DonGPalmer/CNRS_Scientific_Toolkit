"""CNRS-H local expansion-point demo for v0.5.2.

This example shows a CNRS-H jet around a nonzero scale address.  The jet is a
finite local analytic representation in the variable u = s - s0.  Structural
differentiation and the chain rule are checked directly in coefficient space.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cnrs.symbolic import Var, exp, sin
from cnrs.cnrs_h_jet import jet_from_symbolic, verify_jet_chain_rule


def main() -> None:
    s = Var("s")
    x = Var("x")

    # A simple scale law expanded around cellular scale s0 ~= -12 nats.
    scale_center = -12.0
    k = 0.08
    law = exp(k * s)
    law_jet = jet_from_symbolic(law, s, center=scale_center, order=8, description="exp(k*s)")
    dlaw = law_jet.diff(order=8)

    print("CNRS-H local scale expansion")
    print("--------------------------------")
    print(f"center s0 = {scale_center} nats")
    print("coefficients f^(n)(s0):")
    print(law_jet.coeffs)
    print(f"f(s0)  = {law_jet.evaluate(scale_center):.12g}")
    print(f"f'(s0) = {dlaw.evaluate(scale_center):.12g}")
    print()

    # Direct local-jet chain rule at nonzero centers:
    # outer f(x)=sin(x) around x0=exp(0.5), inner g(s)=exp(s) around s0=0.5.
    inner_center = 0.5
    outer_center = math.exp(inner_center)
    outer = jet_from_symbolic(sin(x), x, center=outer_center, order=14, description="sin(x)")
    inner = jet_from_symbolic(exp(s), s, center=inner_center, order=14, description="exp(s)")
    cmp = verify_jet_chain_rule(outer, inner, order=10, atol=1e-8)

    print("Local-jet chain rule")
    print("--------------------")
    print("Identity: D(f o g) = (Df o g) * Dg")
    print(f"passed: {cmp.passed}")
    print(f"max coefficient error: {cmp.max_error:.3e}")
    test_s = 0.55
    print(f"evaluated derivative at s={test_s}: {cmp.lhs.evaluate(test_s):.12g}")
    print(f"analytic check: {math.cos(math.exp(test_s)) * math.exp(test_s):.12g}")


if __name__ == "__main__":
    main()
