#!/usr/bin/env python3
"""Reproducible v0.14.0 streaming-versus-materialized benchmark.

This is a measurement harness, not a correctness or speedup assertion.
Run from the repository root after implementing the frozen v0.14.0 API.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import tracemalloc
from typing import Callable

from cnrs.division import canonical_expansion
from cnrs.streaming_division import stream_division
from cnrs.witnesses import division_witness, validate_division_witness


SCHEMA = "cnrs-v014-performance-results-v1"
DEFAULT_CASES = (
    {"name": "zero", "p": (0, 0), "q": (1, 0)},
    {"name": "integer", "p": (7, -3), "q": (1, 0)},
    {"name": "terminating_base_power", "p": (-2, -1), "q": (5, 0)},
    {"name": "short_period", "p": (1, 0), "q": (2, 0)},
    {"name": "coprime_7", "p": (3, 1), "q": (7, 0)},
    {"name": "shifted_5", "p": (1, 0), "q": (5, 0)},
    {"name": "shifted_35", "p": (2, -1), "q": (35, 0)},
    {"name": "gaussian_q1", "p": (3, 2), "q": (1, 2)},
    {"name": "gaussian_q2", "p": (3, 2), "q": (-1, 2)},
    {"name": "gaussian_q3", "p": (3, 2), "q": (-1, -2)},
    {"name": "gaussian_q4", "p": (3, 2), "q": (1, -2)},
) + tuple(
    {
        "name": f"fixed_{index:02d}",
        "p": ((index % 9) - 4, ((index * 3) % 7) - 3),
        "q": ((2, 3, 5, 7, 10, 11, 13)[index % 7], 0),
    }
    for index in range(19)
)


def stats(values: list[int]) -> dict[str, object]:
    ordered = sorted(values)
    q = statistics.quantiles(ordered, n=4, method="inclusive")
    median = statistics.median(ordered)
    deviations = [abs(x - median) for x in ordered]
    return {
        "raw": values,
        "median": median,
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "mad": statistics.median(deviations),
        "iqr": q[2] - q[0],
    }


def timed(operation: Callable[[], object], warmups: int, repetitions: int) -> dict[str, object]:
    for _ in range(warmups):
        operation()
    values = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        operation()
        values.append(time.perf_counter_ns() - start)
    return stats(values)


def memory(operation: Callable[[], object], repetitions: int) -> dict[str, object]:
    peaks = []
    for _ in range(repetitions):
        tracemalloc.start()
        try:
            operation()
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        peaks.append(peak)
    return {"raw_peak_bytes": peaks, "median_peak_bytes": statistics.median(peaks)}


def exact_parity(p: tuple[int, int], q: tuple[int, int]) -> None:
    streamed = stream_division(p, q).resolve()
    traditional = canonical_expansion(p, q)
    assert streamed.power_offset == traditional.power_offset
    assert streamed.prefix_digits == traditional.prefix
    assert streamed.period_digits == traditional.period
    assert streamed.exact_value_fractions() == traditional.exact_value_fractions()


def materialized_take(
    p: tuple[int, int], q: tuple[int, int], count: int
) -> tuple[int, ...]:
    """Resolve traditionally, then materialize the requested logical prefix."""
    expansion = canonical_expansion(p, q)
    digits = list(expansion.prefix)
    if expansion.period:
        while len(digits) < count:
            digits.extend(expansion.period)
    return tuple(digits[:count])


def measure(
    name: str,
    operation: Callable[[], object],
    warmups: int,
    repetitions: int,
    memory_repetitions: int,
) -> dict[str, object]:
    return {
        "name": name,
        "timing_ns": timed(operation, warmups, repetitions),
        "memory": memory(operation, memory_repetitions),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--memory-repetitions", type=int, default=10)
    parser.add_argument("--json", default="v014_performance_results.json")
    parser.add_argument("--csv", default="v014_performance_summary.csv")
    parser.add_argument("--commit", default=os.environ.get("CNRS_CANDIDATE_COMMIT", "UNRECORDED"))
    parser.add_argument("--tree", default=os.environ.get("CNRS_CANDIDATE_TREE", "UNRECORDED"))
    args = parser.parse_args()
    if args.warmups < 5 or args.repetitions < 30 or args.memory_repetitions < 10:
        parser.error("minimums are 5 warmups, 30 timing repetitions, and 10 memory repetitions")

    harness_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    prefix_lengths = (1, 10, 100, 1000)
    records: list[dict[str, object]] = []
    gc_enabled = gc.isenabled()
    assert len(DEFAULT_CASES) >= 30, "the governed benchmark corpus requires at least 30 inputs"

    for case in DEFAULT_CASES:
        p = tuple(case["p"])
        q = tuple(case["q"])
        exact_parity(p, q)
        case_records = []
        case_records.append(measure(
            "stream_construct",
            lambda p=p, q=q: stream_division(p, q),
            args.warmups, args.repetitions, args.memory_repetitions,
        ))
        for count in prefix_lengths:
            case_records.append(measure(
                f"stream_take_{count}",
                lambda p=p, q=q, count=count: stream_division(p, q).take(count),
                args.warmups, args.repetitions, args.memory_repetitions,
            ))
            case_records.append(measure(
                f"traditional_expand_{count}",
                lambda p=p, q=q, count=count: materialized_take(p, q, count),
                args.warmups, args.repetitions, args.memory_repetitions,
            ))
        case_records.append(measure(
            "stream_resolve",
            lambda p=p, q=q: stream_division(p, q).resolve(),
            args.warmups, args.repetitions, args.memory_repetitions,
        ))
        case_records.append(measure(
            "traditional_canonical",
            lambda p=p, q=q: canonical_expansion(p, q),
            args.warmups, args.repetitions, args.memory_repetitions,
        ))
        case_records.append(measure(
            "witness_create",
            lambda p=p, q=q: division_witness(p, q),
            args.warmups, args.repetitions, args.memory_repetitions,
        ))
        witness = division_witness(p, q)
        case_records.append(measure(
            "witness_validate",
            lambda witness=witness: validate_division_witness(witness),
            args.warmups, args.repetitions, args.memory_repetitions,
        ))
        records.append({"case": case, "measurements": case_records})

    payload = {
        "schema": SCHEMA,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate": {"commit": args.commit, "tree": args.tree},
        "harness_sha256": harness_hash,
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
            "timer": {
                "implementation": time.get_clock_info("perf_counter").implementation,
                "monotonic": time.get_clock_info("perf_counter").monotonic,
                "adjustable": time.get_clock_info("perf_counter").adjustable,
                "resolution": time.get_clock_info("perf_counter").resolution,
            },
            "gc_enabled": gc_enabled,
        },
        "parameters": {
            "warmups": args.warmups,
            "repetitions": args.repetitions,
            "memory_repetitions": args.memory_repetitions,
            "prefix_lengths": prefix_lengths,
        },
        "results": records,
    }
    Path(args.json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with Path(args.csv).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("case", "operation", "median_ns", "mad_ns", "iqr_ns", "median_peak_bytes"))
        for record in records:
            for measurement in record["measurements"]:
                timing = measurement["timing_ns"]
                writer.writerow((
                    record["case"]["name"],
                    measurement["name"],
                    timing["median"],
                    timing["mad"],
                    timing["iqr"],
                    measurement["memory"]["median_peak_bytes"],
                ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
