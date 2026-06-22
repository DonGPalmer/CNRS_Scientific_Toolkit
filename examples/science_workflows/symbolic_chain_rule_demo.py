"""
Minimal symbolic chain-rule demo for CNRS v0.4.1.

Run from repository root:
    python examples/science_workflows/symbolic_chain_rule_demo.py
"""
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.autodiff import CnrsDual
from cnrs.symbolic import Var, exp, sin, log, diff


def main():
    s = Var("s")
    L = Var("L")
    A = Var("A")
    k = Var("k")

    scale_law = A * exp(k * s)
    d_scale_law = diff(scale_law, s)

    nested = sin(exp(s / L)) + log(s * s + 2)
    d_nested = diff(nested, s)

    env = {"A": 2.0, "k": 0.3, "s": 4.0, "L": 5.0}
    print("Symbolic CNRS chain-rule demo")
    print("--------------------------------")
    print("scale law:       ", scale_law)
    print("d/ds scale law:  ", d_scale_law)
    print("value:           ", complex(scale_law.eval(env, L=20)))
    print("derivative:      ", complex(d_scale_law.eval(env, L=20)))
    print()
    print("nested expr:     ", nested)
    print("d/ds nested:     ", d_nested)
    print("nested value:    ", complex(nested.eval(env, L=20)))
    print("nested deriv:    ", complex(d_nested.eval(env, L=20)))

    # Cross-check symbolic derivative against the existing autodiff backend.
    dual_env = dict(env)
    dual_env["s"] = CnrsDual.variable(env["s"], L=20)
    dual_result = nested.eval(dual_env, L=20)
    print()
    print("autodiff deriv:  ", complex(dual_result.deriv))
    print("difference:      ", complex(d_nested.eval(env, L=20)) - complex(dual_result.deriv))


if __name__ == "__main__":
    main()
