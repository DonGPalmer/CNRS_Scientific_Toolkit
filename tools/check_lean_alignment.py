"""Verify the vendored CNRS-LEAN-CAPSTONE source identity and proof hygiene."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "formal" / "lean"
CAPSTONE_ROOT = ROOT / "formal" / "capstone"
PROJECTS = (
    "CNRSCore", "CnrsQ2", "CNRSArithmetic",
    "CNRSIntegration", "CNRSProblem1", "CNRSProblem2",
)
EXPECTED_ARTIFACT_SHA256 = (
    "840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21"
)
FORBIDDEN = {
    "sorry": re.compile(r"\bsorry\b"),
    "sorryAx": re.compile(r"\bsorryAx\b"),
    "admit": re.compile(r"\badmit\b"),
    "axiom declaration": re.compile(r"^\s*axiom\s+", re.MULTILINE),
    "unsafe declaration": re.compile(r"^\s*unsafe\s+", re.MULTILINE),
}

for project in PROJECTS:
    root = LEAN_ROOT / project
    for required in ("lakefile.toml", "lake-manifest.json", "lean-toolchain"):
        if not (root / required).is_file():
            raise SystemExit(f"FAIL missing {project}/{required}")

provenance = json.loads((ROOT / "formal" / "PROVENANCE.json").read_text())
release = provenance["consolidated_release"]
if release["artifact_sha256"] != EXPECTED_ARTIFACT_SHA256:
    raise SystemExit("FAIL capstone artifact identity drift")
if [p["name"] for p in provenance["projects"]] != list(PROJECTS):
    raise SystemExit("FAIL project inventory drift")

inventory = {}
for line in (CAPSTONE_ROOT / "SHA256SUMS.txt").read_text().splitlines():
    digest, rel = line.split(maxsplit=1)
    rel = rel.removeprefix("./")
    if rel.startswith("release/"):
        inventory[rel.removeprefix("release/")] = digest

if not inventory:
    raise SystemExit("FAIL no release inventory entries")

actual_files = {
    p.relative_to(LEAN_ROOT).as_posix()
    for p in LEAN_ROOT.rglob("*")
    if p.is_file()
}
if set(inventory) != actual_files:
    missing = sorted(set(inventory) - actual_files)
    extra = sorted(actual_files - set(inventory))
    raise SystemExit(f"FAIL inventory mismatch missing={missing} extra={extra}")

for rel, expected in inventory.items():
    data = (LEAN_ROOT / rel).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit(f"FAIL checksum mismatch: {rel}")

lean_files = sorted(LEAN_ROOT.rglob("*.lean"))
if len(lean_files) != 79:
    raise SystemExit(f"FAIL expected 79 Lean files, found {len(lean_files)}")
for path in lean_files:
    text = path.read_text(encoding="utf-8")
    for label, pattern in FORBIDDEN.items():
        if pattern.search(text):
            raise SystemExit(f"FAIL {label}: {path.relative_to(ROOT)}")

print("PASS CNRS-LEAN-CAPSTONE: six projects, exact inventory, 79 Lean files, clean proof markers")
