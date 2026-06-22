# Symbolic Calculus Quickstart

The symbolic calculus layer provides a small expression-tree system for CNRS-oriented workflows. It supports symbolic differentiation, conservative rule-based symbolic integration, evaluation through `CnrsComplex`, and cross-checking through the `CnrsDual` autodiff layer.

## Basic symbolic differentiation

```python
from cnrs.symbolic import Var, exp, sin, diff

s = Var("s")
L = Var("L")
expr = sin(exp(s / L))
deriv = diff(expr, s).simplify()
print(deriv)
```

## Symbolic evaluation

```python
value = expr.eval({"s": 1.2, "L": 5.0}, L=20)
deriv_value = deriv.eval({"s": 1.2, "L": 5.0}, L=20)
```

## Conservative symbolic integration

```python
from cnrs.symbolic import integrate

A = Var("A")
k = Var("k")
scale_law = A * exp(k * s)
antideriv = integrate(scale_law, s).simplify()
print(antideriv)
```

Unsupported integrals remain explicit:

```python
integrate(exp(s * s), s)
```

returns an unevaluated `Integral` object rather than inventing a closed form.

## Cross-checking with autodiff

```python
from cnrs.autodiff import CnrsDual

dual_result = expr.eval({"s": CnrsDual.variable(1.2, L=20), "L": 5.0}, L=20)
print(dual_result.value)
print(dual_result.deriv)
```

This provides a useful regression check: evaluating `diff(expr, s)` numerically should agree with evaluating `expr` on a dual variable and reading the derivative component.


## Branch-aware symbolic expressions

v0.5.1 adds explicit local branch choices for logarithms, square roots, and branch-aware powers.

```python
from cnrs.symbolic import BranchState, Var, log, sqrt, pow_branch, diff

z = Var("z")
state = BranchState(log_branch=2, sqrt_branch=1, pow_branch=1)

expr = log(z, branch=2, branch_state=state)
root = sqrt(z, branch=1, branch_state=state)
power = pow_branch(z, 0.5, branch=1, branch_state=state)

print(expr.eval({"z": -1}, L=20))
print(root.eval({"z": -1}, L=20))
print(diff(expr, z))
```

The derivative of `log_k(z)` is still locally `1/z` away from singularities and branch cuts; the branch affects the value and is retained as expression metadata. The simplifier is conservative and does not globally rewrite `log(exp(z))` or `sqrt(z*z)`.

## Scope

This is a minimal symbolic layer. It is not a full computer algebra system or a global analytic-continuation engine. The current goal is to support transparent CNRS chain-rule, differentiation, integration, explicit local branch choices, and scale-law workflows without unsafe simplification or overclaiming.


## v0.5.1 symbolic-to-CNRS-H bridge

The v0.5.1 release adds `cnrs.cnrs_h_bridge`, a conservative bridge from supported symbolic expressions to finite CNRS-H EGF coefficient representations.  It supports constants, polynomials, simple scale laws such as `A*exp(k*s)`, and `exp`/`sin`/`cos` of affine arguments.  Unsupported expressions raise `UnsupportedBridgeExpression`.


## v0.5.1 direct CNRS-H chain rule

The v0.5.1 release adds `cnrs.cnrs_h_chain`, which implements finite-order EGF-series composition and verifies the chain-rule identity directly in CNRS-H coefficient space:

```text
D(f ∘ g) = (Df ∘ g) * Dg
```

This layer is distinct from `CnrsDual` autodiff.  It uses CNRS-H digit-shift differentiation plus finite EGF composition.  It is intentionally truncated to a requested order and should be read as a computational coefficient-calculus implementation, not a full global analytic-continuation engine.
