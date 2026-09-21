# CNRS Scientific Toolkit v0.15.0 second freeze amendment — 2026-09-15

Status: SECOND AUDIT HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

Audited predecessor: commit `376dc1ec4ed7e576e1ecd75e4200cd1b32f9bc7d`, tree `e8fa88a93e5b52010d0dbed1f4a79c657368613f`.

## Binding decisions

1. `ConvolutionStatus.IN_PROGRESS` represents every nonterminal progress record.
2. Canonical trimming may increase a stored offset. Normalization preserves exact value and exponent placement before trimming, not the original stored offset.
3. A Gaussian-rational denominator uses the exact existing `unit_normalize` ordering, restated in the API contract.
4. Every public v0.15.0 function signature and default is fixed.
5. The complete witness dataclass, top-level JSON object, field types, nullability, canonical bytes, serializer, parser, and verifier inputs are fixed.
6. Raw convolution begins at `left.offset + right.offset`; ordinary constructor trimming then determines its canonical stored offset.
7. `max_carry_steps` counts only post-input carry-drain iterations.
8. Acceptance gates include explicit vectors for every repaired boundary.

This amendment and the synchronized architecture/API/test documents supersede conflicting language in the 2026-09-14 amendment. No runtime implementation may begin until independent re-audit returns GREEN.
