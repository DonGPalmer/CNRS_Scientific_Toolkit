# CNRS Scientific Toolkit v0.15.0 claim boundary

Status: HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

After all gates pass, v0.15.0 may claim exact finite-support Gaussian-integer convolution; exact Gaussian-rational Laurent evaluation; deterministic product-count-limited and chunked execution; independently recomputable complete witnesses; and exact value preservation by the new Gaussian/Laurent normalizer.

Required qualifications:

- “product-count bounded” refers only to the number of stored-position scalar products;
- it does not bound coefficient bit length, carry work, output allocation, elapsed time, or memory;
- chunking changes scheduling, not infinite-stream closure or asymptotic complexity;
- benchmark statements apply only to the recorded environment and input family;
- theorem alignment names exact independently certified Lean propositions, while Python remains independently implemented.

Prohibited claims include arbitrary infinite-stream multiplication, bounded total computational resources, global analytic convergence, universal speed/memory superiority, FFT complexity, Lean extraction or end-to-end verification, use of an unaudited formal result, new physical/biological validation, or a canonical global representation of every complex value.
