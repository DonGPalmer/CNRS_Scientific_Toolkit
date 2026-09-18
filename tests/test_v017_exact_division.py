"""Dedicated tests for the v0.17 exact finite-string division bridge."""
from __future__ import annotations

from fractions import Fraction
import importlib.util
import inspect
from pathlib import Path
import warnings

import pytest

import cnrs
from cnrs.cnrs_div import div_cnrs
from cnrs.exact_division import divide_cnrs_exact
from cnrs.streaming_division import (
    DivisionResolution,
    DivisionSearchLimitError,
    DivisionStreamStatus,
)
from cnrs.validation.exact_division_oracle import exact_quotient_value
from cnrs.witnesses import validate_division_witness
ROOT = Path(__file__).resolve().parents[1]
_GUARD_SPEC = importlib.util.spec_from_file_location(
    "check_v017_claims", ROOT / "tools/check_v017_claims.py"
)
assert _GUARD_SPEC is not None and _GUARD_SPEC.loader is not None
_GUARD = importlib.util.module_from_spec(_GUARD_SPEC)
_GUARD_SPEC.loader.exec_module(_GUARD)
ClaimGuardError = _GUARD.ClaimGuardError
guard_oracle_source = _GUARD.guard_oracle_source
guard_production_source = _GUARD.guard_production_source


def _fraction_value(
    numerator: tuple[int, int], denominator: tuple[int, int]
) -> tuple[Fraction, Fraction]:
    a, b = numerator
    c, d = denominator
    norm = c * c + d * d
    return Fraction(a * c + b * d, norm), Fraction(b * c - a * d, norm)


def test_public_signature_export_and_result_type() -> None:
    assert str(inspect.signature(divide_cnrs_exact)) == (
        "(dividend: 'str', divisor: 'str', *, max_steps: 'int' = 100000) "
        "-> 'DivisionResolution'"
    )
    assert cnrs.divide_cnrs_exact is divide_cnrs_exact
    assert "divide_cnrs_exact" in cnrs.__all__
    assert isinstance(divide_cnrs_exact("1", "1"), DivisionResolution)


@pytest.mark.parametrize(
    ("dividend", "divisor", "status", "value"),
    [
        ("0", "1", DivisionStreamStatus.TERMINATING, (Fraction(0), Fraction(0))),
        ("1", "1", DivisionStreamStatus.TERMINATING, (Fraction(1), Fraction(0))),
        ("1", "10", DivisionStreamStatus.TERMINATING,
         (Fraction(-2, 5), Fraction(-1, 5))),
        (".1", "1", DivisionStreamStatus.TERMINATING,
         (Fraction(-2, 5), Fraction(-1, 5))),
        (".1", ".1", DivisionStreamStatus.TERMINATING,
         (Fraction(1), Fraction(0))),
        ("23.1", "1.", DivisionStreamStatus.TERMINATING,
         exact_quotient_value("23.1", "1.")),
        ("1", "2", DivisionStreamStatus.EVENTUALLY_PERIODIC,
         (Fraction(1, 2), Fraction(0))),
        ("1", "3", DivisionStreamStatus.EVENTUALLY_PERIODIC,
         (Fraction(1, 3), Fraction(0))),
        ("1", "4", DivisionStreamStatus.EVENTUALLY_PERIODIC,
         (Fraction(1, 4), Fraction(0))),
        ("1", "11", DivisionStreamStatus.EVENTUALLY_PERIODIC,
         exact_quotient_value("1", "11")),
        ("1", "20", DivisionStreamStatus.EVENTUALLY_PERIODIC,
         exact_quotient_value("1", "20")),
    ],
)
def test_frozen_fixed_vectors(dividend, divisor, status, value) -> None:
    result = divide_cnrs_exact(dividend, divisor)
    assert result.status is status
    assert result.exact_value_fractions() == value
    assert _fraction_value(result.numerator, result.denominator) == value
    witness = result.to_witness()
    assert validate_division_witness(witness) == witness


def test_periodic_and_shifted_details_are_exact() -> None:
    periodic = divide_cnrs_exact("1", "2")
    assert periodic.prefix_digits == ()
    assert periodic.period_digits == (3, 2)
    assert periodic.power_offset == 0
    assert periodic.witness is not None

    shifted = divide_cnrs_exact("1", "20")
    assert shifted.period_digits == (3, 2)
    assert shifted.power_offset == -1
    assert shifted.witness is not None


def test_limit_is_operational_and_has_no_witness() -> None:
    result = divide_cnrs_exact("1", "2", max_steps=1)
    assert result.status is DivisionStreamStatus.LIMIT_REACHED
    assert result.steps == 1
    assert result.prefix_digits == (3,)
    assert result.witness is None
    assert not result.resolved and not result.terminates
    with pytest.raises(DivisionSearchLimitError):
        result.exact_value_fractions()
    with pytest.raises(DivisionSearchLimitError):
        result.to_witness()


@pytest.mark.parametrize("bad", [None, 1, 1.0, True, b"1"])
def test_operand_types_are_inherited_from_frozen_parser(bad: object) -> None:
    with pytest.raises(TypeError):
        divide_cnrs_exact(bad, "1")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        divide_cnrs_exact("1", bad)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "bad", ["", ".", "5", "-1", "+1", " 1", "1 ", "1e2", "1..2"]
)
def test_malformed_operands_are_rejected(bad: str) -> None:
    with pytest.raises(ValueError):
        divide_cnrs_exact(bad, "1")
    with pytest.raises(ValueError):
        divide_cnrs_exact("1", bad)


@pytest.mark.parametrize("zero", ["0", "00", "0.", ".0", "0.000"])
def test_all_zero_spellings_raise(zero: str) -> None:
    with pytest.raises(ZeroDivisionError):
        divide_cnrs_exact("1", zero)


@pytest.mark.parametrize("bad", [True, 1.0, "1", None])
def test_max_steps_requires_exact_int(bad: object) -> None:
    with pytest.raises(TypeError):
        divide_cnrs_exact("1", "2", max_steps=bad)  # type: ignore[arg-type]
    for invalid in (0, -1):
        with pytest.raises(ValueError):
            divide_cnrs_exact("1", "2", max_steps=invalid)


def test_equivalent_spellings_have_identical_results() -> None:
    spellings = (("1", "1."), ("001", "01.0"), ("1.00", "001.000"))
    expected = divide_cnrs_exact("1", "1").to_dict()
    for dividend, divisor in spellings:
        assert divide_cnrs_exact(dividend, divisor).to_dict() == expected


def test_legacy_outputs_preserved_with_call_time_deprecation() -> None:
    vectors = {
        ("0", "1"): "0",
        ("1", "1"): "1",
        ("1", "10"): "0",
        (".1", "1"): "0",
        (".1", ".1"): "1",
        ("23.1", "1."): "23",
        ("4", "2"): "2",
    }
    for operands, expected in vectors.items():
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert div_cnrs(*operands) == expected
        assert len(caught) == 1
        assert caught[0].category is DeprecationWarning
        assert "divide_cnrs_exact" in str(caught[0].message)


@pytest.mark.parametrize(
    "mutation",
    [
        "from cnrs.validation import exact_division_oracle\n",
        "from cnrs.cnrs_div import div_cnrs\n",
        "\ndef mutation(): return complex(0)\n",
        "\ndef mutation(): return float(0)\n",
        "\ndef mutation(): return round(0)\n",
        "\ndef mutation(): return 1 / 2\n",
        "\ndef mutation(z): return z.real\n",
        "\ndef mutation(z): return z.imag\n",
        "\ndef mutation():\n    for _ in (): pass\n",
        "\ndef mutation(x): return finite_sequence_to_cnrs_string(x)\n",
    ],
)
def test_production_guard_mutation_probes(mutation: str) -> None:
    source = (ROOT / "cnrs/exact_division.py").read_text(encoding="utf-8")
    with pytest.raises(ClaimGuardError):
        guard_production_source(mutation + source if mutation.startswith("from")
                                else source + mutation)


@pytest.mark.parametrize(
    "mutation",
    [
        "from cnrs.exact_division import divide_cnrs_exact\n",
        "from cnrs.finite_string import cnrs_string_to_finite_sequence\n",
        "from cnrs.streaming_division import stream_division\n",
        "from cnrs.canonical_periodic import CanonicalPeriodicExpansion\n",
        "from cnrs.witnesses import division_witness\n",
        "\ndef mutation(): return divide_cnrs_exact('1', '1')\n",
    ],
)
def test_oracle_guard_mutation_probes(mutation: str) -> None:
    source = (ROOT / "cnrs/validation/exact_division_oracle.py").read_text(
        encoding="utf-8"
    )
    with pytest.raises(ClaimGuardError):
        guard_oracle_source(mutation + source if mutation.startswith("from")
                            else source + mutation)
