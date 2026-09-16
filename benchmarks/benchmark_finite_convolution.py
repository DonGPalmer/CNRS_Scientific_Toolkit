"""Reproducible v0.15.0 finite-convolution comparison harness."""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from importlib import metadata
from pathlib import Path
import random

from cnrs.convolution import convolve_exact, multiply_with_witness
from cnrs.convolution_witnesses import verify_convolution_witness
from cnrs.finite_sequence import CNRSFiniteSequence
from cnrs.gaussian_normalization import normalize_gaussian_laurent
from cnrs.validation.convolution_oracle import oracle_convolve


def _git_identity() -> tuple[str, str]:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
        return commit, tree
    except (OSError, subprocess.CalledProcessError):
        return "unavailable", "unavailable"


def _case(length: int, seed: int, sparse: bool) -> tuple[CNRSFiniteSequence, CNRSFiniteSequence]:
    rng = random.Random(seed)
    def coefficient(index: int) -> tuple[int, int]:
        if sparse and index % 4:
            return (0, 0)
        return (rng.randrange(-9, 10), rng.randrange(-9, 10))
    left = CNRSFiniteSequence(tuple(coefficient(i) for i in range(length)), -2)
    right = CNRSFiniteSequence(tuple(coefficient(i + length) for i in range(length)), 3)
    return left, right


def _summary(samples: list[int]) -> dict[str, object]:
    ordered = sorted(samples)
    quartiles = statistics.quantiles(ordered, n=4, method="inclusive") if len(ordered) > 1 else [ordered[0]] * 3
    return {
        "minimum_ns": min(ordered),
        "median_ns": int(statistics.median(ordered)),
        "iqr_ns": int(quartiles[2] - quartiles[0]),
        "samples_ns": samples,
    }


def _time(callable_, repetitions: int) -> dict[str, object]:
    callable_()
    samples: list[int] = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        callable_()
        samples.append(time.perf_counter_ns() - start)
    return _summary(samples)


def _peak(callable_) -> int:
    tracemalloc.start()
    callable_()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def run(lengths: list[int], repetitions: int, seed: int) -> dict[str, object]:
    commit, tree = _git_identity()
    records: list[dict[str, object]] = []
    for sparse in (False, True):
        for length in lengths:
            left, right = _case(length, seed + length + int(sparse) * 10000, sparse)
            expected = oracle_convolve(left, right)
            if convolve_exact(left, right) != expected:
                raise RuntimeError("native/oracle equality precheck failed")
            normalized = normalize_gaussian_laurent(expected)
            complete = multiply_with_witness(left, right)
            if complete.raw_convolution != expected or complete.normalized != normalized:
                raise RuntimeError("witness path equality precheck failed")
            assert complete.witness is not None
            if not verify_convolution_witness(complete.witness).valid:
                raise RuntimeError("witness verification precheck failed")
            operations = {
                "native_raw": lambda: convolve_exact(left, right),
                "independent_oracle": lambda: oracle_convolve(left, right),
                "normalization_only": lambda: normalize_gaussian_laurent(expected),
                "witness_build": lambda: multiply_with_witness(left, right),
                "witness_verify": lambda: verify_convolution_witness(complete.witness),
            }
            for name, operation in operations.items():
                timing = _time(operation, repetitions)
                records.append({
                    "family": "sparse" if sparse else "dense",
                    "length": length,
                    "stored_products": len(left.coefficients) * len(right.coefficients),
                    "operation": name,
                    **timing,
                    "peak_bytes": _peak(operation),
                })
    return {
        "schema": "cnrs-v015-finite-convolution-benchmark-v1",
        "candidate_commit": commit,
        "candidate_tree": tree,
        "seed": seed,
        "repetitions": repetitions,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "logical_cores": os.cpu_count(),
            "numpy": metadata.version("numpy"),
        },
        "command": "python benchmarks/benchmark_finite_convolution.py --output-dir benchmark-results/v015",
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--lengths", default="1,4,16,64,256")
    parser.add_argument("--repetitions", type=int, default=11)
    parser.add_argument("--seed", type=int, default=1500)
    args = parser.parse_args()
    lengths = [int(item) for item in args.lengths.split(",")]
    if args.repetitions < 1 or any(length < 1 for length in lengths):
        raise ValueError("positive repetitions and lengths are required")
    result = run(lengths, args.repetitions, args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "finite_convolution_results.json"
    csv_path = args.output_dir / "finite_convolution_summary.csv"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["family", "length", "stored_products", "operation", "minimum_ns", "median_ns", "iqr_ns", "peak_bytes"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in result["records"]:
            writer.writerow({key: record[key] for key in fields})


if __name__ == "__main__":
    main()
