"""Guard the v0.16 exact-route, oracle independence, and frozen identities."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORMAL_TREE = "d3ee7c7fd6648812966f3aaa4f700acbc40e223f"
PACKET_HASHES = {
    "V016_ARCHITECTURE_FREEZE.md": "f40faffeeb60cabb3e321c971049eb4a3e9d883805cb67727fa94bcc7ff20a38",
    "V016_EXACT_MULTIPLICATION_API_CONTRACT.md": "9a686032c2fca313573c78f35d9a1ca6da6bef73d694b219fa6a7a67a3ee631e",
    "acceptance/v016/README.md": "907edf2c00ee4812e5d987094fc7a69a8bac778fef8a248a8d76f2652a081bd8",
}
PRODUCTION_OPERATIONS = {
    "convolve_exact",
    "normalize_gaussian_laurent",
    "multiply_with_witness",
    "mul_cnrs",
    "cnrs_string_to_finite_sequence",
    "finite_sequence_to_cnrs_string",
}


def _tree(relative: str) -> ast.AST:
    return ast.parse((ROOT / relative).read_text(encoding="utf-8"), filename=relative)


def _imports(tree: ast.AST) -> tuple[set[str], set[str]]:
    modules: set[str] = set()
    symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
            symbols.update(alias.name for alias in node.names)
    return modules, symbols


def _called_names(tree: ast.AST) -> set[str]:
    return {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def _guard_no_duplicate_arithmetic(relative: str, tree: ast.AST) -> None:
    """Reject production-local convolution or carry recurrences.

    The bridge has one permitted coefficient-validation loop. Every other
    explicit loop, every while loop, and every multi-generator comprehension
    is outside the frozen parse/format responsibility.
    """
    explicit_loops = [
        node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.AsyncFor))
    ]
    while_loops = [node for node in ast.walk(tree) if isinstance(node, ast.While)]
    nested_comprehensions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp))
        and len(node.generators) > 1
    ]
    if while_loops or nested_comprehensions:
        raise SystemExit(f"{relative} duplicates arithmetic iteration")

    if relative == "cnrs_mul.py":
        if explicit_loops:
            raise SystemExit(f"{relative} duplicates arithmetic iteration")
        return

    if len(explicit_loops) != 1:
        raise SystemExit(f"{relative} has an unexpected explicit loop")
    loop = explicit_loops[0]
    unpack = loop.body[0] if loop.body else None
    if not (
        isinstance(loop.target, ast.Name)
        and loop.target.id == "coefficient"
        and isinstance(loop.iter, ast.Attribute)
        and isinstance(loop.iter.value, ast.Name)
        and loop.iter.value.id == "value"
        and loop.iter.attr == "coefficients"
        and not loop.orelse
        and len(loop.body) == 2
        and isinstance(unpack, ast.Assign)
        and len(unpack.targets) == 1
        and isinstance(unpack.targets[0], ast.Tuple)
        and [
            element.id
            for element in unpack.targets[0].elts
            if isinstance(element, ast.Name)
        ]
        == ["real", "imaginary"]
        and isinstance(unpack.value, ast.Name)
        and unpack.value.id == "coefficient"
        and isinstance(loop.body[1], ast.If)
    ):
        raise SystemExit(f"{relative} loop is not the frozen coefficient validator")


def _guard_production() -> None:
    multiplication = _tree("cnrs/cnrs_mul.py")
    bridge = _tree("cnrs/finite_string.py")
    for relative, tree in (("cnrs_mul.py", multiplication), ("finite_string.py", bridge)):
        modules, _ = _imports(tree)
        if any("validation" in module for module in modules):
            raise SystemExit(f"{relative} imports validation code")
        if _called_names(tree) & {"complex", "round"}:
            raise SystemExit(f"{relative} uses complex or round")
        if any(
            isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
            for node in ast.walk(tree)
        ):
            raise SystemExit(f"{relative} uses division")
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        if attributes & {"real", "imag"}:
            raise SystemExit(f"{relative} uses floating complex components")
        _guard_no_duplicate_arithmetic(relative, tree)

    called = _called_names(multiplication)
    required = {
        "cnrs_string_to_finite_sequence",
        "convolve_exact",
        "normalize_gaussian_laurent",
        "finite_sequence_to_cnrs_string",
    }
    if not required <= called:
        raise SystemExit("mul_cnrs does not use every frozen exact-route operation")
def _guard_oracle(relative: str) -> None:
    tree = _tree(relative)
    modules, symbols = _imports(tree)
    prohibited_modules = {
        "cnrs.cnrs_mul",
        "cnrs.convolution",
        "cnrs.gaussian_normalization",
        "cnrs.finite_string",
    }
    if modules & prohibited_modules or symbols & PRODUCTION_OPERATIONS:
        raise SystemExit(f"{relative} imports a prohibited production operation")
    if _called_names(tree) & PRODUCTION_OPERATIONS:
        raise SystemExit(f"{relative} calls a prohibited production operation")


def _guard_packet_and_formal_tree() -> None:
    for relative, expected in PACKET_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"approved packet identity changed: {relative}")
    actual_tree = subprocess.run(
        ["git", "rev-parse", "HEAD:formal"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual_tree != FORMAL_TREE:
        raise SystemExit(f"formal subtree changed: {actual_tree}")


def main() -> None:
    _guard_production()
    _guard_oracle("cnrs/validation/legacy_string_multiplication.py")
    _guard_oracle("cnrs/validation/exact_string_oracle.py")
    _guard_packet_and_formal_tree()
    print("v0.16.0 exact-route, oracle-independence, and identity guards: PASS")


if __name__ == "__main__":
    main()
