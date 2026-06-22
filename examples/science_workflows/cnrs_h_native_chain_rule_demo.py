"""Direct CNRS-H chain-rule demonstration.

This example does not use CnrsDual autodiff.  It works directly with CNRS-H
EGF coefficient strings and verifies the finite-order identity

    D(f o g) = (Df o g) * Dg.
"""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.cnrs_h_chain import exp_series, identity, monomial, compose_series, verify_chain_rule


def main() -> None:
    order = 10

    # f(x) = exp(x)
    f = exp_series(1, 0, order=order + 2)

    # g(s) = s^2
    g = monomial(2, 1, order=order + 2)

    composed = compose_series(f, g, order=order)
    comparison = verify_chain_rule(f, g, order=order)

    print("CNRS-H native chain-rule demo")
    print("f(x) = exp(x)")
    print("g(s) = s^2")
    print("f(g(s)) as CNRS-H:", composed.pretty("s"))
    print("D(f o g) left path :", comparison.lhs.pretty("s"))
    print("(Df o g)Dg right  :", comparison.rhs.pretty("s"))
    print("max coefficient error:", comparison.max_error)
    print("passed:", comparison.passed)

    # A polynomial example: f(x)=x^3+2x, g(s)=s-s^2.
    f_poly = monomial(3, 1, order=order + 2) + monomial(1, 2, order=order + 2)
    g_poly = identity(order + 2) + monomial(2, -1, order=order + 2)
    poly_cmp = verify_chain_rule(f_poly, g_poly, order=order)
    print("\nPolynomial check passed:", poly_cmp.passed)
    print("Polynomial max coefficient error:", poly_cmp.max_error)


if __name__ == "__main__":
    main()
