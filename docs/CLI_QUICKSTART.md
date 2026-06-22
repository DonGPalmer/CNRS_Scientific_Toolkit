# CNRS CLI Quickstart

The `cnrs` command is a lightweight interface for inspection, conversion, symbolic calculus, and demonstrations. It is not intended to replace the Python API; it is a convenient entry point for quick checks and reproducible examples.

Install the package in editable mode from the repository root:

```bash
python -m pip install -e .
```

Show the installed version:

```bash
cnrs version
```

Convert a Gaussian integer to a finite CNRS-A digit string:

```bash
cnrs convert "1+2j" --to cnrs
```

Convert a CNRS-A digit string back to a Gaussian integer:

```bash
cnrs convert "104" --from cnrs
```

Evaluate a symbolic expression:

```bash
cnrs eval "sin(exp(s/L))" --at s=1.2,L=5
```

Differentiate symbolically:

```bash
cnrs diff "sin(exp(s/L))" --var s
```

Differentiate and evaluate the derivative:

```bash
cnrs diff "sin(exp(s/L))" --var s --at s=1.2,L=5
```

Integrate using the conservative rule-based symbolic integrator:

```bash
cnrs integrate "A*exp(k*s)" --var s
```

List example scripts:

```bash
cnrs examples
```

Run the built-in demonstration:

```bash
cnrs demo
```

## Expression syntax

The parser accepts a small, safe Python-like expression language:

- operators: `+`, `-`, `*`, `/`, `**`
- functions: `exp`, `log`, `sin`, `cos`, `tan`, `sqrt`
- constants: `pi`, `e`, `i`, `j`
- assignments: `--at s=1.2,L=5,z=1+2i`

Unsupported expressions are rejected rather than evaluated through Python's general execution machinery.


## Branch-aware symbolic examples

```bash
cnrs eval "log(z, branch=2)" --at z=-1
cnrs eval "sqrt(z, branch=1)" --at z=-1
cnrs eval "pow_branch(z, 0.5, branch=1)" --at z=-1
cnrs diff "log(z, branch=2)" --var z
```

Branch arguments are explicit local branch tags. They are preserved by the symbolic expression layer, but they do not yet constitute full path-dependent analytic continuation.


## v0.5.1 symbolic-to-CNRS-H bridge

The v0.5.1 release adds `cnrs.cnrs_h_bridge`, a conservative bridge from supported symbolic expressions to finite CNRS-H EGF coefficient representations.  It supports constants, polynomials, simple scale laws such as `A*exp(k*s)`, and `exp`/`sin`/`cos` of affine arguments.  Unsupported expressions raise `UnsupportedBridgeExpression`.
