# v0.14.0 performance comparison protocol

Status: FROZEN FOR IMPLEMENTATION  
Benchmark harness: benchmarks/benchmark_streaming_division.py

## Purpose

Measure streaming division against the established materialized processing without presuming that streaming is universally faster. The primary hypotheses are lower latency and lower peak memory when a caller consumes only an initial digit prefix. Complete resolution may be similar or slower because cycle detection, witness construction, and witness validation perform additional work.

No performance claim may appear in release material until this protocol has produced candidate-specific results.

## Compared operations

| Scenario | Streaming operation | Traditional operation |
| --- | --- | --- |
| Construction | stream_division(p, q) | Not presented as a speed comparison |
| First digit | stream_division(p, q).take(1) | canonical_expansion(p, q), then materialize one digit |
| Prefix | stream_division(p, q).take(n) | canonical_expansion(p, q), then materialize n logical digits |
| Complete canonical result | stream_division(p, q).resolve() | canonical_expansion(p, q) |
| Witness creation | division_witness(p, q) | Reported separately; no traditional equivalent |
| Witness validation | validate_division_witness(w) | Reported separately; no traditional equivalent |

The traditional prefix comparator resolves the existing canonical compact
representation before expanding its prefix/period to the same requested logical
digit count. This gives an equal-output comparison for integer and Gaussian
denominators.

## Required datasets

Benchmark at least:

- terminating inputs;
- short-period coprime integer denominators;
- shifted eventually-periodic inputs;
- long preperiod or period cases identified by deterministic corpus scan;
- Gaussian denominators in every quadrant;
- prefix lengths 1, 10, 100, and 1,000 where supported.

Inputs must be stored in the result artifact. Do not select only favorable cases. The final candidate benchmark must contain at least 30 distinct inputs, including the acceptance corpus representatives.

## Timing method

- Use time.perf_counter_ns().
- Run at least 5 untimed warmups and 30 measured repetitions per operation.
- Alternate or deterministically rotate operation order to reduce systematic ordering bias.
- Create a fresh result object inside each measured repetition.
- Report median, minimum, maximum, median absolute deviation, and interquartile range.
- Record raw repetition values in nanoseconds.
- Do not combine stream construction with prefix consumption silently.
- Run with garbage collection policy recorded and held constant.

Timing should be performed on an otherwise idle machine. Results from shared CI runners may be retained as regression evidence but must not be presented as authoritative speed comparisons.

## Memory method

Use tracemalloc with a fresh tracing interval for each repetition. Report median and raw peak bytes. Measure construction, prefix consumption, and complete resolution independently. At least 10 memory repetitions are required.

tracemalloc does not capture all native allocations. This limitation must accompany published memory results.

## Environment record

The JSON result must record:

- Toolkit version, candidate commit, and tree;
- benchmark-harness SHA-256;
- Python implementation and full version;
- operating system and architecture;
- processor string and logical CPU count;
- timer implementation;
- timestamp in UTC;
- warmup, timing, and memory repetition counts;
- garbage-collection policy;
- complete input corpus and prefix lengths.

## Analysis and claims

For paired scenarios calculate streaming/traditional ratios from medians. A ratio below 1 favors streaming. Publish absolute values as well as ratios.

Do not use a fixed timing threshold as a correctness acceptance test. The release gate requires:

1. successful completion with schema-valid JSON and CSV;
2. exact output parity for every compared case;
3. no unbounded eager materialization in stream construction;
4. no unexplained order-of-magnitude regression in full resolution;
5. review of raw data and environment metadata.

Permitted wording must match the evidence, for example: “On the recorded benchmark environment, median time to the first 100 digits was lower for the tested corpus.” Do not generalize a machine-specific measurement into a universal complexity or speed claim.

## Artifacts

The governed release evidence directory must retain:

- `benchmark-results/v014/v014_performance_results.json`;
- `benchmark-results/v014/v014_performance_summary.csv`;
- the exact benchmark harness;
- its SHA-256;
- the candidate commit/tree and execution command;
- reviewer disposition of anomalies.
