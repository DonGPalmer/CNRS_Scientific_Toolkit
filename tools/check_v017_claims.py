"""Guard v0.17 exact-route, oracle independence, and frozen identities."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORMAL_TREE = "d3ee7c7fd6648812966f3aaa4f700acbc40e223f"
PACKET_HASHES = {
    "V017_ARCHITECTURE_FREEZE.md":
        "cd7a5887eee7176c59e9de0533ed029fc41b81f3003e957c7fa3cb32d0b0c432",
    "V017_EXACT_DIVISION_API_CONTRACT.md":
        "98f4c3b628cc113411abf26f1b949f016d8679ea595b706002f458d7cf28c050",
    "acceptance/v017/README.md":
        "c7c8f30a4b061d2c4d2130b7070b662e4402d084c3f75b457e7e5750989042c2",
}
PRODUCTION_PATH = "cnrs/exact_division.py"
ORACLE_PATH = "cnrs/validation/exact_division_oracle.py"
PROHIBITED_PRODUCTION_MODULES = {
    "cnrs.validation",
    "validation",
    "cnrs.cnrs_div",
    "cnrs_div",
    "cnrs.canonical_periodic",
    "canonical_periodic",
    "cnrs.witnesses",
    "witnesses",
}
PROHIBITED_PRODUCTION_SYMBOLS = {
    "CanonicalPeriodicExpansion",
    "CycleWitness",
    "division_witness",
    "primitive_period",
    "validate_division_witness",
    "_witness_from_resolution",
}
PROHIBITED_PRODUCTION_ATTRIBUTES = {
    "allclose",
    "from_gaussian_fraction",
    "isclose",
    "to_witness",
    "validate_division_witness",
}
PROHIBITED_WITNESS_LITERALS = {
    "algorithm",
    "cnrs-division-witness-v1",
    "cnrs-gaussian-rational-stream-v1",
    "schema",
}
PROHIBITED_ORACLE_MODULES = {
    "cnrs.exact_division",
    "exact_division",
    "cnrs.finite_sequence",
    "finite_sequence",
    "cnrs.finite_string",
    "finite_string",
    "cnrs.streaming_division",
    "streaming_division",
    "cnrs.canonical_periodic",
    "canonical_periodic",
    "cnrs.witnesses",
    "witnesses",
}
PROHIBITED_ORACLE_SYMBOLS = {
    "divide_cnrs_exact",
    "_finite_value_fraction",
    "cnrs_string_to_finite_sequence",
    "stream_division",
    "CanonicalPeriodicExpansion",
    "division_witness",
    "validate_division_witness",
}


class ClaimGuardError(RuntimeError):
    """A frozen v0.17 architecture or identity claim was violated."""


def _parse_source(source: str, name: str) -> ast.AST:
    return ast.parse(source, filename=name)


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


def guard_production_source(source: str) -> None:
    tree = _parse_source(source, PRODUCTION_PATH)
    modules, symbols = _imports(tree)
    if any(
        module == prohibited or module.startswith(prohibited + ".")
        for module in modules
        for prohibited in PROHIBITED_PRODUCTION_MODULES
    ):
        raise ClaimGuardError(
            "production imports validation, legacy division, canonical, or witness code"
        )
    if symbols & PROHIBITED_PRODUCTION_SYMBOLS:
        raise ClaimGuardError("production imports canonical or witness operations")

    called = _called_names(tree)
    if called & {"complex", "float", "round"}:
        raise ClaimGuardError("production uses approximate numeric construction")
    if any(
        isinstance(node, ast.Constant) and type(node.value) is float
        for node in ast.walk(tree)
    ):
        raise ClaimGuardError("production uses a floating literal or tolerance")
    if any(isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
           for node in ast.walk(tree)):
        raise ClaimGuardError("production uses numeric division")
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    if attributes & {"real", "imag"}:
        raise ClaimGuardError("production uses floating complex components")
    if called & {"isclose", "allclose"} or attributes & {"isclose", "allclose"}:
        raise ClaimGuardError("production uses a floating tolerance comparison")
    if any(
        isinstance(node, (ast.For, ast.AsyncFor, ast.While, ast.comprehension))
        for node in ast.walk(tree)
    ):
        raise ClaimGuardError("production duplicates arithmetic iteration")
    if called & PROHIBITED_PRODUCTION_SYMBOLS:
        raise ClaimGuardError("production calls canonical or witness operations")
    if attributes & PROHIBITED_PRODUCTION_ATTRIBUTES:
        raise ClaimGuardError("production reaches canonical or witness operations")

    identifiers = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {
        node.arg for node in ast.walk(tree) if isinstance(node, ast.arg)
    } | {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if any("witness" in identifier.lower() for identifier in identifiers):
        raise ClaimGuardError("production inspects, trusts, or mutates witness data")
    if any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value in PROHIBITED_WITNESS_LITERALS
        for node in ast.walk(tree)
    ):
        raise ClaimGuardError("production defines or mutates witness identity fields")
    if "finite_sequence_to_cnrs_string" in called or "str" in {
        getattr(node.returns, "id", "")
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "divide_cnrs_exact"
    }:
        raise ClaimGuardError("production returns a finite-string approximation")

    required_calls = {
        "cnrs_string_to_finite_sequence",
        "gmul",
        "stream_division",
    }
    if not required_calls <= called or "resolve" not in attributes:
        raise ClaimGuardError("production does not delegate through the frozen route")


def guard_oracle_source(source: str) -> None:
    tree = _parse_source(source, ORACLE_PATH)
    modules, symbols = _imports(tree)
    if modules & PROHIBITED_ORACLE_MODULES:
        raise ClaimGuardError("oracle imports a prohibited production module")
    if symbols & PROHIBITED_ORACLE_SYMBOLS:
        raise ClaimGuardError("oracle imports a prohibited production operation")
    if _called_names(tree) & PROHIBITED_ORACLE_SYMBOLS:
        raise ClaimGuardError("oracle calls a prohibited production operation")


def _guard_legacy_boundary() -> None:
    tree = _parse_source((ROOT / "cnrs/cnrs_div.py").read_text(encoding="utf-8"),
                         "cnrs/cnrs_div.py")
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    function = functions.get("div_cnrs")
    if function is None:
        raise ClaimGuardError("legacy div_cnrs is missing")
    if [arg.arg for arg in function.args.args] != ["a", "b"]:
        raise ClaimGuardError("legacy div_cnrs signature changed")
    warning_calls = [
        node for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "warnings"
        and node.func.attr == "warn"
    ]
    if len(warning_calls) != 1:
        raise ClaimGuardError("legacy div_cnrs must warn exactly once on call")
    top_level_warning = [
        node for node in tree.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and node.value.func.attr == "warn"
    ]
    if top_level_warning:
        raise ClaimGuardError("legacy warning occurs during import")


def _guard_packet_and_formal_tree() -> None:
    for relative, expected in PACKET_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ClaimGuardError(f"approved packet identity changed: {relative}")
    actual_tree = subprocess.run(
        ["git", "rev-parse", "HEAD:formal"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual_tree != FORMAL_TREE:
        raise ClaimGuardError(f"formal subtree changed: {actual_tree}")


def main() -> None:
    guard_production_source((ROOT / PRODUCTION_PATH).read_text(encoding="utf-8"))
    guard_oracle_source((ROOT / ORACLE_PATH).read_text(encoding="utf-8"))
    _guard_legacy_boundary()
    _guard_packet_and_formal_tree()
    print("v0.17.0 exact-route, oracle-independence, and identity guards: PASS")


if __name__ == "__main__":
    main()
