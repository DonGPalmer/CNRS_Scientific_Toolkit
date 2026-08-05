# CNRS Scientific Toolkit v0.12.0

## Finite global Riemann-surface layer

This release adds `cnrs.riemann_surface`, an explicit finite-sheet branched-cover model with:

- finite sheet permutations;
- branch-locus loop generators;
- reduced ordered path words;
- noncommuting monodromy;
- lifted surface points and audited transport steps;
- connected-sheet orbit checks;
- local chart evaluators and overlap validation;
- cyclic root-surface constructors.

The earlier generalized node-specific branch registry remains supported. The new layer addresses cases where winding totals are insufficient because loop order matters.

## Validation

Nine new tests cover permutation algebra, path reduction, square- and cubic-root sheet transport, inverse words, noncommuting monodromy, atlas overlap checks, convenience construction, and invalid-data rejection.

## Boundaries

This is a finite monodromy and atlas scaffold. It does not automatically infer algebraic branch points, Puiseux expansions, monodromy, genus, compactification, or certified geometric path words.
