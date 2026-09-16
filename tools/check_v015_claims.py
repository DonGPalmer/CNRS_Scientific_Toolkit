"""Guard v0.15.0 claim language and verifier independence."""
from __future__ import annotations

from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]

PRODUCTION_CONVOLUTION_SYMBOLS = {
    "_convolution_values",
    "convolve_exact",
    "iter_convolution",
    "multiply_with_witness",
}

PUBLIC_CLAIM_FILES = (
    "README.md",
    "RELEASE_NOTES.md",
    "V015_IMPLEMENTATION_CANDIDATE_RECORD.md",
    "docs/V015_IMPLEMENTATION_STATUS.md",
    "docs/V015_PERFORMANCE_RESULTS.md",
)

PROHIBITED_RELEASE_ASSERTIONS = (
    "bounded total computational resources",
    "bounded total resources",
    "bounded elapsed time",
    "bounded total memory",
    "universally faster",
    "universal speed superiority",
    "universal memory superiority",
)


def validate_public_claim_text(relative: str, text: str) -> None:
    """Reject release-facing assertions that exceed the frozen resource claim."""
    lowered = text.lower()
    for phrase in PROHIBITED_RELEASE_ASSERTIONS:
        if phrase in lowered:
            raise ValueError(f"prohibited total-resource claim in {relative}: {phrase}")


def main() -> None:
    claim = (ROOT / "docs" / "V015_CLAIM_BOUNDARY.md").read_text(encoding="utf-8")
    contract = (ROOT / "V015_FINITE_CONVOLUTION_API_CONTRACT.md").read_text(encoding="utf-8")
    governed_text = claim + "\n" + contract
    required = ("product-count bounded", "post-input carry-drain-count bounded")
    for phrase in required:
        if phrase not in governed_text:
            raise SystemExit(f"missing required resource qualification: {phrase}")

    for relative in PUBLIC_CLAIM_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        try:
            validate_public_claim_text(relative, text)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

    oracle_path = ROOT / "cnrs" / "validation" / "convolution_oracle.py"
    source = oracle_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
            imported = set()
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module or ""]
            imported = {alias.name for alias in node.names}
        else:
            continue
        if any(name.endswith(".convolution") or name == "convolution" for name in modules):
            raise SystemExit("independent oracle imports production convolution")
        if imported & PRODUCTION_CONVOLUTION_SYMBOLS:
            raise SystemExit("independent oracle imports a production convolution symbol")

    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_calls = called & PRODUCTION_CONVOLUTION_SYMBOLS
    if forbidden_calls:
        raise SystemExit(
            "independent oracle calls production convolution symbols: "
            + ", ".join(sorted(forbidden_calls))
        )
    print("v0.15.0 claim and verifier-independence guards: PASS")


if __name__ == "__main__":
    main()
