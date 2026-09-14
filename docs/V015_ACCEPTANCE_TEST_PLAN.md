# CNRS Scientific Toolkit v0.15.0 acceptance test plan

Status: HOLD REPAIRED; FROZEN BEFORE IMPLEMENTATION; RE-AUDIT REQUIRED

| Gate | Requirement |
|---|---|
| A1 | Exact-int and pair coercion passes; Boolean, malformed, approximate, and noncanonical inputs fail |
| A2 | Trimming updates offset correctly and zero has the sole empty/offset-zero representation |
| A3 | Support and coefficient lookup cover positive and negative Laurent offsets |
| A4 | `GaussianRational` reduction, unit normalization, equality, zero, and zero-denominator behavior pass |
| A5 | Laurent evaluation returns exact reduced rational values, including `beta^-1=(-2-i)/5` |
| A6 | Evaluation at zero rejects negative support and handles nonnegative support exactly |
| A7 | Known and seeded randomized cases match an independent exact oracle |
| A8 | Evaluation of convolution equals the product of exact evaluations |
| A9 | Empty, singleton, shifted, sparse/internal-zero, cancellation, and large-bit cases pass |
| A10 | Commutativity, associativity, distributivity, zero, and identity laws pass |
| A11 | Required product count is exactly stored-length product, including internal zeros |
| A12 | Traversal is left-major/right-minor and progress `last_pair` is exact |
| A13 | Limit tests cover zero, below, equal, and above required count |
| A14 | `convolve_exact` preflight failure performs no products and raises `ConvolutionLimitError` |
| A15 | Iterator emits chunk records and exactly one terminal under every boundary case |
| A16 | `LIMIT_REACHED` exposes no result; `COMPLETE` exposes the sole authoritative result |
| A17 | Chunk size changes neither complete result nor canonical witness |
| A18 | `multiply_with_witness` returns the frozen field/null behavior for both statuses and normalize modes |
| A19 | Exact Gaussian/Laurent normalization uses no `complex`, float, or `round` |
| A20 | Normalization digits are 0..4 Gaussian-real pairs and preserve exact value and offset semantics |
| A21 | Carry-step exhaustion raises `NormalizationLimitError` without a partial canonical result |
| A22 | Canonical sequence/witness JSON matches exact key, array, UTF-8, separator, ordering, and newline rules |
| A23 | SHA-256 vectors match independently generated expected bytes and lowercase digests |
| A24 | Strict parsing rejects missing/unknown fields, bad schema/status/algorithm/traversal, malformed pairs, and bad digests |
| A25 | No incomplete witness can be constructed, serialized, or accepted |
| A26 | Independent verifier has an import/dependency guard preventing use of production convolution |
| A27 | Independent verifier detects mutations of every decisive field and recomputes normalization |
| A28 | Claim guard requires “product-count bounded” and rejects broader bounded-resource language |
| A29 | Complete pre-v0.15 regression and unchanged v0.14 acceptance suites pass |
| A30 | Benchmark oracle checks equality before timing and records raw JSON/CSV plus environment metadata |
| A31 | Timing reports warm-up, samples, median, minimum, IQR, input family, and separated witness/normalization cost |
| A32 | Peak-memory protocol is separate, reproducible, qualified, and permits negative results |
| A33 | Lean mapping records theorem statements, hypotheses, carrier/offset/evaluation conventions, certified identities, and adapters |
| A34 | Vendored Lean identity/proof hygiene and all six existing project builds pass |
| A35 | Package/runtime/CFF versions stay 0.14.1 until final release activation |
| A36 | Reproducible wheel/sdist double-build, clean installs, retained artifact, and independent candidate audit pass |
| A37 | Manifest, amendment, source index, repaired document blobs, PR head, and Git tree form a complete terminal evidence chain |

Use exhaustive small cases where feasible, fixed seeded wider cases, metamorphic laws, corruption matrices, exact reference vectors, and gross-regression thresholds that do not treat timing noise as correctness failure. No waiver may be silent.
