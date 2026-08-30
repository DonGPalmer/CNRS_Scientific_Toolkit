"""Repository-level guards for the Lean/CNRS theorem-alignment layer.

These tests do not execute Lean. Lean runs in its own GitHub Actions job.
They protect the maintained formal-source identity, theorem crosswalk, and
Python theorem-registry metadata from silent drift.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from cnrs.theorem_alignment import TheoremStatus, get_theorem_record

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "formal" / "lean" / "CnrsQ2"
MODULE_ROOT = LEAN_ROOT / "CnrsQ2"
ALIGNMENT = ROOT / "docs" / "LEAN_FORMALIZATION_ALIGNMENT.md"

EXPECTED_MODULES = {
    "Basic.lean",
    "DigitAlphabet.lean",
    "HenselRoot.lean",
    "Embedding.lean",
    "Density.lean",
    "FieldLevel.lean",
    "DigitExpansion.lean",
}

EXPECTED_THEOREMS = {
    "norm_beta": "Basic.lean",
    "prime_beta": "Basic.lean",
    "digit_bijective": "DigitAlphabet.lean",
    "padicInt_is_beta_adic_completion": "Density.lean",
    "padic_is_beta_adic_completion_field": "FieldLevel.lean",
    "exists_unique_digitP": "DigitExpansion.lean",
    "exists_unique_reduction": "DigitExpansion.lean",
    "partialSum_digitSeq_spec": "DigitExpansion.lean",
    "tendsto_partialSum_digitSeq": "DigitExpansion.lean",
    "digitSeq_unique": "DigitExpansion.lean",
    "exists_unique_digit_expansion": "DigitExpansion.lean",
}

MANIFEST_ROW = re.compile(
    r"^\| `(?P<path>[^`]+)` \| (?P<bytes>[0-9,]+) \| `(?P<prefix>[0-9a-f]{16})…` \|$"
)
SORRY_TOKEN = re.compile(r"\b(?:sorry|sorryAx)\b")


def test_formal_project_files_present():
    assert (LEAN_ROOT / "lakefile.toml").is_file()
    assert (LEAN_ROOT / "lean-toolchain").is_file()
    assert (LEAN_ROOT / "CnrsQ2.lean").is_file()
    assert (LEAN_ROOT / "MANIFEST.md").is_file()
    assert EXPECTED_MODULES == {p.name for p in MODULE_ROOT.glob("*.lean")}


def test_crosswalk_references_real_theorems():
    alignment_text = ALIGNMENT.read_text(encoding="utf-8")
    for theorem, filename in EXPECTED_THEOREMS.items():
        source = (MODULE_ROOT / filename).read_text(encoding="utf-8")
        assert theorem in source, f"{theorem} missing from {filename}"
        assert theorem in alignment_text, f"{theorem} missing from crosswalk"


def test_governed_manifest_matches_checked_in_formal_tree():
    rows = {}
    for line in (LEAN_ROOT / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
        match = MANIFEST_ROW.match(line)
        if match:
            rows[match.group("path")] = (
                int(match.group("bytes").replace(",", "")),
                match.group("prefix"),
            )
    assert rows, "No source rows parsed from Lean MANIFEST.md"
    for rel, (expected_bytes, expected_prefix) in rows.items():
        path = LEAN_ROOT / rel
        data = path.read_bytes()
        assert len(data) == expected_bytes, f"byte-size drift: {rel}"
        assert hashlib.sha256(data).hexdigest().startswith(expected_prefix), f"hash drift: {rel}"


def test_formal_sources_have_no_sorry_tokens():
    for path in [LEAN_ROOT / "CnrsQ2.lean", *MODULE_ROOT.glob("*.lean")]:
        text = path.read_text(encoding="utf-8")
        assert not SORRY_TOKEN.search(text), f"sorry token found in {path.relative_to(ROOT)}"


def test_q2_theorem_registry_carries_formal_metadata():
    for name in (
        "CNRS Q2 beta-adic completion",
        "CNRS Q2 unique beta-adic digit expansion",
    ):
        record = get_theorem_record(name)
        assert record.status == TheoremStatus.THEOREM_BACKED
        assert record.formal_system == "Lean 4 / Mathlib 4.33.0"
        assert record.formal_source and record.formal_source.startswith("formal/lean/CnrsQ2")
        assert record.formal_status == "Lean-verified mathematical theorem"
