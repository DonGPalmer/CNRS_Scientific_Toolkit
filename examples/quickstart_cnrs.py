"""
quickstart_cnrs.py
==================

Minimal first-run example for the CNRS Scientific Toolkit.

This script is a compact research-code demonstration. It shows:
  1. CNRS-A representation and arithmetic;
  2. CNRS-H digit-shift calculus;
  3. scale-law evaluation;
  4. NumPy/SciPy interoperability helpers.

Run from the repository root:
    python examples/quickstart_cnrs.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import cnrs


def main() -> None:
    print("CNRS Scientific Toolkit quickstart")
    print("=" * 40)

    # 1. CNRS-A: finite complex-base representation.
    z = 3 + 2j
    s = cnrs.gaussian_to_cnrs_str(z)
    z_back = cnrs.cnrs_to_gaussian(s)
    print(f"CNRS-A representation: {z!r} -> {s!r} -> {z_back!r}")

    # Arithmetic through the public wrappers.
    a = cnrs.gaussian_to_cnrs_str(3 + 2j)
    b = cnrs.gaussian_to_cnrs_str(1 + 1j)
    c_add = cnrs.cnrs_add(a, b)
    c_mul = cnrs.cnrs_mul(a, b)
    print(f"CNRS-A add: {a} + {b} = {c_add}")
    print(f"CNRS-A mul: {a} * {b} = {c_mul}")

    # 2. CNRS-H: coefficient calculus.
    # f(rho) = 1 + 2*rho + 3*rho^2/2!
    f = cnrs.CnrsH.from_list([1.0, 2.0, 3.0])
    df = f.differentiate()
    integral = f.integrate(constant=0.0)
    rho = 0.25
    print(f"CNRS-H f({rho})  = {f(rho):.6g}")
    print(f"CNRS-H f'({rho}) = {df(rho):.6g}")
    print(f"CNRS-H integral coefficient length = {integral.length}")

    # 3. ScaleLaw: exact derivative through CNRS-H digit shift.
    law = cnrs.ScaleLaw.exponential(lam=-0.5, scale=2.0, terms=12)
    dlaw = law.derivative()
    s_vals = np.array([0.0, 0.5, 1.0])
    print("ScaleLaw values:", np.round(law(s_vals), 6))
    print("ScaleLaw derivative at s=0:", dlaw.evaluate(0.0))

    # 4. Interop: convert a CNRS-H object to NumPy samples.
    grid = np.linspace(0.0, 1.0, 5)
    samples = cnrs.cnrsh_to_numpy(f, grid)
    print("CNRS-H -> NumPy samples:", np.round(samples, 6))

    print("Quickstart complete.")


if __name__ == "__main__":
    main()
