"""
Three-workflow comparison harness.

Workflow A: reduce to real observable early.
Workflow B: preserve ordinary complex state and observe late.
Workflow C: preserve CNRS complex-state representation and observe late.
"""
from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
import numpy as np

from cnrs.cnrs_float import encode, decode
from cnrs.science.scale_law import CnrsScaleLaw
from cnrs.science.branch import branch_indices_from_unwrapped, winding_number


@dataclass
class ThreeWorkflowResult:
    name: str
    metrics: dict
    interpretation: str


def _q(z: complex, L: int = 14) -> complex:
    return decode(encode(complex(z), L=L))


def _rel_l2(a, b) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    den = np.linalg.norm(a)
    return float(np.linalg.norm(a - b) / (den if den else 1.0))


def compare_interference(n: int = 1000, L: int = 14) -> ThreeWorkflowResult:
    theta = np.linspace(0, 2 * np.pi, n)
    psi1 = np.ones_like(theta, dtype=complex)
    psi2 = np.exp(1j * theta)
    psi = psi1 + psi2

    A = np.abs(psi1) ** 2 + np.abs(psi2) ** 2
    B = np.abs(psi) ** 2
    C_state = np.array([_q(z, L=L) for z in psi])
    C = np.abs(C_state) ** 2
    cross = B - A

    return ThreeWorkflowResult(
        "interference",
        {
            "A_phase_variation": float(np.max(A) - np.min(A)),
            "B_intensity_min": float(np.min(B)),
            "B_intensity_max": float(np.max(B)),
            "lost_cross_term_min": float(np.min(cross)),
            "lost_cross_term_max": float(np.max(cross)),
            "C_intensity_rel_L2_error": _rel_l2(C, B),
            "C_amplitude_rel_L2_error": _rel_l2(C_state, psi),
        },
        "Early real reduction loses the interference cross term; CNRS preserves the unsquared amplitude until observation.",
    )


def compare_complex_scale_law(alpha: float = -0.14, omega: float = 4.25, omega2: float = 1.75,
                              terms: int = 48, L: int = 14) -> ThreeWorkflowResult:
    s = np.linspace(-3, 3, 800)
    A0 = 1.15 * np.exp(0.4j)
    lam = alpha + 1j * omega
    psi = A0 * np.exp(lam * s)
    psi2 = A0 * np.exp((alpha + 1j * omega2) * s)

    A = np.abs(psi) ** 2
    A2 = np.abs(psi2) ** 2
    B_phase = np.unwrap(np.angle(psi))
    law = CnrsScaleLaw.exponential(lam, scale=A0, terms=terms)
    C_h = law(s)
    C_float = np.array([_q(z, L=L) for z in psi])

    return ThreeWorkflowResult(
        "complex_scale_law",
        {
            "A_mod2_difference_when_omega_changed": float(np.max(np.abs(A - A2))),
            "B_phase_derivative_mean": float(np.mean(np.gradient(B_phase, s)[80:-80])),
            "B_real_relative_difference_when_omega_changed": _rel_l2(np.real(psi), np.real(psi2)),
            "C_CNRS_H_state_rel_L2_error": _rel_l2(C_h, psi),
            "C_CNRS_float_state_rel_L2_error": _rel_l2(C_float, psi),
        },
        "Modulus-squared loses scale-frequency omega; CNRS-H preserves and differentiates the complex scale law.",
    )


def compare_branch_winding(n: int = 1200, L: int = 14) -> ThreeWorkflowResult:
    t = np.linspace(0, 12, n)
    phi = 0.9 * t + 0.18 * t ** 2 + 0.6 * np.sin(3 * t)
    z = np.exp(1j * phi)

    A = np.abs(z) ** 2
    wrapped = np.angle(z)
    unwrapped = np.unwrap(wrapped)
    branches = branch_indices_from_unwrapped(wrapped, unwrapped)

    zc = np.array([_q(v, L=L) for v in z])
    uc = np.unwrap(np.angle(zc))
    off = np.median(uc - unwrapped)

    return ThreeWorkflowResult(
        "branch_winding",
        {
            "A_modulus_squared_variation": float(np.max(A) - np.min(A)),
            "B_winding_number": winding_number(unwrapped),
            "B_branch_min": int(min(branches)),
            "B_branch_max": int(max(branches)),
            "C_phase_max_abs_error": float(np.max(np.abs((uc - off) - unwrapped))),
            "C_phasor_rel_L2_error": _rel_l2(zc, z),
        },
        "Modulus-squared loses branch/winding history; CNRS-float preserves the phasor sufficiently to recover phase path.",
    )
