"""
examples/demo.py
----------------
A walkthrough of the stable CNRS arithmetic and calculus layers.

Run with:
    python examples/demo.py

This script requires no dependencies beyond the cnrs package itself.

Scope
-----
This demo covers the stable layers only:
  1. CNRS-A representation of Gaussian integers
  2. Addition via 14-state transducer
  3. Multiplication via convolution + carry normalisation
  4. CNRS-H digit-shift calculus (differentiation, integration, Euler's formula)

For approximate representation of general complex values (including
Gaussian rationals like 1/2), see CnrsFloat in cnrs_float.py.
General Gaussian rational periodic expansion is not yet implemented;
see README.md § Known limitations.
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cnrs

SEP = "-" * 60

# ── 1. Representation ─────────────────────────────────────────────────────────

print(SEP)
print("1. CNRS-A Representation  [stable]")
print(SEP)
print(f"   Base:   z0 = {cnrs.Z0}")
print(f"   Digits: D  = {cnrs.DIGITS}")
print()

examples = [0+0j, 1+0j, 1j, -1+0j, 3+2j, -5+7j, 12-3j]
for z in examples:
    s = cnrs.gaussian_to_cnrs_str(z)
    back = cnrs.cnrs_to_gaussian(s)
    ok = abs(back - z) < 1e-9
    print(f"   {z:>10}  ->  {s:>10}  ->  {back}  {'OK' if ok else 'FAIL'}")

# ── 2. Addition ───────────────────────────────────────────────────────────────

print()
print(SEP)
print("2. CNRS-A Addition  [stable — 14-state transducer]")
print(SEP)

pairs = [(3+2j, 1+1j), (7-4j, -3+5j), (12+0j, -12+0j)]
for a, b in pairs:
    sa = cnrs.gaussian_to_cnrs_str(a)
    sb = cnrs.gaussian_to_cnrs_str(b)
    sc = cnrs.cnrs_add(sa, sb)
    result = cnrs.cnrs_to_gaussian(sc)
    ok = abs(result - (a+b)) < 1e-9
    print(f"   ({a}) + ({b})  =  {result}  [expected {a+b}]  {'OK' if ok else 'FAIL'}")

# ── 3. Multiplication ─────────────────────────────────────────────────────────

print()
print(SEP)
print("3. CNRS-A Multiplication  [stable — convolution + carry normalisation]")
print(SEP)

pairs = [(3+2j, 1+1j), (2+1j, 2+1j), (4-3j, 1+2j)]
for a, b in pairs:
    sa = cnrs.gaussian_to_cnrs_str(a)
    sb = cnrs.gaussian_to_cnrs_str(b)
    sc = cnrs.cnrs_mul(sa, sb)
    result = cnrs.cnrs_to_gaussian(sc)
    ok = abs(result - a*b) < 1e-9
    print(f"   ({a}) * ({b})  =  {result}  [expected {a*b}]  {'OK' if ok else 'FAIL'}")

# ── 4. CNRS-H digit-shift calculus ────────────────────────────────────────────

print()
print(SEP)
print("4. CNRS-H Digit-Shift Calculus  [stable]")
print(SEP)
print("   Place values: d_n * rho^n / n!")
print("   Differentiation = drop leading digit (exact, no approximation)")
print("   Integration     = prepend constant digit")
print()

# f(rho) = 1 + rho + rho^2/2! + rho^3/3!  (truncated exp)
f = cnrs.CnrsH((1, 1, 1, 1))
print(f"   f  = CnrsH{f.coeffs}   (truncated e^rho, 4 terms)")
print(f"   f(1.0) = {f.evaluate(1.0).real:.6f}   [e = 2.718282...]")

df = f.differentiate()
print(f"   Df = CnrsH{df.coeffs}      (digit-shift: drop leading coefficient)")
print(f"   Df(1.0) = {df.evaluate(1.0).real:.6f}")

intf = f.integrate(constant=0)
print(f"   If = CnrsH{intf.coeffs}  (digit-shift: prepend 0)")
print(f"   If(1.0) = {intf.evaluate(1.0).real:.6f}   [integral of e^rho from 0 to 1 ≈ 1.718...]")

# Fundamental theorem: D(I(f)) == f
reconstructed = intf.differentiate()
ftc_ok = all(abs(reconstructed.coeff(k) - f.coeff(k)) < 1e-12
             for k in range(f.length))
print(f"   D(I(f)) == f: {ftc_ok}")

print()
print("   Euler's formula: e^(i*pi) + 1")
n_terms = 20
coeffs = tuple(1j**k for k in range(n_terms))
exp_i = cnrs.CnrsH(coeffs)
val = exp_i.evaluate(math.pi)
print(f"   e^(i*pi) + 1 = {val + 1:.2e}   (should be ~0, {n_terms} terms)")

# ── 5. Z[i][1/z0] fractions (exact, stable) ──────────────────────────────────

print()
print(SEP)
print("5. Exact Z[i][1/z0] Fractions  [stable]")
print(SEP)
print("   These are values p/z0^k for p in Z[i] — finitely representable.")
print()

from cnrs.cnrs_rational import gaussian_rational_to_cnrs

# 1/z0 = (-2-i)/5: exact finite expansion
r = gaussian_rational_to_cnrs(-2-1j, 5)
val = r.evaluate(10)
print(f"   1/z0 = (-2-i)/5:")
print(f"     CNRS string: {r.to_str()}")
print(f"     is_finite:   {r.is_finite}")
print(f"     value:       {val:.6f}   [exact: {(-2-1j)/5:.6f}]")

from cnrs.cnrs_float import encode, decode
print()
print("   For general complex values, use CnrsFloat (approximate):")
cf = encode(0.5 + 0j, L=8)
print(f"   encode(0.5, L=8) -> {cf}")
print(f"   decoded: {decode(cf):.6f}   [target: 0.5]")

# ── 6. Gaussian rational expansion (z0-adic and Laurent-periodic) ─────────────

print()
print(SEP)
print("6. Gaussian Rational Expansion  [experimental]")
print(SEP)
print("   Three cases: finite Z[i][1/z0], pure z0-adic periodic, Laurent-periodic.")
print("   Values are assigned by the rational closed form S = block + z0^T * S,")
print("   not by ordinary complex convergence (|z0| = sqrt(5) > 1).")
print()

from fractions import Fraction

# Case 2: gcd(q, 5) = 1 — pure z0-adic periodic
r = gaussian_rational_to_cnrs(1, 2, max_frac=50)
re_f, im_f = r.z0_adic_value_fractions()
print(f"   1/2  [pure z0-adic, period {r.period_length}]:")
print(f"     digits: {r.frac_digits[:r.period_start]}[{r.frac_digits[r.period_start:]}]")
print(f"     exact value (Fraction): {re_f} + {im_f}*i")
print(f"     matches 1/2: {re_f == Fraction(1, 2)}")

print()

# Case 2: 1/3
r3 = gaussian_rational_to_cnrs(1, 3, max_frac=50)
re3, im3 = r3.z0_adic_value_fractions()
print(f"   1/3  [pure z0-adic, period {r3.period_length}]:")
print(f"     digits: [{r3.frac_digits[r3.period_start:]}]  (period, starts at pos {r3.period_start})")
print(f"     exact value (Fraction): {re3} + {im3}*i")
print(f"     matches 1/3: {re3 == Fraction(1, 3)}")

print()

# Case 3: gcd(q, 5) > 1 — Laurent-periodic
r5 = gaussian_rational_to_cnrs(1, 5, max_frac=50)
re5, im5 = r5.z0_adic_value_fractions()
print(f"   1/5  [Laurent-periodic, power_offset={r5.power_offset}, period {r5.period_length}]:")
pre5 = r5.frac_digits[:r5.period_start] if r5.period_start else []
per5 = r5.frac_digits[r5.period_start:] if r5.period_start is not None else r5.frac_digits
print(f"     digits: z0^{r5.power_offset} * {pre5}[{per5}]")
print(f"     exact value (Fraction): {re5} + {im5}*i")
print(f"     matches 1/5: {re5 == Fraction(1, 5)}")

print()

# Long-period case
r23 = gaussian_rational_to_cnrs(1, 23, max_frac=1000)
re23, im23 = r23.z0_adic_value_fractions()
print(f"   1/23 [pure z0-adic, period {r23.period_length}  (long-period stress test)]:")
print(f"     period_start: {r23.period_start},  period_length: {r23.period_length}")
print(f"     exact value (Fraction): {re23}  [matches 1/23: {re23 == Fraction(1, 23)}]")
print(f"     (required max_frac=1000; default max_frac=200 would raise RuntimeError)")

print()
print(SEP)
print("All demonstrations complete.")
print(SEP)
