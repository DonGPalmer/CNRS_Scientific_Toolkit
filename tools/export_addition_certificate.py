"""Reproduce the finite addition fixture from pinned authoritative CI evidence."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

ARTIFACT_SHA256 = "4cecf1ae810503c8b9fb11bc723cbf1ab9fcab17c13f13956dc20afa253f8fe0"
SOURCE_ZIP_SHA256 = "62f295b730fc0c90bc51b418e763a5444bfa56966a2e11373c0c3aae2764c69b"
LEAN_SOURCE_SHA256 = "4f87aa2ed0eb2a9a3727f8598331966b642df613b21eff9538a8e114096da0dc"
RUNNER_SOURCE_SHA256 = "4d3e5acb3ac9b4aea99ac6b78e9e82c4a9c1c44ca7883697ab316b194b043bee"


def export_certificate(evidence: Path, output: Path) -> None:
    data = evidence.read_bytes()
    if hashlib.sha256(data).hexdigest() != ARTIFACT_SHA256:
        raise ValueError("authoritative evidence artifact digest mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as artifact:
        archive = artifact.read("authoritative/e2/live-source.zip")
        if hashlib.sha256(archive).hexdigest() != SOURCE_ZIP_SHA256:
            raise ValueError("installed source archive digest mismatch")
        with zipfile.ZipFile(io.BytesIO(archive)) as source:
            lean = source.read("CNRSIntegration/CNRSIntegration/ToolkitTransitionTable.lean")
            runner = source.read("CNRSIntegration/CNRSIntegration/ToolkitRunner.lean")
    if hashlib.sha256(lean).hexdigest() != LEAN_SOURCE_SHA256:
        raise ValueError("checked Lean module digest mismatch")
    if hashlib.sha256(runner).hexdigest() != RUNNER_SOURCE_SHA256:
        raise ValueError("checked runner module digest mismatch")
    text = lean.decode("utf-8")
    carries_text = text.split("def pythonCarries : List GaussianInt :=", 1)[1].split("def pythonRows", 1)[0]
    rows_text = text.split("def pythonRows : List (Nat × Nat) :=", 1)[1].split("def carryAt", 1)[0]
    carries = [[int(a.strip("()")), int(b.strip("()"))] for a, b in
               re.findall(r"gi (\(?-?\d+\)?) (\(?-?\d+\)?)", carries_text)]
    values = [[int(d), int(n)] for d, n in re.findall(r"\((\d+), (\d+)\)", rows_text)]
    if len(carries) != 14 or len(values) != 350:
        raise ValueError("checked Lean literal format or inventory changed")
    rows = [[q, a, b, *values[q * 25 + a * 5 + b]]
            for q in range(14) for a in range(5) for b in range(5)]
    lengths = []
    for q in range(14):
        state, seen = q, set()
        while state != 0:
            if state in seen:
                raise ValueError("cycle in captured zero-input drain")
            seen.add(state)
            state = values[state * 25][1]
        lengths.append(len(seen))
    result = {
        "schema": "cnrs.finite-addition-certificate.v1",
        "provenance": {
            "status": "installed_authoritatively_verified_E2_candidate; final adoption pending",
            "repository": "DonGPalmer/SSC_Formal_Methods_CI",
            "commit": "03e40d19348694b470897b6c6434e38ccc841250",
            "run_id": 39331704917,
            "artifact_id": 12224872876,
            "artifact_sha256": ARTIFACT_SHA256,
            "installed_source_zip_sha256": SOURCE_ZIP_SHA256,
            "lean_module": "CNRSIntegration/CNRSIntegration/ToolkitTransitionTable.lean",
            "lean_module_sha256": LEAN_SOURCE_SHA256,
            "runner_module": "CNRSIntegration/CNRSIntegration/ToolkitRunner.lean",
            "runner_module_sha256": RUNNER_SOURCE_SHA256,
            "captured_python_source_sha256": "b2ad3ae14f6cf905e36a7c4f3db446938445a070288ae5cafd97209bb2287d47",
            "theorems": ["CNRSIntegration.ToolkitTransition." + name for name in (
                "table_matches_addStep", "table_value_equation", "table_drain_five",
                "table_drain_four_insufficient", "tableRun_refines",
                "tableRun_append_drain", "tableRun_drained_value")],
        },
        "carry_pairs": carries,
        "rows": rows,
        "zero_input_drain_lengths": lengths,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export_certificate(args.evidence, args.output)
