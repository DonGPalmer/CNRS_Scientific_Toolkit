"""Repository guards for the CNRS-LEAN-CAPSTONE alignment layer."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cnrs.theorem_alignment import TheoremStatus, get_theorem_record

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "formal"
PROJECTS = (
    "CNRSCore", "CnrsQ2", "CNRSArithmetic",
    "CNRSIntegration", "CNRSProblem1", "CNRSProblem2",
)


def test_capstone_alignment_guard():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_lean_alignment.py")],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS CNRS-LEAN-CAPSTONE" in result.stdout


def test_capstone_provenance():
    data = json.loads((FORMAL / "PROVENANCE.json").read_text())
    release = data["consolidated_release"]
    assert release["commit"] == "07e776b4e1d7d09513394a4b676516eb51e4c597"
    assert release["tree"] == "fd61bac37369f8e3020d70141c565a4fba414a98"
    assert release["workflow_run"] == 34534566879
    assert release["workflow_job"] == 103063055916
    assert release["artifact_id"] == 10175389923
    assert release["lean_source_files"] == 79
    assert [p["name"] for p in data["projects"]] == list(PROJECTS)
    public = data["public_release"]
    assert public["repository"] == "DonGPalmer/CNRS_Lean"
    assert public["release"] == "v1.0.3"
    assert public["commit"] == "ce56a7359f494d29bab8e9bea6c3ea596f8fd62f"
    assert public["zenodo_version_doi"] == "10.5281/zenodo.22727725"
    assert public["zenodo_concept_doi"] == "10.5281/zenodo.22726349"


def test_capstone_theorem_boundaries_documented():
    inventory = (FORMAL / "docs" / "GOVERNED_THEOREM_INVENTORY.md").read_text()
    crosswalk = (FORMAL / "docs" / "TOOLKIT_LEAN_CROSSWALK.md").read_text()
    for marker in ("P1-L1–L7", "P2-L1–L10", "Phase F"):
        assert marker in inventory
    for source in ("CNRSIntegration.lean", "FiniteHurwitzAntiderivative.lean"):
        assert source in inventory
    for exclusion in (
        "infinite-series serialization", "analytic continuation",
        "unequal-branch arithmetic", "streaming multiplication/division",
    ):
        assert exclusion in crosswalk


def test_q2_registry_retains_formal_metadata():
    for name in (
        "CNRS Q2 beta-adic completion",
        "CNRS Q2 unique beta-adic digit expansion",
    ):
        record = get_theorem_record(name)
        assert record.status == TheoremStatus.THEOREM_BACKED
        assert record.formal_system == "Lean 4 / Mathlib 4.33.0"
        assert record.formal_source and record.formal_source.startswith("formal/lean/CnrsQ2")

