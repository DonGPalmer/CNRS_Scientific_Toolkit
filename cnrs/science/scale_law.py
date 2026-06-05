"""
CNRS-H scale-law utilities.

This module wraps CnrsH for common scientific scale-law workflows:
exponential laws, complex exponent laws, least-squares EGF fitting, and
coefficient-shift derivatives.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence
import numpy as np

from cnrs.cnrs_h import CnrsH


def exp_coeffs(lam: complex, terms: int, scale: complex = 1) -> list[complex]:
    """EGF coefficients for scale * exp(lam*rho)."""
    return [scale * (lam ** n) for n in range(terms)]


def exp_scale_law(lam: complex, scale: complex = 1, terms: int = 32) -> CnrsH:
    return CnrsH.from_list(exp_coeffs(lam, terms=terms, scale=scale))


@dataclass
class CnrsScaleLaw:
    """A CNRS-H backed scale law f(rho)."""
    h: CnrsH
    name: str = "scale_law"

    def __call__(self, rho):
        if np.ndim(rho) == 0:
            return self.h.evaluate(complex(rho))
        return np.array([self.h.evaluate(complex(x)) for x in rho], dtype=complex)

    def derivative(self) -> "CnrsScaleLaw":
        return CnrsScaleLaw(self.h.differentiate(), name=f"D({self.name})")

    def integral(self, constant=0) -> "CnrsScaleLaw":
        return CnrsScaleLaw(self.h.integrate(constant), name=f"I({self.name})")

    def log_derivative(self, rho):
        vals = self(rho)
        dvals = self.derivative()(rho)
        return dvals / vals

    @staticmethod
    def exponential(lam: complex, scale: complex = 1, terms: int = 32, name: str | None = None) -> "CnrsScaleLaw":
        return CnrsScaleLaw(exp_scale_law(lam, scale=scale, terms=terms), name=name or f"{scale}*exp(({lam})rho)")


def fit_egf_scale_law(rho: Sequence[float], y: Sequence[complex], degree: int, name: str = "fit") -> CnrsScaleLaw:
    """
    Least-squares fit y(rho) ≈ Σ a_n rho^n/n!.

    Returns a CnrsScaleLaw backed by a CnrsH coefficient stream.
    """
    rho_arr = np.asarray(rho, dtype=float)
    y_arr = np.asarray(y, dtype=complex)
    A = np.vstack([(rho_arr ** n) / math.factorial(n) for n in range(degree + 1)]).T
    coeffs, *_ = np.linalg.lstsq(A, y_arr, rcond=None)
    return CnrsScaleLaw(CnrsH.from_list(coeffs.tolist()), name=name)
