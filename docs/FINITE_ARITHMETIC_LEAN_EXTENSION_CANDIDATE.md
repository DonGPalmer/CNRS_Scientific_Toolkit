# Finite arithmetic Lean extension — candidate crosswalk

Status: installed, authoritatively verified E2 DEVELOPMENT CANDIDATE.
Final governed adoption/freeze and Toolkit release activation remain pending.
The certified capstone and Toolkit `formal/` subtree remain unchanged.

Certified public source: `DonGPalmer/CNRS_Lean` at
`ce56a7359f494d29bab8e9bea6c3ea596f8fd62f`.
The separate private checker head is
`03e40d19348694b470897b6c6434e38ccc841250`, authoritative installed-source
[run 39331704917](https://github.com/DonGPalmer/SSC_Formal_Methods_CI/actions/runs/39331704917).
It checked the actual installed source/configuration inputs in normal and
clean offline builds. The retained evidence contains source hashes, dependency
revisions, build logs and axiom reports. This is successful checking of a
candidate; it does not by itself establish final governed promotion.

The Integration extension contains 28 results: 12 finite-Laurent bridge
results, seven literal-table results, and nine typed-runner results.
Declarations below are in `CNRSIntegration.ToolkitBridge` (bridge) or
`CNRSIntegration.ToolkitTransition` (table/runner).

| Contract | Installed candidate results | Toolkit connection and remaining obligation |
|---|---|---|
| Common fractional shift | `evalFiniteLaurent_addWords_shift` | Abstract finite addition value; actual parse/format refinement remains |
| Independent shifts | `wordValue_lowZeroPad`, `betaFrac_ne_zero`, `evalFiniteLaurent_lowZeroPad`, `evalFiniteLaurent_align`, `evalFiniteLaurent_addWords_mixed` | Proves mathematical alignment; Python alignment still independently tested |
| Negation by 144 | `wordValue_144`, `fixedMultiply_144_negates`, `evalFiniteLaurent_fixedMultiply_144_negates` | Proves abstract multiplication by 144 negates; actual Python convolution/normalizer correspondence remains |
| Subtraction | `evalFiniteLaurent_subWords`, `evalFiniteLaurent_subWords_mixed` | Abstract composition; requires runtime negation and addition bridges |
| Abstract stopped run | `runAddition_stopped_value` | Correct value conditional on zero final carry |
| Carry inventory and literal relation | `carry_order_matches`, `table_size`, `table_matches_addStep`, `carry_indices_injective`, `table_value_equation` | Permanent Python gate compares all 350 rows and 14 ordered carries to these pinned literals |
| Sharp literal-table drain | `table_drain_five`, `table_drain_four_insufficient` | Permanent gate checks all zero-input paths; runtime guard remains 20 |
| Typed single-step simulation | `table_carry_mem`, `tableOutput_matches`, `tableNext_matches` | Establishes state/output relation in Lean; Python table identity checked computationally |
| Arbitrary finite typed runner | `tableRun_refines`, `tableRun_output_length`, `tableRun_invariant` | No input-length bound in these Lean results; actual Python loop/trace bridge remains |
| Stopped/drained typed runner | `tableRun_stopped_value`, `tableRun_append_drain`, `tableRun_drained_value` | Conditional zero-stop correctness and unconditional correctness after fixed five-column drain; Python's variable-length early stop still needs explicit refinement |

The [certificate documentation](FINITE_ADDITION_CERTIFICATE.md) records exact
module/artifact pins and reproducible extraction. Its CI gate checks drift
against Lean-checked data without invoking Lean. It does not extend the
certified `formal/` crosswalk or establish full Python program verification.

Axiom reports remain part of the authoritative evidence. Algebraic corollaries
can inherit native-decision dependencies from certified carry/termination
lemmas; the extension does not remove that trust boundary.

The candidate Python APIs `cnrs_string_value_exact`, `cnrs_eq_exact`,
`CVal.to_gaussian_exact` and `CVal.equals_exact` supply exact finite-value
comparison using existing exact carriers. They are independently tested;
these Lean results do not certify those functions, canonical spelling
uniqueness, arbitrary infinite streams, ordinary-complex analytic convergence,
or the general multiplication normalizer.
