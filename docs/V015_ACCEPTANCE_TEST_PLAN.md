# CNRS Scientific Toolkit v0.15.0 acceptance test plan

Status: SECOND HOLD REPAIRED; FROZEN BEFORE IMPLEMENTATION; RE-AUDIT REQUIRED

| Gate | Requirement |
|---|---|
| A1 | Exact-int/pair coercion passes and every prohibited scalar form fails |
| A2 | Canonical trimming increments offset per low zero; zero is uniquely empty/offset-zero |
| A3 | Support, lookup, and exact Laurent evaluation cover positive/negative offsets |
| A4 | Gaussian-rational vector tests fix gcd reduction and the exact `(abs(im),real,imag)` unit ordering |
| A5 | `beta^-1=(-2-i)/5` and base-zero boundary vectors pass exactly |
| A6 | Known, exhaustive-small, and seeded cases match an independent convolution oracle |
| A7 | Convolution evaluation equals the product of exact evaluations |
| A8 | Algebraic laws, sparse/internal-zero, cancellation, shifted, and large-bit cases pass |
| A9 | Required count is stored-length product and traversal is left-major/right-minor |
| A10 | Raw offset begins at left-plus-right offset; trimming vectors test unchanged and increased offsets |
| A11 | `IN_PROGRESS`, `COMPLETE`, and `LIMIT_REACHED` are the only statuses |
| A12 | Iterator chunk records use `IN_PROGRESS` with null result and exact last pair |
| A13 | Exactly one terminal is emitted, including zero-work and exact-chunk-boundary vectors |
| A14 | Product limits cover zero/below/equal/above; exact API preflights without arithmetic |
| A15 | Limited iteration performs exactly the allowed count and exposes no result |
| A16 | Complete iteration exposes the sole result and is invariant under chunk size |
| A17 | Every public signature, keyword-only boundary, default, and invalid argument exception is introspection-tested |
| A18 | `multiply_with_witness` nullability/status behavior passes every normalize/limit combination |
| A19 | Normalization uses exact Gaussian arithmetic and contains no float/complex/round route |
| A20 | Normalization preserves value/exponent semantics while canonical output offset may increase |
| A21 | Vector `[((-2,1)), offset=-1]` normalizes to value one at canonical offset zero |
| A22 | Carry limit counts only post-input drain iterations; 0/equal/below vectors pass |
| A23 | Exhaustion raises without exposing a partial canonical result |
| A24 | Witness dataclass field order/types and exact top-level JSON key set match the contract |
| A25 | Canonical UTF-8 bytes, separators, sorting, no-BOM/no-newline, and digest vectors match |
| A26 | Normalized object/digest null together exactly when normalization was not requested |
| A27 | Serializer rejects structurally or arithmetically inconsistent witnesses |
| A28 | Parser rejects non-bytes, invalid UTF-8, duplicate/unknown/missing keys, noncanonical bytes, bad identifiers, pairs, and digests |
| A29 | No incomplete witness can be constructed, serialized, parsed, or verified |
| A30 | Independent verifier dependency guard forbids production-convolution import/call |
| A31 | Independent verifier detects mutation of every decisive field and recomputes normalization |
| A32 | Claim guard requires product-count/carry-drain-count wording and rejects total-resource claims |
| A33 | Complete pre-v0.15 regression and unchanged v0.14 acceptance suites pass |
| A34 | Benchmark equality precheck, raw JSON/CSV, environment, timing statistics, memory lane, and cost separation pass |
| A35 | Lean mapping records exact propositions, hypotheses, carriers, offsets, evaluation, certified identities, and adapters |
| A36 | Vendored Lean identity/proof hygiene and all six existing project builds pass |
| A37 | Package/runtime/CFF versions remain 0.14.1 until final activation |
| A38 | Reproducible wheel/sdist double-build, clean installs, retained artifact, and independent candidate audit pass |
| A39 | Both amendments, manifest, exact blobs, source index, final PR head, and tree form the terminal evidence chain |

No waiver may be silent. A dated waiver must state scope, justification, impact, and approval.
