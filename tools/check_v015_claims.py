"""Guard v0.15.0 claim language and verifier independence."""
from __future__ import annotations

from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    claim = (ROOT / "docs" / "V015_CLAIM_BOUNDARY.md").read_text(encoding="utf-8")
    contract = (ROOT / "V015_FINITE_CONVOLUTION_API_CONTRACT.md").read_text(encoding="utf-8")
    governed_text = claim + "\n" + contract
    required = ("product-count bounded", "post-input carry-drain-count bounded")
    for phrase in required:
        if phrase not in governed_text:
            raise SystemExit(f"missing required resource qualification: {phrase}")
    oracle_path = ROOT / "cnrs" / "validation" / "convolution_oracle.py"
    source = oracle_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        if any(name.endswith("convolution") for name in names):
            raise SystemExit("independent oracle imports production convolution")
    print("v0.15.0 claim and verifier-independence guards: PASS")


if __name__ == "__main__":
    main()
