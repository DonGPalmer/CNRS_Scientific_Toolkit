"""Dependency-free local guard for the maintained Lean integration tree.

This checks source identity and token hygiene; it does not replace `lake build`.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lean_root = root / "formal" / "lean" / "CnrsQ2"
modules = lean_root / "CnrsQ2"
expected = [
    "Basic.lean", "DigitAlphabet.lean", "HenselRoot.lean", "Embedding.lean",
    "Density.lean", "FieldLevel.lean", "DigitExpansion.lean",
]
missing = [p for p in expected if not (modules / p).is_file()]
if missing:
    raise SystemExit("FAIL missing Lean modules: " + ", ".join(missing))

sorry_token = re.compile(r"\b(?:sorry|sorryAx)\b")
for path in [lean_root / "CnrsQ2.lean", *(modules / p for p in expected)]:
    text = path.read_text(encoding="utf-8")
    if sorry_token.search(text):
        raise SystemExit(f"FAIL sorry token: {path.relative_to(root)}")

row_re = re.compile(
    r"^\| `(?P<path>[^`]+)` \| (?P<bytes>[0-9,]+) \| `(?P<prefix>[0-9a-f]{16})…` \|$"
)
rows = {}
for line in (lean_root / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
    m = row_re.match(line)
    if m:
        rows[m.group("path")] = (int(m.group("bytes").replace(",", "")), m.group("prefix"))
if not rows:
    raise SystemExit("FAIL no source rows parsed from Lean MANIFEST.md")
for rel, (size, prefix) in rows.items():
    data = (lean_root / rel).read_bytes()
    if len(data) != size or not hashlib.sha256(data).hexdigest().startswith(prefix):
        raise SystemExit(f"FAIL manifest mismatch: formal/lean/CnrsQ2/{rel}")

print("PASS Lean integration structure, governed manifest, and source-token checks")
