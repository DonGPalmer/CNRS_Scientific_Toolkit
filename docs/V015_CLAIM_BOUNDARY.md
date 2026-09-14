# CNRS Scientific Toolkit v0.15.0 claim boundary

Status: FROZEN FOR IMPLEMENTATION

## Claims permitted after all release gates pass

v0.15.0 may claim:

- exact finite-support convolution over the implemented Gaussian-integer coefficient carrier;
- exact agreement with direct finite polynomial multiplication for accepted inputs;
- deterministic bounded and chunked execution;
- independently recomputable convolution/multiplication witnesses;
- value preservation across the documented canonical-normalization adapter;
- empirical timing and memory measurements for the disclosed benchmark environment;
- theorem alignment only for exact propositions identified in the Lean-alignment record.

## Claims requiring qualification

- “Streaming” or “chunked” describes bounded scheduling and memory behavior, not infinite-stream closure.
- “Theorem-aligned” means the Python behavior is tested against the stated mathematical proposition; Python is independently implemented.
- Performance statements apply only to named inputs, versions, hardware, interpreter, repetitions, and statistics.
- Algebraic laws apply within the finite exact carrier and documented resource limits.

## Claims prohibited

v0.15.0 must not claim:

- arbitrary or productive infinite-stream multiplication;
- general analytic convergence;
- universal speed or memory superiority over conventional processing;
- FFT-equivalent complexity;
- Lean extraction, proof-carrying Python, or end-to-end formal verification;
- that a later or unaudited Lean result governs the released Python implementation;
- new physical, biological, or empirical validation;
- a canonical global representation for every complex value.

Release notes, README text, benchmarks, API documentation, and provenance must preserve these boundaries.
