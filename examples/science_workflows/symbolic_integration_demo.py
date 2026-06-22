#!/usr/bin/env python3
"""
Conservative symbolic integration demo for CNRS Scientific Toolkit v0.4.2.

The symbolic integrator applies a small set of safe elementary rules and returns
an unevaluated Integral object when no rule applies.  Each supported example is
checked by differentiating the antiderivative.
"""
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.symbolic import Var, exp, sin, integrate, diff


def main() -> None:
    s = Var("s")
    k = Var("k")
    A = Var("A")

    examples = [
        ("constant", 5),
        ("power", s ** 3),
        ("reciprocal", 1 / s),
        ("scale law", A * exp(k * s)),
        ("sine affine", sin(2 * s + 1)),
        ("unsupported Gaussian", exp(s * s)),
    ]

    env = {"s": 1.2, "A": 2.0, "k": 0.3}
    print("CNRS symbolic integration demo")
    print("================================")
    for name, expr in examples:
        anti = integrate(expr, s).simplify()
        print(f"\n{name}")
        print(f"  expr:       {expr}")
        print(f"  integral:   {anti}")
        if name != "unsupported Gaussian":
            check = diff(anti, s).simplify().eval(env, L=20)
            print(f"  d/ds check: {complex(check):.12g}")
        else:
            print("  note:       no conservative elementary rule; returned unevaluated Integral")


if __name__ == "__main__":
    main()
