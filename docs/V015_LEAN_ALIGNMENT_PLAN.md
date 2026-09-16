# CNRS Scientific Toolkit v0.15.0 Lean-alignment record

Status: IMPLEMENTATION CANDIDATE MAPPED; THEOREM BOUNDARY RESTRICTED

## Target mathematical bridge

The intended bridge is finite-support convolution multiplication: coefficient convolution represents multiplication of evaluated finite Laurent/polynomial expressions over the applicable Gaussian-integer/CNRS carrier.

## Required theorem map

Before any theorem-backed release claim, record:

- Lean repository and project;
- theorem names and complete statements;
- hypotheses, carrier, support convention, offset convention, and evaluation map;
- Lean/toolchain and dependency revisions;
- certified commit, Git tree, workflow run/job, artifact identity, and source checksums;
- a field-by-field mapping from Lean objects to Python types and operations.

## Certified theorem map used by this candidate

The governed CNRS-LEAN-CAPSTONE identity is repository
`DonGPalmer/SSC_Formal_Methods_CI`, commit
`07e776b4e1d7d09513394a4b676516eb51e4c597`, tree
`fd61bac37369f8e3020d70141c565a4fba414a98`, Lean `4.33.0`, workflow
run `34534566879`, job `103063055916`, artifact `10175389923`, artifact
SHA-256 `840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.
The exact sources are vendored under `formal/lean/` and guarded by
`tools/check_lean_alignment.py`.

| Lean proposition | Exact hypotheses and carrier | Python correspondence | Boundary |
|---|---|---|---|
| `CNRSArithmetic.coeffValue_convolutionCoefficients` | `xs ys : List Digit`; `Digit = Fin 5`; coefficients and values in the Gaussian integers; LSD-first, exponent zero | `convolve_exact()` restricted to zero-offset inputs whose coefficients are `(d,0)`, `0 <= d <= 4`; `CNRSFiniteSequence.evaluate((-2,1))` | The Python API additionally accepts arbitrary Gaussian coefficients and integer Laurent offsets; those extensions are computationally validated, not covered by this theorem |
| `CNRSArithmetic.normalizeCoefficients_correct` | arbitrary finite `List GaussianInt`; evaluation by `coeffValue`; exponent zero | `normalize_gaussian_laurent()` restricted to offset zero; digit recurrence and evaluation at `(-2,1)` | Python preserves arbitrary integer offsets by carrying the offset unchanged; that placement adapter is tested but is not a Lean theorem |
| `CNRSArithmetic.fixedMultiply_correct` | canonical finite digit lists; convolution followed by normalization | `multiply_with_witness()` on zero-offset canonical-digit sequences with normalization requested | Witness serialization, limits, progress records, Gaussian-rational evaluation, and negative offsets are outside this theorem |

The adapter is explicit: Lean `GaussianInt` maps to Python `(real, imag)`;
Lean `List Digit` maps to `CNRSFiniteSequence(tuple((int(d),0) ...), 0)`;
Lean LSD-first list position maps to Python coefficient index; Lean `beta` maps
to Python `(-2,1)`; and Lean `wordValue`/`coeffValue` maps to
`CNRSFiniteSequence.evaluate((-2,1))`. No claim maps a negative Python offset
to the natural-number denominator shift used by `CnrsQ2.evalFiniteLaurent`.

## Synchronization rule

The Toolkit may import a Lean result only after that result has completed its own independent audit and governed promotion. The exact certified sources must be vendored or checksum-linked using the existing source-identity mechanism. Development snapshots may guide tests but cannot support release claims.

## Python/Lean boundary

Lean proves the identified finite mathematical proposition in its formal carrier. Python remains independently implemented. Toolkit tests verify representative and property-based correspondence; they do not convert the Python runtime into formally verified or Lean-extracted software.

## Mismatch handling

Differences in trimming, zero representation, coefficient order, Laurent offsets, normalization, or resource-limit behavior must be resolved explicitly. An adapter may bridge representations only if it is documented and tested as value preserving. A mismatch cannot be hidden by weakening release language after implementation.

## Fallback release posture

The certified capstone contains the restricted finite-convolution and
normalization propositions above, but not a theorem matching the complete
v0.15.0 Python carrier and API. Accordingly, v0.15.0 remains a computationally
validated Python release. The restricted mapping may be described accurately;
the complete Python implementation must not be described as Lean-verified,
Lean-extracted, or end-to-end formally verified.
