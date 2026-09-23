"""Guard v0.18 exact routes, oracle independence, and frozen identities."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORMAL_TREE = "d3ee7c7fd6648812966f3aaa4f700acbc40e223f"
TRANSITION_SHA256 = "b68818cdb0766aead9993639ca2f1b96351371154c94453e730bf9a67a0746ee"
PACKET_HASHES = {
    "V018_ARCHITECTURE_FREEZE.md": "885c93e4e530cafc64c59d16451b156a0c949fe80c794c2da49519d2693398f8",
    "V018_EXACT_ADDITION_SUBTRACTION_API_CONTRACT.md": "1acc7dafda1bee31aa2e1be1391d8f123554a8019e431523d842a394f2c3a003",
    "acceptance/v018/README.md": "3c5270f84c1451f02ba14e6b0c8ee66e4ed93b004aa1ab3f97277ff94d180421",
}
EVIDENCE_TEST_PATHS = (
    "acceptance/v018/test_exact_addition_subtraction_contract.py",
    "tests/test_v018_exact_addition_subtraction.py",
)
EVIDENCE_CONSTANTS = {
    "LONG_PAIR_COUNT": 100,
    "LONG_MAX_DIGITS": 1000,
    "LONG_LAW_COUNT": 100,
}
EVIDENCE_TESTS = {
    "test_a05_one_hundred_long_input_pairs_to_one_thousand_digits",
    "test_a10_one_hundred_randomized_longer_domain_law_triples",
    "test_a10_exhaustive_short_and_randomized_longer_domain_laws",
    "test_a13_fractional_direct_and_cval_route_parity",
}


class ClaimGuardError(RuntimeError):
    pass


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ClaimGuardError(f"missing function {name}")


def _guard_exact_production() -> None:
    add_tree = ast.parse((ROOT / "cnrs/cnrs_add.py").read_text())
    for name in ("_build_addition_table", "add_cnrs"):
        function = _function(add_tree, name)
        calls = {node.func.id for node in ast.walk(function) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        attrs = {node.attr for node in ast.walk(function) if isinstance(node, ast.Attribute)}
        if calls & {"complex", "float", "round", "cnrs_remainder"} or attrs & {"real", "imag"}:
            raise ClaimGuardError(f"{name} uses an approximate or value-map route")
        if any(isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) for node in ast.walk(function)):
            raise ClaimGuardError(f"{name} uses nonintegral division")

    ops = (ROOT / "cnrs/cnrs_ops.py").read_text()
    if "return mul_cnrs(_NEGATIVE_ONE, a)" not in ops:
        raise ClaimGuardError("accepted negation does not route through exact multiplication")
    if "return add_cnrs(a, cnrs_neg(b))" not in ops:
        raise ClaimGuardError("accepted subtraction does not route through exact addition")
    if "if _is_finite_cnrs_string(a) and _is_finite_cnrs_string(b):" not in ops:
        raise ClaimGuardError("compatibility subtraction lane is not grammar-separated")
    if "from .cnrs_add import add_cnrs" not in ops:
        raise ClaimGuardError("operations do not reuse the single addition relation")


def _guard_oracle_independence() -> None:
    source = (ROOT / "cnrs/validation/exact_addition_subtraction_oracle.py").read_text()
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    if any(name.startswith("cnrs") for name in imports):
        raise ClaimGuardError("independent oracle imports production code")
    identifiers = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    prohibited = {"add_cnrs", "cnrs_add", "cnrs_neg", "cnrs_sub", "mul_cnrs", "complex", "float", "round"}
    if identifiers & prohibited:
        raise ClaimGuardError("independent oracle calls a prohibited operation")


def _guard_transition_identity() -> None:
    from cnrs.cnrs_add import ADDITION_TABLE, CARRY_SET_PAIRS

    payload = {
        "carry_set_pairs": CARRY_SET_PAIRS,
        "transitions": [(*key, *value) for key, value in sorted(ADDITION_TABLE.items())],
    }
    digest = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
    if digest != TRANSITION_SHA256:
        raise ClaimGuardError(f"transition checksum drift: {digest}")


def _guard_committed_acceptance_evidence() -> None:
    for path in EVIDENCE_TEST_PATHS:
        source = (ROOT / path).read_text()
        tree = ast.parse(source)
        functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        required_tests = {
            "test_a05_one_hundred_long_input_pairs_to_one_thousand_digits",
            "test_a13_fractional_direct_and_cval_route_parity",
        }
        required_tests.add(
            "test_a10_exhaustive_short_and_randomized_longer_domain_laws"
            if path.startswith("acceptance/")
            else "test_a10_one_hundred_randomized_longer_domain_law_triples"
        )
        if not required_tests <= functions.keys():
            missing = sorted(required_tests - functions.keys())
            raise ClaimGuardError(f"missing committed v0.18 evidence in {path}: {missing}")

        assignments = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                try:
                    assignments[node.targets[0].id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    pass
        for name, expected in EVIDENCE_CONSTANTS.items():
            if assignments.get(name) != expected:
                raise ClaimGuardError(f"{path} does not freeze {name}={expected}")
        vectors = assignments.get("FRACTIONAL_CVAL_VECTORS")
        if not isinstance(vectors, tuple) or len(vectors) < 4:
            raise ClaimGuardError(f"{path} has fewer than four fractional CVal vectors")

        imports_cval = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "cnrs.cnrs_value"
            and any(alias.name == "CVal" for alias in node.names)
            for node in tree.body
        )
        if not imports_cval:
            raise ClaimGuardError(f"{path} does not import CVal for A13 parity")

        evidence_nodes = [functions[name] for name in required_tests]
        if "_assert_a10_laws" in functions:
            evidence_nodes.append(functions["_assert_a10_laws"])
        identifiers = {
            node.id
            for function in evidence_nodes
            for node in ast.walk(function)
            if isinstance(node, ast.Name)
        }
        required_identifiers = {
            "LONG_PAIR_COUNT", "LONG_MAX_DIGITS", "LONG_LAW_COUNT",
            "FRACTIONAL_CVAL_VECTORS", "CVal", "exact_string_value",
            "exact_sum_value", "exact_negated_value", "exact_difference_value",
        }
        if not required_identifiers <= identifiers:
            missing = sorted(required_identifiers - identifiers)
            raise ClaimGuardError(f"{path} evidence omits required independent routes: {missing}")


def _guard_identities() -> None:
    for path, expected in PACKET_HASHES.items():
        observed = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if observed != expected:
            raise ClaimGuardError(f"adopted packet drift: {path}: {observed}")
    observed_formal = subprocess.check_output(["git", "rev-parse", "HEAD:formal"], cwd=ROOT, text=True).strip()
    if observed_formal != FORMAL_TREE:
        raise ClaimGuardError(f"formal subtree drift: {observed_formal}")


def main() -> int:
    _guard_exact_production()
    _guard_oracle_independence()
    _guard_transition_identity()
    _guard_committed_acceptance_evidence()
    _guard_identities()
    print("v0.18 claim guard: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
