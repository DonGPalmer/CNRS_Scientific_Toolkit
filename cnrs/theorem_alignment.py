"""
cnrs.theorem_alignment
======================

Small registry mapping toolkit functions to their theory/proof status.

This is not a theorem prover.  It is an implementation discipline tool: every
core feature should declare whether it is theorem-backed, computationally
verified, scaffold, bridge, validation, or open.  The registry complements
``cnrs.native_status`` by recording theorem/proof alignment rather than broad
architectural role.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class TheoremStatus(str, Enum):
    THEOREM_BACKED = "theorem_backed"
    COMPUTATIONALLY_VERIFIED = "computationally_verified"
    CONDITIONAL = "conditional"
    SCAFFOLD = "scaffold"
    BRIDGE = "bridge"
    VALIDATION = "validation"
    OPEN = "open"


@dataclass(frozen=True)
class TheoremRecord:
    name: str
    module: str
    status: TheoremStatus
    statement: str
    implementation_note: str = ""
    formal_system: str | None = None
    formal_source: str | None = None
    formal_status: str | None = None


THEOREM_REGISTRY: tuple[TheoremRecord, ...] = (
    TheoremRecord(
        "CNRS-A finite representation",
        "cnrs.cnrs_repr",
        TheoremStatus.THEOREM_BACKED,
        "Gaussian integers have finite canonical CNRS-A representations in base z0=-2+i.",
        "Implemented by greedy digit extraction and canonical formatting. Lean verifies selected base/primality and residue-digit foundations, not this entire executable routine.",
    ),
    TheoremRecord(
        "CNRS Q2 beta-adic completion",
        "cnrs.topology",
        TheoremStatus.THEOREM_BACKED,
        "For beta=-2+i, the natural beta-adic completion is represented concretely at ring level by Z_5 and at field level by Q_5, with beta mapped to norm 1/5.",
        "Python topology utilities provide finite theorem-aligned metric/isometry witnesses; the Toolkit does not claim a runtime Z_5/Q_5 object or Lean-extracted implementation.",
        formal_system="Lean 4 / Mathlib 4.33.0",
        formal_source="formal/lean/CnrsQ2",
        formal_status="Lean-verified mathematical theorem",
    ),
    TheoremRecord(
        "CNRS Q2 unique beta-adic digit expansion",
        "cnrs.topology",
        TheoremStatus.THEOREM_BACKED,
        "Every x in Z_5 has a unique Fin 5 digit sequence whose beta-power partial sums converge to x.",
        "This is a completion-level formal theorem. Current Python expansion utilities are independently implemented and do not constitute a refinement proof or a general runtime Z_5 infinite-stream implementation.",
        formal_system="Lean 4 / Mathlib 4.33.0",
        formal_source="formal/lean/CnrsQ2/CnrsQ2/DigitExpansion.lean",
        formal_status="Lean-verified mathematical theorem",
    ),
    TheoremRecord(
        "Scoped addition normalisation",
        "cnrs.normalization.normalize_addition",
        TheoremStatus.COMPUTATIONALLY_VERIFIED,
        "Bounded addition raw inputs use the addition transducer route.",
        "v0.8.1 explicitly separates this from general coefficient normalisation.",
    ),
    TheoremRecord(
        "General finite coefficient normalisation",
        "cnrs.normalization.normalize_general_coefficients",
        TheoremStatus.THEOREM_BACKED,
        "Arbitrary finite Gaussian-integer coefficient strings normalise to canonical CNRS-A values.",
        "Used for multiplication convolution outputs and other unbounded finite coefficient inputs.",
    ),
    TheoremRecord(
        "CNRS-A multiplication closure",
        "cnrs.cnrs_mul.mul_cnrs",
        TheoremStatus.THEOREM_BACKED,
        "Finite CNRS-A strings are closed under multiplication via convolution followed by general normalisation.",
        "Not claimed to be the same 14-state bounded-addition transducer.",
    ),
    TheoremRecord(
        "CNRS-A division classification",
        "cnrs.division",
        TheoremStatus.CONDITIONAL,
        "Gaussian rational division is classified as finite, base-power terminating, periodic, or shifted periodic.",
        "Sharp minimal carry-state/cardinality formulas remain open.",
    ),
    TheoremRecord(
        "CNRS-H differentiation/integration",
        "cnrs.cnrs_h_native.CnrsHNative",
        TheoremStatus.THEOREM_BACKED,
        "CNRS-H differentiation and integration are coefficient drop/prepend operations.",
        "Coefficients are CVal objects in the native layer.",
    ),
    TheoremRecord(
        "CNRS-H product rule",
        "cnrs.cnrs_h_native.verify_leibniz",
        TheoremStatus.COMPUTATIONALLY_VERIFIED,
        "EGF product uses binomial convolution and obeys the finite Leibniz check.",
        "Tests compare coefficient strings, not only decoded numeric values.",
    ),
    TheoremRecord(
        "CNRS-H finite-order chain rule",
        "cnrs.cnrs_h_native.verify_chain_rule_native",
        TheoremStatus.COMPUTATIONALLY_VERIFIED,
        "Finite-order Faà di Bruno composition supports chain-rule verification in CNRS-A coefficient space.",
        "Algorithmic-native coefficient calculus, not finite-state composition.",
    ),
    TheoremRecord(
        "CNRS* formal state preservation",
        "cnrs.formal_state.CnrsFormalState",
        TheoremStatus.CONDITIONAL,
        "Core CNRS* state operations preserve well-formed value/coefficient/metadata structure.",
        "Branch-composition semantics remain scope-qualified.",
    ),
    TheoremRecord(
        "Symbolic expression bridge",
        "cnrs.symbolic",
        TheoremStatus.BRIDGE,
        "Human-readable symbolic expressions can build/check CNRS-H objects for a supported subset.",
        "Not the native representation itself.",
    ),
    TheoremRecord(
        "CNRS rational value status",
        "cnrs.rational_value.CnrsRationalValue",
        TheoremStatus.CONDITIONAL,
        "Finite and periodic division outputs preserve their CNRS-A representation status instead of claiming finite-string field closure.",
        "Value-facing wrapper around structured division expansions; sharp carry counts remain open.",
    ),
    TheoremRecord(
        "Complex-state preservation workflow",
        "cnrs.science.workflow",
        TheoremStatus.SCAFFOLD,
        "Workflow diagnostics keep complex state until explicit observation maps are selected.",
        "Application-level diagnostic harness, not a new physical theorem.",
    ),
)


def all_theorem_records() -> tuple[TheoremRecord, ...]:
    return THEOREM_REGISTRY


def by_status(status: TheoremStatus | str) -> tuple[TheoremRecord, ...]:
    s = status if isinstance(status, TheoremStatus) else TheoremStatus(str(status))
    return tuple(record for record in THEOREM_REGISTRY if record.status == s)


def get_theorem_record(name_or_module: str) -> TheoremRecord:
    key = name_or_module.lower()
    exact = [r for r in THEOREM_REGISTRY if r.name.lower() == key or r.module.lower() == key]
    if exact:
        return exact[0]
    hits = [r for r in THEOREM_REGISTRY if key in r.name.lower() or key in r.module.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise KeyError(f"No theorem-alignment record matches {name_or_module!r}")
    raise KeyError(f"Ambiguous theorem-alignment query {name_or_module!r}: {', '.join(r.name for r in hits)}")


def theorem_alignment_table(records: Iterable[TheoremRecord] | None = None) -> str:
    rows = list(records if records is not None else THEOREM_REGISTRY)
    lines = [
        "| Result | Module | Status | Formal verification | Statement |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        statement = item.statement.replace("|", "\\|")
        formal = (item.formal_status or "").replace("|", "\\|")
        lines.append(f"| {item.name} | `{item.module}` | {item.status.value} | {formal} | {statement} |")
    return "\n".join(lines)


__all__ = [
    "TheoremStatus",
    "TheoremRecord",
    "THEOREM_REGISTRY",
    "all_theorem_records",
    "by_status",
    "get_theorem_record",
    "theorem_alignment_table",
]
