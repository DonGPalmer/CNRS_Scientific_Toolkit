# Finite arithmetic Lean extension — candidate crosswalk

Status: DEVELOPMENT CANDIDATE; no governed promotion or release activation.
The certified capstone and Toolkit `formal/` subtree remain unchanged.

Certified source: `DonGPalmer/CNRS_Lean` at
`ce56a7359f494d29bab8e9bea6c3ea596f8fd62f`, Lean 4.33.0 / Mathlib
`db584cd6d46c92f209a44c0f1c829460d327499d`.

The separate private checker candidate is
[finite-bridge audit source](https://github.com/DonGPalmer/SSC_Formal_Methods_CI/blob/7129e8166273ce620f0680ff5d1ce4e2e772d495/audit/v018/SharedShiftAddition.lean).
CI evidence and the adoption decision must be read separately: source presence
alone does not establish either successful checking or governed promotion.

| Boundary | Extension declarations | Remaining software correspondence |
|---|---|---|
| Common denominator shift | `evalFiniteLaurent_addWords_shift` | Parse/format and runtime refinement |
| Independent shifts | `wordValue_lowZeroPad`, `betaFrac_ne_zero`, `evalFiniteLaurent_lowZeroPad`, `evalFiniteLaurent_align`, `evalFiniteLaurent_addWords_mixed` | Actual parser alignment and canonical output |
| Negation constant | `wordValue_144`, `fixedMultiply_144_negates` | Python convolution/normalizer correspondence |
| Fractional negation | `evalFiniteLaurent_fixedMultiply_144_negates` | Actual finite Laurent carrier pipeline |
| Subtraction | `evalFiniteLaurent_subWords`, `evalFiniteLaurent_subWords_mixed` | Composition of verified runtime bridges |
| Early stopping | `runAddition_stopped_value` | Show Python's emitted trace is the formal run and its drain reaches zero |

The stopping lemma assumes zero final carry. It does not independently prove
that a Python loop terminates or that two output strings are identical. The
existing certified five-step drain supplies the mathematical termination fact;
the trace correspondence remains to be proved.

The prior three declarations passed the earlier additive audit run
[39257321314](https://github.com/DonGPalmer/SSC_Formal_Methods_CI/actions/runs/39257321314).
The extended candidate's checking result is retained in the programme audit
evidence. It remains a candidate until author-governed adoption.

Axiom output is retained per theorem. New algebraic corollaries can inherit
native-decision dependencies from certified carry and termination lemmas; this
extension does not claim to remove that existing trust boundary.

The exact comparison/value Python additions reuse existing exact carriers and
are independently tested. These model lemmas do not certify those Python
functions, canonical spelling uniqueness, arbitrary infinite streams, or
ordinary-complex analytic convergence.
