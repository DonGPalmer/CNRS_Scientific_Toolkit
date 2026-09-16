# CNRS Scientific Toolkit v0.15.0 finite-convolution comparison

Status: candidate measurement; independently reproducible; release interpretation pending audit.

## Provenance

- Implementation commit: `467fda628e046545209fb99366802a8b631b9c50`
- Implementation tree: `48ec916d092aae3c4547cad7fbc2650072b527c2`
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
| Native raw convolution | 19.918 ms | 35,488 bytes |
| Independent conventional oracle | 20.109 ms | 35,456 bytes |
| Normalization only | 0.441 ms | 12,644 bytes |
| Convolution plus witness construction | 20.371 ms | 86,534 bytes |
| Independent witness verification | 20.644 ms | 82,084 bytes |

These measurements show near-parity between the two exact schoolbook implementations in this case. Complete witness construction and verification add memory and time, while normalization is a smaller component for this input family. This is an environment-specific observation, not a universal performance claim.

## Artifact identities

- `finite_convolution_results.json`: SHA-256 `1fd134b1b02fbae3c2267a07f300f91b51a35a91751336c40aa790dc1fc8d223`
- `finite_convolution_summary.csv`: SHA-256 `e75a092e88ddf38d42add4c9241d16ec66e687fc929469e50a60b8bfbd560a0c`
