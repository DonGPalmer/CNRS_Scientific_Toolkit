# CNRS Scientific Toolkit v0.15.0 comparison and benchmark plan

Status: FROZEN BEFORE IMPLEMENTATION

## Questions

1. What time and peak-memory cost does exact CNRS finite convolution add relative to direct conventional processing?
2. What overhead is attributable to witness generation and validation?
3. When does chunked execution reduce peak working memory?
4. Does canonical normalization dominate convolution cost for representative CNRS inputs?

## Compared implementations

- v0.15 native exact finite convolution;
- independent schoolbook Python convolution over Gaussian-integer pairs;
- ordinary Python polynomial convolution over built-in complex integers represented as pairs;
- existing Toolkit multiplication path where input domains overlap;
- optional NumPy comparison clearly labeled approximate/non-native and excluded from exactness claims.

## Input families

Dense and sparse supports; lengths 1, 4, 16, 64, 256, and 1024 where practical; zero/cancellation-heavy inputs; shifted Laurent supports; small and increasing coefficient bit lengths; with and without witness generation; with and without canonical normalization.

## Measurement protocol

- Record commit, Python/platform versions, CPU, logical cores, memory, dependency versions, and command.
- Use a deterministic seed and store generated-case descriptors.
- Perform warm-up separately.
- Report at least 11 measured repetitions for short cases; justify fewer for long cases.
- Record median, minimum, interquartile range, and samples.
- Measure peak memory consistently in a separate lane from timing.
- Store raw JSON and CSV plus a Markdown interpretation.
- Verify exact output equality before accepting each timing sample.

## Interpretation rules

No universal superiority claim is allowed. Report cross-over points only for the measured environment. Separate algorithmic complexity from implementation overhead. A slowdown is a valid result. Chunking may improve bounded memory while increasing time. Witness and normalization costs must not be hidden in an unlabeled aggregate.

## Acceptance

The harness must be reproducible from one documented command, survive an independent rerun, and fail if compared implementations disagree. Results become release evidence only after checksums and candidate identity are recorded.
