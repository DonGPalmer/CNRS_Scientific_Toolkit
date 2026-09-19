# v0.14.0 local candidate performance results

Status: LOCAL MEASUREMENT COMPLETE; INDEPENDENT REVIEW PENDING

Measured source commit: `939bbecf4cc6fa76b25c543c5459634cdf9f0a86`

Measured source tree: `e670990ee0783a254011af803d0e7c0ebb2566c7`
Generated: 2026-09-12T22:07:09Z

## Environment

- CPython 3.12.14;
- Linux 6.18.35 x86_64, glibc 2.39;
- 9 logical CPUs reported;
- monotonic nanosecond-resolution performance counter;
- garbage collection enabled;
- 5 warmups, 30 timing repetitions, and 10 memory repetitions;
- 30 deterministic exact Gaussian-rational cases.

## Median ratio summary

Each ratio is streaming divided by traditional processing. Values below 1
favor streaming for the measured quantity.

| Operation | Median time ratio | Median peak-memory ratio |
|---|---:|---:|
| First digit | 0.645 | 1.495 |
| First 10 digits | 0.936 | 1.255 |
| First 100 digits | 3.073 | 1.050 |
| First 1,000 digits | 10.736 | 0.721 |
| Complete resolution | 0.973 | not summarized |

On this environment, streaming reduced median latency for very short prefixes,
was slower when materializing 100 or 1,000 digits, and used less median peak
memory at 1,000 digits. Complete resolution time was approximately comparable
in aggregate. The compact traditional periodic representation is especially
efficient when expanded repeatedly in Python, while the stream recomputes each
exact recurrence digit.

These observations are machine- and corpus-specific. They do not establish a
universal speed advantage or asymptotic theorem.

## Retained evidence

- `benchmark-results/v014/v014_performance_results.json` — raw timing and
  peak-memory samples,
  environment, inputs, and parameters;
- `benchmark-results/v014/v014_performance_summary.csv` — per-case medians and
  dispersion;
- `benchmarks/benchmark_streaming_division.py` — exact harness;
- harness SHA-256:
  `a8ddf73c170178f2ab265644d1e0dd6d54c16121a8573eeb32fa2f494c378f7b`.

The benchmark uses equal-output comparisons: both paths return the same number
and sequence of logical digits. Exact canonical parity is checked before any
case is measured.
