"""
cnrs.native_status
==================

Native-status registry for the CNRS Scientific Toolkit.

The registry separates CNRS-native structures from bridge, validation,
scaffold, and application layers.  It is intentionally lightweight: it is a
package-internal claim/status map, not a theorem prover.  Its purpose is to
keep the code architecture aligned with the CNRS theoretical programme.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class NativeStatus(str, Enum):
    """Classification of a toolkit component relative to CNRS-native structure."""

    NATIVE_CORE = "native_core"
    NATIVE_FINITE = "native_finite"
    NATIVE_LOCAL = "native_local"
    BRIDGE = "bridge"
    VALIDATION = "validation"
    SCAFFOLD = "scaffold"
    APPLICATION = "application"
    COMPATIBILITY = "compatibility"


@dataclass(frozen=True)
class ComponentStatus:
    """Status record for a public CNRS component."""

    name: str
    module: str
    status: NativeStatus
    layer: str
    claim: str
    notes: str = ""

    @property
    def is_native(self) -> bool:
        return self.status in {
            NativeStatus.NATIVE_CORE,
            NativeStatus.NATIVE_FINITE,
            NativeStatus.NATIVE_LOCAL,
        }


_COMPONENTS: tuple[ComponentStatus, ...] = (
    ComponentStatus(
        "CNRS base and digit alphabet",
        "cnrs.core.base",
        NativeStatus.NATIVE_CORE,
        "CNRS-A",
        "Defines z0=-2+i and the digit alphabet {0,1,2,3,4}.",
        "Native representational foundation.",
    ),
    ComponentStatus(
        "CNRS-A digit conversion and normalization",
        "cnrs.core.digits",
        NativeStatus.NATIVE_CORE,
        "CNRS-A",
        "Finite CNRS-A digit strings are evaluated and normalized through the core representation.",
        "Formal support: canonical normalization theorem for finite strings/Gaussian-integer layer.",
    ),
    ComponentStatus(
        "CNRS-A value wrapper",
        "cnrs.core.value",
        NativeStatus.NATIVE_CORE,
        "CNRS-A",
        "Wraps canonical CNRS-A values while preserving the digit-string representation.",
    ),
    ComponentStatus(
        "CNRS-A arithmetic",
        "cnrs.core.arithmetic",
        NativeStatus.NATIVE_CORE,
        "CNRS-A",
        "Addition, subtraction, multiplication, negation, equality, and available division helpers over CNRS-A forms.",
        "Division remains scope-qualified: finite for base powers/units; broader division is periodic/approximate unless separately proved.",
    ),
    ComponentStatus(
        "Layer-2 branch state",
        "cnrs.core.branch",
        NativeStatus.NATIVE_CORE,
        "Branch/Layer 2",
        "Explicit branch-state object used to retain log/sqrt/power branch information.",
        "Native representational metadata; not full analytic continuation by itself.",
    ),
    ComponentStatus(
        "CNRS-H series",
        "cnrs.h.series",
        NativeStatus.NATIVE_CORE,
        "CNRS-H",
        "EGF coefficient representation with z0^n/n! place values.",
    ),
    ComponentStatus(
        "CNRS-H calculus",
        "cnrs.h.calculus",
        NativeStatus.NATIVE_CORE,
        "CNRS-H",
        "Differentiation and integration are coefficient-shift operations.",
    ),
    ComponentStatus(
        "CNRS-H composition",
        "cnrs.h.compose",
        NativeStatus.NATIVE_FINITE,
        "CNRS-H",
        "Finite-order EGF composition inside CNRS-H coefficient space.",
        "Native finite-order operation, not a CNRS-A finite-state composition transducer.",
    ),
    ComponentStatus(
        "CNRS-H chain rule",
        "cnrs.h.chain_rule",
        NativeStatus.NATIVE_FINITE,
        "CNRS-H",
        "Finite-order structural chain-rule verification by CNRS-H coefficient composition and shift.",
        "Formal theorem note still recommended for the truncated identity.",
    ),
    ComponentStatus(
        "CNRS-H local jets",
        "cnrs.h.jet",
        NativeStatus.NATIVE_LOCAL,
        "CNRS-H local analytic",
        "Finite local CNRS-H analytic object with expansion center, branch state, path history, and domain metadata.",
        "Local/truncated, not a global analytic object.",
    ),
    ComponentStatus(
        "CNRS-H domain diagnostics",
        "cnrs.h.domain",
        NativeStatus.SCAFFOLD,
        "Diagnostics",
        "Conservative local-radius and singularity hints for CNRS-H jets.",
        "Diagnostic metadata, not a rigorous convergence proof.",
    ),
    ComponentStatus(
        "CNRS-H Taylor-model metadata",
        "cnrs.h.taylor_model",
        NativeStatus.SCAFFOLD,
        "Certification scaffold",
        "Wraps finite CNRS-H jets with optional remainder metadata.",
        "Not yet full interval/disk arithmetic.",
    ),
    ComponentStatus(
        "CNRS-H path and winding",
        "cnrs.h.path",
        NativeStatus.NATIVE_LOCAL,
        "Branch/continuation scaffold",
        "Path/winding bookkeeping updates branch state for local CNRS-H objects.",
        "Piecewise-linear local scaffold, not full Riemann-surface lifting.",
    ),
    ComponentStatus(
        "CNRS-H branch continuation rebuild",
        "cnrs.h.continuation",
        NativeStatus.SCAFFOLD,
        "Branch/continuation scaffold",
        "Uses symbolic source expressions to rebuild local jets after supported branch events.",
        "Coefficient-active but still source-expression-dependent.",
    ),

    ComponentStatus(
        "CNRS-A native CVal",
        "cnrs.cnrs_value",
        NativeStatus.NATIVE_CORE,
        "CNRS-A",
        "Canonical CNRS-A value wrapper with native addition, negation, subtraction, and multiplication.",
        "Negation uses the finite CNRS-A representation -1 = 144; multiplication uses convolution followed by general CNRS-A normalisation.",
    ),
    ComponentStatus(
        "CNRS-A division classification",
        "cnrs.division",
        NativeStatus.NATIVE_FINITE,
        "CNRS-A division",
        "Classifies Gaussian rational division into terminating, base-power, periodic, and shifted-periodic cases.",
        "This is not finite-string field closure; persistent denominators are represented by periodic structures.",
    ),
    ComponentStatus(
        "CNRS-H native coefficients",
        "cnrs.cnrs_h_native",
        NativeStatus.NATIVE_CORE,
        "CNRS-H",
        "Stores CNRS-H coefficients as CNRS-A CVal objects and performs coefficient arithmetic through CNRS-A operations.",
        "Evaluation at ordinary points remains a bridge to Python complex arithmetic.",
    ),
    ComponentStatus(
        "CNRS-H native composition and chain rule",
        "cnrs.cnrs_h_native.compose_native",
        NativeStatus.NATIVE_FINITE,
        "CNRS-H",
        "Finite-order Faà di Bruno/Bell-polynomial composition and chain-rule verification in CNRS-A coefficient space.",
        "Algorithmic-native coefficient calculus, not a finite-state CNRS-A transducer.",
    ),
    ComponentStatus(
        "CNRS* formal state",
        "cnrs.formal_state",
        NativeStatus.NATIVE_LOCAL,
        "CNRS*",
        "Theory-aligned state tuple carrying value, branch state, native coefficient jet, centre, order, and domain metadata.",
    ),

    ComponentStatus(
        "CNRS-A scoped normalisation",
        "cnrs.normalization",
        NativeStatus.NATIVE_CORE,
        "CNRS-A",
        "Separates bounded addition-transducer normalisation from general finite coefficient normalisation.",
        "Prevents treating multiplication convolution coefficients as bounded addition input.",
    ),
    ComponentStatus(
        "CNRS theorem-alignment registry",
        "cnrs.theorem_alignment",
        NativeStatus.VALIDATION,
        "Theory alignment",
        "Maps implementation features to theorem-backed, conditional, bridge, validation, scaffold, or open status.",
        "Governance/status layer rather than mathematical operation.",
    ),
    ComponentStatus(
        "Symbolic expressions",
        "cnrs.symbolic",
        NativeStatus.BRIDGE,
        "Bridge",
        "Human-readable expression layer used to build or inspect CNRS-H objects.",
    ),
    ComponentStatus(
        "Symbolic-to-CNRS-H bridge",
        "cnrs.cnrs_h_bridge",
        NativeStatus.BRIDGE,
        "Bridge",
        "Converts supported symbolic expressions into CNRS-H coefficient representations.",
    ),
    ComponentStatus(
        "Autodiff reference",
        "cnrs.validation.autodiff",
        NativeStatus.VALIDATION,
        "Validation",
        "Standard dual-number autodiff retained as a reference/comparison method.",
        "Not the CNRS-native chain rule.",
    ),
    ComponentStatus(
        "Reference complex comparisons",
        "cnrs.validation.reference_complex",
        NativeStatus.VALIDATION,
        "Validation",
        "Interoperability and comparison against Python complex arithmetic.",
    ),
    ComponentStatus(
        "CNRS scientific state",
        "cnrs.science.state",
        NativeStatus.NATIVE_LOCAL,
        "Scientific state",
        "Science-facing object that keeps the CNRS-H jet as primary representation and carries metadata around it.",
        "Finite local scientific representation; not physical truth claim.",
    ),
    ComponentStatus(
        "Observation maps",
        "cnrs.science.observation",
        NativeStatus.APPLICATION,
        "Application",
        "Explicit maps from preserved complex CNRS state to real-valued observations.",
        "Observation is deliberately late and explicit.",
    ),
    ComponentStatus(
        "Scientific workflows",
        "cnrs.workflows",
        NativeStatus.APPLICATION,
        "Application",
        "Scale-law, oscillator, and reaction-diffusion workflows built around CNRS objects.",
    ),
    ComponentStatus(
        "Flat legacy modules",
        "cnrs.cnrs_*",
        NativeStatus.COMPATIBILITY,
        "Compatibility",
        "Historical flat import paths preserved for users and tests.",
        "Preferred conceptual imports now live under cnrs.core, cnrs.h, cnrs.validation, cnrs.science, and cnrs.workflows.",
    ),
)


STATUS_REGISTRY: tuple[ComponentStatus, ...] = _COMPONENTS


def all_statuses() -> tuple[ComponentStatus, ...]:
    """Return all registered component-status records."""

    return STATUS_REGISTRY


def native_components() -> tuple[ComponentStatus, ...]:
    """Return components classified as CNRS-native."""

    return tuple(item for item in STATUS_REGISTRY if item.is_native)


def by_status(status: NativeStatus | str) -> tuple[ComponentStatus, ...]:
    """Return component records matching a native-status category."""

    s = status if isinstance(status, NativeStatus) else NativeStatus(str(status))
    return tuple(item for item in STATUS_REGISTRY if item.status == s)


def by_layer(layer: str) -> tuple[ComponentStatus, ...]:
    """Return component records whose layer label contains ``layer``."""

    key = layer.lower()
    return tuple(item for item in STATUS_REGISTRY if key in item.layer.lower())


def get_component(name_or_module: str) -> ComponentStatus:
    """Find a component by exact name/module or unique substring."""

    key = name_or_module.lower()
    exact = [item for item in STATUS_REGISTRY if item.name.lower() == key or item.module.lower() == key]
    if exact:
        return exact[0]
    hits = [item for item in STATUS_REGISTRY if key in item.name.lower() or key in item.module.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise KeyError(f"No CNRS native-status component matches {name_or_module!r}")
    names = ", ".join(item.name for item in hits)
    raise KeyError(f"Ambiguous CNRS native-status query {name_or_module!r}: {names}")


def status_table(records: Iterable[ComponentStatus] | None = None) -> str:
    """Render component status records as a markdown table."""

    rows = list(records if records is not None else STATUS_REGISTRY)
    lines = [
        "| Component | Module | Status | Layer | Claim |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        claim = item.claim.replace("|", "\\|")
        lines.append(f"| {item.name} | `{item.module}` | {item.status.value} | {item.layer} | {claim} |")
    return "\n".join(lines)


__all__ = [
    "NativeStatus",
    "ComponentStatus",
    "STATUS_REGISTRY",
    "all_statuses",
    "native_components",
    "by_status",
    "by_layer",
    "get_component",
    "status_table",
]
