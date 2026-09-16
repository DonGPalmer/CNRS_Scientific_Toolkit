# CNRS Scientific Toolkit v0.15.0 finite-convolution comparison

Status: AMBER-repair candidate measurement; terminal re-audit pending.

## Provenance

- Implementation commit: `2adf691b3ad25dd2db9a7be6d9aae92175a71db8`
- Implementation tree: `8e05246d477237bd96b6d3cb51c82a1f17404e9d`
- Deterministic seed: `1500`
- Repetitions: 11 per measured operation
- Families: dense and sparse
- Stored lengths: 1, 4, 16, 64 and 256
- Command: `python benchmarks/benchmark_finite_convolution.py --output-dir benchmark-results/v015`

The environment and every raw timing sample are recorded in `benchmark-results/v015/finite_convolution_results.json`. The compact results are in `finite_convolution_summary.csv`.

## Equality gate

Every measured case first required exact equality among production convolution, the independent nested-loop oracle, normalization output and the witness path. Witness validation was also required to pass. No timing sample was accepted before these checks.

## Representative observation

For the dense length-256 case on the recorded environment:

| Operation | Median time | Peak traced memory |
|---|---:|---:|
| Native raw convolution | 18.603 ms | 35,488 bytes |
| Independent conventional oracle | 19.373 ms | 35,456 bytes |
| Normalization only | 0.419 ms | 12,644 bytes |
| Convolution plus witness construction | 19.280 ms | 86,534 bytes |
| Independent witness verification | 19.915 ms | 82,084 bytes |

These measurements show near-parity between the two exact schoolbook implementations in this case. Complete witness construction and verification add memory and time, while normalization is a smaller component for this input family. This is an environment-specific observation, not a universal performance claim.

## Artifact identities

- `finite_convolution_results.json`: SHA-256 `b0150b8e9fdf475aa2e74f4fd47657a9d889d749b7cd6a304a40c81c71b4ff1c`
- `finite_convolution_summary.csv`: SHA-256 `e6f4b482292fefdefc8541d1e54a99f286d1b03a089888929a72d9864a36f11a`
