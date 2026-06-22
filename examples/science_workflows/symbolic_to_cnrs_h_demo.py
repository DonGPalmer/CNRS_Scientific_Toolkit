"""Demonstrate the v0.5.0 symbolic-to-CNRS-H bridge."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.symbolic import Var, exp, sin, diff, integrate
from cnrs.cnrs_h_bridge import (
    cnrs_h_from_symbolic,
    compare_symbolic_and_cnrs_h_derivative,
    compare_symbolic_and_cnrs_h_integral,
)


def main() -> None:
    s = Var("s")
    A = Var("A")
    k = Var("k")

    scale_law = A * exp(k * s)
    env = {"A": 2.0, "k": 0.3}

    h = cnrs_h_from_symbolic(scale_law, "s", order=8, env=env)
    print("Symbolic expression:", scale_law)
    print("CNRS-H coefficients:", h)
    print("CNRS-H pretty:", h.pretty("s"))

    dcheck = compare_symbolic_and_cnrs_h_derivative(scale_law, "s", order=7, env=env)
    print("Derivative bridge check passed:", dcheck.passed, "max error:", dcheck.max_error)

    icheck = compare_symbolic_and_cnrs_h_integral(exp(k * s), "s", order=7, env={"k": 0.3})
    print("Integral bridge check passed:", icheck.passed, "max error:", icheck.max_error)

    oscillatory = sin(s / 5.0)
    oscillatory_h = cnrs_h_from_symbolic(oscillatory, "s", order=8)
    print("Oscillatory supported expression:", oscillatory)
    print("Oscillatory CNRS-H coefficients:", oscillatory_h)
    print("Value at s=0.2 from CNRS-H:", oscillatory_h.evaluate(0.2))


if __name__ == "__main__":
    main()
