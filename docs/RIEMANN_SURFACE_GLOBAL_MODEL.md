# CNRS finite global Riemann-surface model

## Scope

Version 0.12.0 introduces a finite-sheet global continuation layer. It represents a branched cover by:

- an explicit finite sheet set;
- isolated branch loci;
- an oriented loop generator for each locus;
- a monodromy permutation for each generator;
- ordered path words in those generators;
- lifted endpoints `(projected z, sheet)`;
- optional local chart evaluators and overlap checks.

This is a real extension beyond the prior node-specific cyclic branch registry. The prior registry remains useful for local symbolic expressions. The global surface model handles noncommuting monodromy, where a winding vector alone is insufficient.

## Core state

For a surface with sheets `F` and branch locus `B`, the user supplies a monodromy representation

\[
\rho:\pi_1(\mathbb C\setminus B,z_*)\longrightarrow \operatorname{Perm}(F).
\]

A computational path is stored as an ordered reduced word in named branch generators. Continuation applies the corresponding permutations in order.

## Example: cubic noncommuting monodromy

```python
from cnrs.riemann_surface import *

sheets = (0, 1, 2)
a = SheetPermutation.cycle(sheets, (0, 1))
b = SheetPermutation.cycle(sheets, (1, 2))

surface = RiemannSurface(
    "S3 example",
    sheets,
    [BranchGenerator("a", 0, a), BranchGenerator("b", 1, b)],
)

ab = surface.lift(SurfacePoint(2, 0), PathWord(["a", "b"]))
ba = surface.lift(SurfacePoint(2, 0), PathWord(["b", "a"]))

assert ab.word.winding_vector(["a", "b"]) == ba.word.winding_vector(["a", "b"])
assert ab.end.sheet != ba.end.sheet
```

## What is global here

The layer is global in the following bounded sense:

1. sheet identity is preserved across an arbitrarily long ordered continuation word;
2. finite monodromy actions may be noncommutative;
3. inverse paths and closed lifted paths are testable;
4. connected components of the sheet action are computable;
5. chart evaluators can be attached and checked on overlaps.

## Current boundaries

The implementation does not yet:

- infer branch points from `P(z,w)=0`;
- compute Puiseux expansions;
- derive monodromy permutations numerically;
- convert a sampled geometric path automatically into a fundamental-groupoid word;
- certify branch-cut avoidance or singular-distance bounds;
- normalize singular algebraic curves;
- construct compact surfaces including branch behavior at infinity;
- compute genus, homology cycles, period matrices, or Abelian integrals.

These are the next research layers rather than hidden capabilities of the current code.
